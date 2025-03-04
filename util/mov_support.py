from moviepy import VideoFileClip

def extract_audio_from_video(video_path, output_audio_path) -> bool:
    """
    从视频文件中提取音频，并保存为 WAV 文件
    :param video_path: 视频文件路径
    :param output_audio_path: 输出音频文件路径
    :return: 是否提取成功
    """
    # 加载视频文件
    video = VideoFileClip(video_path)
    
    # 提取音频
    audio = video.audio
    
    # 保存为 WAV 文件
    audio.write_audiofile(output_audio_path, codec='pcm_s16le')
    
    # 关闭视频文件
    video.close()

    return True