from flask import Flask, request, jsonify
import os
import uuid
import threading
from werkzeug.utils import secure_filename
import time
import json
from functools import wraps
from flask_cors import CORS
import secrets
from threading import Lock

# 导入FunASR相关库
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

app = Flask(__name__)
CORS(app)

# 配置参数
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 最大500MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# API密钥存储
API_KEYS_FILE = 'api_keys.json'
api_keys_lock = Lock()

def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_api_keys(api_keys):
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(api_keys, f, indent=2)

api_keys = load_api_keys()

# 如果首次运行生成默认管理员密钥
if not api_keys:
    default_admin_key = secrets.token_urlsafe(32)
    with api_keys_lock:
        api_keys[default_admin_key] = {
            'created_at': time.time(),
            'is_admin': True,
            'is_active': True,
            'usage': {
                'total_requests': 0,
                'last_used': None,
                'total_processing_time': 0
            }
        }
        save_api_keys(api_keys)
    print(f"初始管理员API密钥已生成：{default_admin_key}")
    print("请立即保存此密钥，应用重启后将不再显示！")

# 存储任务状态的字典
tasks = {}
tasks_lock = Lock()

# 初始化模型
print("Loading SenseVoice model...")
model = AutoModel(
    model="iic/SenseVoiceSmall",
    trust_remote_code=True,
    remote_code="./model.py",    
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    device="cuda:7",
)
print("Model loaded successfully!")

# 身份验证装饰器
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': '缺少API密钥'}), 401

        with api_keys_lock:
            key_info = api_keys.get(api_key)
            if not key_info or not key_info.get('is_active', True):
                return jsonify({'error': '无效或已禁用的API密钥'}), 401

            # 更新使用统计
            key_info['usage']['total_requests'] += 1
            key_info['usage']['last_used'] = time.time()
            save_api_keys(api_keys)

        request.key_info = key_info
        return f(*args, **kwargs)
    return decorated

def require_admin_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': '缺少API密钥'}), 401

        with api_keys_lock:
            key_info = api_keys.get(api_key)
            if not key_info or not key_info.get('is_active', True):
                return jsonify({'error': '无效或已禁用的API密钥'}), 401

            if not key_info.get('is_admin', False):
                return jsonify({'error': '需要管理员权限'}), 403

            # 更新使用统计
            key_info['usage']['total_requests'] += 1
            key_info['usage']['last_used'] = time.time()
            save_api_keys(api_keys)

        request.key_info = key_info
        return f(*args, **kwargs)
    return decorated

def process_audio(file_path, task_id, language, api_key):
    """后台处理音频文件的函数"""
    start_time = time.time()
    try:
        with tasks_lock:
            tasks[task_id]['status'] = 'processing'

        # 使用模型进行识别
        res = model.generate(
            input=file_path,
            cache={},
            language=language,
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,
            merge_length_s=15,
        )
        
        # 处理结果
        text = rich_transcription_postprocess(res[0]["text"])
        processing_time = time.time() - start_time

        with tasks_lock:
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['result'] = text
            tasks[task_id]['completed_at'] = time.time()

        # 更新处理时间
        with api_keys_lock:
            if api_key in api_keys:
                api_keys[api_key]['usage']['total_processing_time'] += processing_time
                save_api_keys(api_keys)

        # 删除临时文件
        if tasks[task_id].get('delete_after_processing', True):
            try:
                os.remove(file_path)
            except:
                pass

    except Exception as e:
        processing_time = time.time() - start_time
        with tasks_lock:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['error'] = str(e)

        # 更新处理时间（即使失败）
        with api_keys_lock:
            if api_key in api_keys:
                api_keys[api_key]['usage']['total_processing_time'] += processing_time
                save_api_keys(api_keys)

        # 尝试删除临时文件
        if tasks[task_id].get('delete_after_processing', True):
            try:
                os.remove(file_path)
            except:
                pass

@app.route('/recognize', methods=['POST'])
@require_auth
def recognize_speech():
    """接收音频文件并开始处理的端点"""
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '空文件名'}), 400
    
    language = request.form.get('language', 'auto')
    is_final = request.form.get('is_final', 'false').lower() == 'true'
    api_key = request.headers.get('X-API-Key')

    task_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
    file.save(file_path)

    with tasks_lock:
        tasks[task_id] = {
            'status': 'queued',
            'created_at': time.time(),
            'file_path': file_path,
            'is_final': is_final,
            'delete_after_processing': not is_final,
            'api_key': api_key
        }

    # 启动处理线程
    thread = threading.Thread(target=process_audio, args=(file_path, task_id, language, api_key))
    thread.daemon = True
    thread.start()

    return jsonify({
        'task_id': task_id,
        'status': 'queued',
        'message': '文件已上传，正在处理中...'
    })

@app.route('/status/<task_id>', methods=['GET'])
@require_auth
def check_status(task_id):
    """检查任务状态"""
    with tasks_lock:
        task = tasks.get(task_id)
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    response = {
        'task_id': task_id,
        'status': task['status'],
        'created_at': task['created_at'],
        'is_final': task.get('is_final', False)
    }
    
    if task['status'] == 'completed':
        response['result'] = task['result']
        response['completed_at'] = task.get('completed_at')
    
    if task['status'] == 'failed':
        response['error'] = task.get('error', '未知错误')
    
    return jsonify(response)

@app.route('/admin/create_key', methods=['POST'])
@require_admin_auth
def create_api_key():
    """创建新API密钥"""
    data = request.json
    is_admin = data.get('is_admin', False)
    
    new_key = secrets.token_urlsafe(32)
    with api_keys_lock:
        while new_key in api_keys:
            new_key = secrets.token_urlsafe(32)
        
        api_keys[new_key] = {
            'created_at': time.time(),
            'is_admin': is_admin,
            'is_active': True,
            'usage': {
                'total_requests': 0,
                'last_used': None,
                'total_processing_time': 0
            }
        }
        save_api_keys(api_keys)
    
    return jsonify({
        'api_key': new_key,
        'is_admin': is_admin,
        'created_at': api_keys[new_key]['created_at']
    })

@app.route('/admin/keys', methods=['GET'])
@require_admin_auth
def list_api_keys():
    """列出所有API密钥（脱敏）"""
    keys_info = []
    with api_keys_lock:
        for key, info in api_keys.items():
            keys_info.append({
                'prefix': f"{key[:5]}...{key[-5:]}",
                'created_at': info['created_at'],
                'is_admin': info['is_admin'],
                'is_active': info['is_active'],
                'usage': info['usage']
            })
    return jsonify({'keys': keys_info})

@app.route('/admin/toggle_key', methods=['POST'])
@require_admin_auth
def toggle_api_key():
    """启用/禁用API密钥"""
    data = request.json
    target_key = data.get('api_key')
    new_status = data.get('active', True)

    with api_keys_lock:
        if target_key not in api_keys:
            return jsonify({'error': '密钥不存在'}), 404
        
        api_keys[target_key]['is_active'] = new_status
        save_api_keys(api_keys)
    
    return jsonify({'message': f'密钥状态已更新为{"启用" if new_status else "禁用"}'})

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'model': 'SenseVoiceSmall',
        'timestamp': time.time()
    })

def cleanup_tasks():
    """定期清理旧任务"""
    while True:
        current_time = time.time()
        to_delete = []
        
        with tasks_lock:
            for task_id, task in tasks.items():
                # 普通任务保留30分钟，最终转写任务保留24小时
                retention = 1800 if not task.get('is_final') else 86400
                if (current_time - task['created_at'] > retention) and \
                   (task['status'] in ['completed', 'failed']):
                    to_delete.append(task_id)
            
            for task_id in to_delete:
                del tasks[task_id]
        
        time.sleep(600)

if __name__ == '__main__':
    cleanup_thread = threading.Thread(target=cleanup_tasks)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    app.run(host='0.0.0.0', port=14612, debug=False, threaded=True)