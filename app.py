import sys
import os
import time
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QWidget, QPushButton, QTextEdit, QLabel, QFileDialog,
                               QComboBox, QGroupBox, QProgressBar, QMessageBox, QCheckBox, QLineEdit)
from PySide6.QtCore import QTimer, Slot, Qt, QSettings
from PySide6.QtGui import QIcon, QTextCursor

# Import the core module you defined earlier
from audio_transcription import TranscriptionManager
from summarize import SummarizationWorker
from Instructions import *

from PySide6.QtCore import QThread, Signal

class AudioExtractionWorker(QThread):
    extraction_finished = Signal(bool, str)  # 成功与否和消息

    def __init__(self, transcription_manager, movie_path, status_bar, audio_ouput_path="tmp/extraction.wav"):
        super().__init__()
        self.transcription_manager = transcription_manager
        self.movie_path = movie_path
        self.audio_output_path = audio_ouput_path
        self.status_bar = status_bar

    def run(self):
        self.status_bar.showMessage("Extracting audio from video...")
        success = self.transcription_manager.extract_audio_from_video(self.movie_path, self.audio_output_path)
        if success:
            self.status_bar.showMessage("Audio extraction completed")
        else:
            self.status_bar.showMessage("Audio extraction failed")
        self.extraction_finished.emit(success, self.audio_output_path)

class AudioTranscriptionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Lecture Transcription Assistant"))
        self.resize(660, 700)

        # Load settings
        self.settings = QSettings("YourOrganization", "LectureTranscriber")
        self.speech_api_key = self.settings.value("speech_api_key", "")
        self.speech_api_url = self.settings.value("speech_api_url", "http://localhost:14612")
        self.llm_api_key = self.settings.value("llm_api_key", "")
        self.output_dir = self.settings.value("output_dir", str(Path.home() / "transcriptions"))

        # Initialize core component
        self.transcription_manager = None
        self.init_transcription_manager()

        # Initialize UI components
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Setup UI
        self.setup_ui()

        # Initialize timer for recording chunks
        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self.record_audio_chunk)

        # Initialize timer for status checking
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.check_transcription_status)

        # Recording state
        self.recording = False
        self.current_audio_file: Optional[str] = None
        self.transcription_in_progress = False
        self.elapsed_time = 0
        self.recording_timer = QTimer(self)
        self.recording_timer.timeout.connect(self.update_recording_time)

        self.summarization_worker = None  # 初始化 summarization_worker

        # 创建QSettings，配置文件是tmp/.temp
        self.setting = QSettings('tmp/.temp', QSettings.IniFormat) 
		
		# 设置UTF8编码，防止保存配置文件时出现乱码
        # self.setting.setIniCodec('UTF-8') 
		
		# 读取上一次的目录路径
        self.last_path = self.setting.value('LastFilePath')
		
	 	# 如果字符串为空，将路径索引到根目录
        if self.last_path is None:
            self.last_path = "" # 根盘符

    def init_transcription_manager(self):
        """Initialize or reinitialize the transcription manager with current settings."""
        if all([self.speech_api_key, self.speech_api_url, self.llm_api_key]):
            self.transcription_manager = TranscriptionManager(
                speech_api_key=self.speech_api_key,
                speech_api_url=self.speech_api_url,
                llm_api_key=self.llm_api_key,
                output_dir=self.output_dir
            )
        else:
            self.transcription_manager = None

    def setup_ui(self):
        """Set up the user interface components."""
        # API Configuration Group
        self.setup_api_config_group()

        # Recording Controls Group
        self.setup_recording_controls()

        # Language Selection
        self.setup_language_selection()

        # Transcription and Summary Group
        self.setup_transcription_display()

        # File Operations Group
        self.setup_file_operations()

        # Status Bar
        self.statusBar().showMessage("Ready")

    def setup_api_config_group(self):
        """Set up the API configuration UI group."""
        api_group = QGroupBox("API Configuration")
        api_layout = QVBoxLayout()

        # Speech API Key input
        speech_key_layout = QHBoxLayout()
        speech_key_layout.addWidget(QLabel("Speech API Key:"))
        self.speech_api_key_input = QLineEdit()
        self.speech_api_key_input.setFixedHeight(30)
        # self.speech_api_key_input.setPlainText(self.speech_api_key)
        self.speech_api_key_input.setText(self.speech_api_key)
        self.speech_api_key_input.setToolTip("Enter your SenseVoice API key")
        self.speech_api_key_input.setToolTipDuration(5000)
        self.speech_api_key_input.setEchoMode(QLineEdit.Password)
        speech_key_layout.addWidget(self.speech_api_key_input)
        api_layout.addLayout(speech_key_layout)

        # Speech API URL input
        speech_url_layout = QHBoxLayout()
        speech_url_layout.addWidget(QLabel("Speech API URL:"))
        self.speech_api_url_input = QTextEdit()
        self.speech_api_url_input.setFixedHeight(30)
        self.speech_api_url_input.setPlainText(self.speech_api_url)
        self.speech_api_url_input.setToolTip("Enter the URL of the SenseVoice API server")
        speech_url_layout.addWidget(self.speech_api_url_input)
        api_layout.addLayout(speech_url_layout)

        # LLM API Key input
        llm_key_layout = QHBoxLayout()
        llm_key_layout.addWidget(QLabel("LLM API Key:"))
        self.llm_api_key_input = QLineEdit()
        self.llm_api_key_input.setFixedHeight(30)
        # self.llm_api_key_input.setPlainText(self.llm_api_key)
        self.llm_api_key_input.setText(self.llm_api_key)
        self.llm_api_key_input.setToolTip("Enter your DeepSeek API key")
        self.llm_api_key_input.setToolTipDuration(5000)
        self.llm_api_key_input.setEchoMode(QLineEdit.Password)

        llm_key_layout.addWidget(self.llm_api_key_input)
        api_layout.addLayout(llm_key_layout)

        # Output directory input
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(QLabel("Output Directory:"))
        self.output_dir_input = QTextEdit()
        self.output_dir_input.setFixedHeight(30)
        self.output_dir_input.setPlainText(self.output_dir)
        output_dir_layout.addWidget(self.output_dir_input)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(browse_button)
        api_layout.addLayout(output_dir_layout)

        # Save button
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_api_config)
        api_layout.addWidget(save_button)

        api_group.setLayout(api_layout)
        self.main_layout.addWidget(api_group)

    def setup_recording_controls(self):
        """Set up the recording controls UI group."""
        recording_group = QGroupBox("Recording Controls")
        recording_layout = QVBoxLayout()

        buttons_layout = QHBoxLayout()

        # Start recording button
        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.toggle_recording)
        buttons_layout.addWidget(self.record_button)

        # Open file button
        open_file_button = QPushButton("Open Audio File")
        open_file_button.clicked.connect(self.open_audio_file)
        buttons_layout.addWidget(open_file_button)

        recording_layout.addLayout(buttons_layout)

        # Recording time display
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        recording_layout.addWidget(self.time_label)

        # Recording progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        recording_layout.addWidget(self.progress_bar)

        recording_group.setLayout(recording_layout)
        self.main_layout.addWidget(recording_group)

    def setup_language_selection(self):
        """Set up the language selection dropdown."""
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("Language:"))

        self.language_combo = QComboBox()
        self.language_combo.addItem("Auto-detect", "auto")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Chinese", "zh")
        # Add more languages as needed

        language_layout.addWidget(self.language_combo)
        self.main_layout.addLayout(language_layout)

    def setup_transcription_display(self):
        """Set up the transcription and summary display area."""
        # Create group box
        transcription_group = QGroupBox("Transcription & Summary")
        transcription_layout = QVBoxLayout()

        # Transcription area
        transcription_layout.addWidget(QLabel("Transcription:"))
        self.transcription_text = QTextEdit()
        self.transcription_text.setReadOnly(True)
        transcription_layout.addWidget(self.transcription_text)

        # Summary options
        summary_options_layout = QHBoxLayout()
        self.summarize_checkbox = QCheckBox("Summarize transcript")
        self.summarize_checkbox.setChecked(True)
        summary_options_layout.addWidget(self.summarize_checkbox)

        summary_options_layout.addWidget(QLabel("Instruction:"))
        self.instruction_combo = QComboBox()
        # Add some default summarization instructions
        self.instruction_combo.addItem("提示词模版一，注重内容的完整性")
        self.instruction_combo.setItemData(0, Instruction1, Qt.ToolTipRole)
        self.instruction_combo.addItem("提示词模版二，注重内容的精炼性")
        self.instruction_combo.setItemData(1, Instruction2, Qt.ToolTipRole)
        self.instruction_combo.addItem("You are a helpful assistant that processes lecture transcripts...")
        self.instruction_combo.setItemData(2, "You are a helpful assistant that processes lecture transcripts "
                                              "Organize the content into clear sections with headings, bullet points, and highlight key concepts.", Qt.ToolTipRole)
        self.instruction_combo.addItem("Create detailed study notes")
        self.instruction_combo.addItem("Summarize main concepts only")
        self.instruction_combo.addItem("Extract action items and assignments")
        self.instruction_combo.setEditable(True)
        summary_options_layout.addWidget(self.instruction_combo)

        transcription_layout.addLayout(summary_options_layout)

        # Summary area
        transcription_layout.addWidget(QLabel("Summary:"))
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        transcription_layout.addWidget(self.summary_text)

        transcription_group.setLayout(transcription_layout)
        self.main_layout.addWidget(transcription_group)

    def setup_file_operations(self):
        """Set up the file operations UI group."""
        file_ops_layout = QHBoxLayout()

        self.save_transcript_button = QPushButton("Save Transcript")
        self.save_transcript_button.clicked.connect(self.save_transcript)
        self.save_transcript_button.setEnabled(False)
        file_ops_layout.addWidget(self.save_transcript_button)

        self.save_summary_button = QPushButton("Save Summary")
        self.save_summary_button.clicked.connect(self.save_summary)
        self.save_summary_button.setEnabled(False)
        file_ops_layout.addWidget(self.save_summary_button)

        # 添加打开新窗口查看Summary按钮
        self.open_summary_button = QPushButton("Open Summary")
        self.open_summary_button.clicked.connect(self.open_summary)
        self.open_summary_button.setEnabled(True)
        file_ops_layout.addWidget(self.open_summary_button)

        # 添加复制Summary按钮
        self.copy_summary_button = QPushButton("Copy Summary")
        self.copy_summary_button.clicked.connect(self.copy_summary)
        self.copy_summary_button.setEnabled(True)
        file_ops_layout.addWidget(self.copy_summary_button)

        self.main_layout.addLayout(file_ops_layout)

    def open_summary(self):
        """打开摘要文件"""
        if not self.summary_text.toPlainText():
            QMessageBox.warning(self, "No Summary", "No summary to open.")
            return

        # 创建一个新窗口，Filled with TextEdit Widget
        self.new_window = QMainWindow()
        self.new_window.setWindowTitle("Summary")
        self.new_window.resize(660, 700)
        self.central_widget = QWidget()
        self.new_window.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 添加一个TextEdit Widget
        self.summary_text_copy = QTextEdit()
        self.summary_text_copy.setReadOnly(True)
        self.summary_text_copy.setMarkdown(self.summary_text.toMarkdown())
        self.main_layout.addWidget(self.summary_text_copy)

        self.new_window.show()

    def copy_summary(self):
        """复制摘要内容到剪贴板"""
        if not self.summary_text.toPlainText():
            QMessageBox.warning(self, "No Summary", "No summary to copy.")
            return
        # 复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(self.summary_text.toMarkdown())
        self.statusBar().showMessage("Summary copied to clipboard", 3000)


    def browse_output_dir(self):
        """Open a dialog to browse for output directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_input.setPlainText(directory)

    def save_api_config(self):
        """Save API configuration to settings."""
        self.speech_api_key = self.speech_api_key_input.text().strip()
        self.speech_api_url = self.speech_api_url_input.toPlainText().strip()
        self.llm_api_key = self.llm_api_key_input.text().strip()
        self.output_dir = self.output_dir_input.toPlainText().strip()

        # Save to settings
        self.settings.setValue("speech_api_key", self.speech_api_key)
        self.settings.setValue("speech_api_url", self.speech_api_url)
        self.settings.setValue("llm_api_key", self.llm_api_key)
        self.settings.setValue("output_dir", self.output_dir)

        # Reinitialize the transcription manager
        self.init_transcription_manager()

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        self.statusBar().showMessage("Configuration saved", 3000)

    def toggle_recording(self):
        """Toggle between starting and stopping recording."""
        if not self.transcription_manager:
            QMessageBox.warning(self, "Configuration Required",
                                "Please configure API keys and save configuration first.")
            return

        if not self.recording:
            # Start recording
            self.recording = True
            self.transcription_manager.start_recording()
            self.record_timer.start(100)  # Record chunks every 100ms
            self.record_button.setText("Stop Recording")
            self.statusBar().showMessage("Recording...")

            # Start recording time counter
            self.elapsed_time = 0
            self.recording_timer.start(1000)  # Update every second
        else:
            # Stop recording
            self.recording = False
            self.record_timer.stop()
            self.recording_timer.stop()

            # Get the path of the recorded file
            self.current_audio_file = self.transcription_manager.stop_recording()
            self.record_button.setText("Start Recording")

            if self.current_audio_file:
                # Start transcription process
                self.transcribe_audio()

    def update_recording_time(self):
        """Update the displayed recording time."""
        self.elapsed_time += 1
        hours = self.elapsed_time // 3600
        minutes = (self.elapsed_time % 3600) // 60
        seconds = self.elapsed_time % 60
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def record_audio_chunk(self):
        """Record a chunk of audio data."""
        if self.transcription_manager and self.recording:
            self.transcription_manager.record_chunk()

    def open_audio_file(self):
        """Open an existing audio file for transcription."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", self.last_path, "Audio Files & Movie Files" \
                    "(*.wav *.mp3 *.flac *.ogg *.m4a *.mp4 *.avi *.mov *.mkv)"
        )

        if file_path:
            self.setting.setValue('LastFilePath', os.path.dirname(file_path))

            self.current_audio_file = file_path
            self.transcribe_audio()

    def transcribe_audio(self):
        """Submit current audio file for transcription."""
        if not self.transcription_manager or not self.current_audio_file:
            return

        # Clear previous results
        self.transcription_text.clear()
        self.summary_text.clear()

        # Show progress
        self.progress_bar.setVisible(True)
        self.transcription_in_progress = True

        if self.current_audio_file[-4:] in ['.mp4', '.avi', '.mov', '.mkv']:
            # Extract audio from video in a separate thread
            self.audio_extraction_worker = AudioExtractionWorker(self.transcription_manager, self.current_audio_file, self.statusBar())
            self.audio_extraction_worker.extraction_finished.connect(self.on_audio_extraction_finished)
            self.audio_extraction_worker.start()
        else:
            self.start_transcription()

    def on_audio_extraction_finished(self, success, audio_file):
        """Handle the completion of audio extraction."""
        self.progress_bar.setVisible(False)
        if success:
            self.current_audio_file = audio_file
            self.start_transcription()
        else:
            self.transcription_in_progress = False
            QMessageBox.warning(self, "Audio Extraction Error", "Failed to extract audio from video.")

    def start_transcription(self):
        """Start the transcription process."""
        self.statusBar().showMessage("Transcribing audio...")
        success = self.transcription_manager.submit_for_transcription(
            self.current_audio_file, self.language_combo.currentData(), True
        )

        if success:
            self.status_timer.start(2000)  # Check every 2 seconds
        else:
            self.progress_bar.setVisible(False)
            self.transcription_in_progress = False
            QMessageBox.warning(self, "Transcription Error", "Failed to submit audio for transcription.")

    def check_transcription_status(self):
        """Check the status of the current transcription task."""
        if not self.transcription_manager or not self.transcription_in_progress:
            return

        status_info = self.transcription_manager.check_transcription_status()

        if status_info["status"] == "completed":
            # Transcription is complete
            self.transcription_in_progress = False
            self.status_timer.stop()
            self.progress_bar.setVisible(False)

            # Display transcript
            transcript = status_info["result"]
            self.transcription_text.setPlainText(transcript)
            self.statusBar().showMessage("Transcription completed")
            self.save_transcript_button.setEnabled(True)

            # Perform summarization if requested
            if self.summarize_checkbox.isChecked():
                self.summarize_transcript(transcript)
            else:
                self.save_summary_button.setEnabled(False)  # Disable summary save if no summary

        elif status_info["status"] == "failed":
            # Transcription failed
            self.transcription_in_progress = False
            self.status_timer.stop()
            self.progress_bar.setVisible(False)
            error_message = status_info.get("error", "Transcription failed")
            self.statusBar().showMessage("Transcription failed", 5000)
            QMessageBox.critical(self, "Transcription Failed", error_message)

        elif status_info["status"] != "completed":
            # Still in progress, update status bar
            status_message = status_info.get("message", f"Transcription task {status_info['status']}")
            self.statusBar().showMessage(status_message + "...")

    # def summarize_transcript(self, transcript):
    #     """Summarize the given transcript using DeepSeek LLM."""
    #     if not self.transcription_manager:
    #         QMessageBox.warning(self, "Configuration Error", "LLM API Key not configured.")
    #         return
    #
    #     self.statusBar().showMessage("Summarizing transcript...")
    #     instruction = self.instruction_combo.currentText()
    #
    #     summary = self.transcription_manager.summarize_transcript(transcript, instruction)
    #     self.summary_text.setText(summary)
    #     self.statusBar().showMessage("Summary completed")
    #     self.save_summary_button.setEnabled(True)

    def summarize_transcript(self, transcript):
        """Summarize the given transcript using DeepSeek LLM in a separate thread."""
        if not self.transcription_manager:
            QMessageBox.warning(self, "Configuration Error", "LLM API Key not configured.")
            return

        self.statusBar().showMessage("Summarizing transcript...")
        self.summary_text.clear()  # 清空 Summary TextEdit
        self.progress_bar.setVisible(True)  # 显示进度条
        self.progress_bar.setRange(0, 0)  # 设置为不确定进度条

        instruction = self.instruction_combo.currentData(Qt.ToolTipRole)  # 获取提示词
        if not instruction:
            instruction = self.instruction_combo.currentText()
        # 输出当前提示词
        print(instruction)
        # return

        # 创建 SummarizationWorker 实例，如果之前有worker在运行，先停止并清理
        if self.summarization_worker and self.summarization_worker.isRunning():
            self.summarization_worker.quit()
            self.summarization_worker.wait()
            self.summarization_worker.deleteLater()  # 安全删除旧的worker
        self.summarization_worker = SummarizationWorker(self.transcription_manager.api, transcript, instruction)

        # 连接信号和槽
        self.summarization_worker.summary_chunk_ready.connect(self.append_summary_text)
        self.summarization_worker.summary_finished.connect(self.on_summary_finished)
        self.summarization_worker.summary_error.connect(self.on_summary_error)

        self.summarization_worker.start()  # 启动工作线程
        self.save_summary_button.setEnabled(False)  # 禁用保存摘要按钮，直到完成
        self.open_summary_button.setEnabled(False)
        self.copy_summary_button.setEnabled(False)

    def save_transcript(self):
        """Save the transcription to a file."""
        if not self.transcription_text.toPlainText():
            QMessageBox.warning(self, "No Transcript", "No transcript to save.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Transcript", self.output_dir, "Text Files (*.txt)"
        )
        if filepath:
            saved_path = self.transcription_manager.save_transcript(self.transcription_text.toPlainText(), filepath)
            self.statusBar().showMessage(f"Transcript saved to: {saved_path}", 3000)

    def save_summary(self):
        """Save the summary to a file."""
        if not self.summary_text.toPlainText():
            QMessageBox.warning(self, "No Summary", "No summary to save.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Summary", self.output_dir, "Text Files (*.txt)"
        )
        if filepath:
            saved_path = self.transcription_manager.save_summary(self.summary_text.toPlainText(), filepath)
            self.statusBar().showMessage(f"Summary saved to: {saved_path}", 3000)

    @Slot(str)
    def append_summary_text(self, text_chunk):
        """槽函数，用于接收来自后台线程的文本块，并追加到 summary_text 中 (线程安全)."""
        self.summary_text.moveCursor(QTextCursor.End)  # 移动光标到末尾，确保追加内容可见
        self.summary_text.insertPlainText(text_chunk)  # 追加文本块


    @Slot()
    def on_summary_finished(self):
        """槽函数，当总结任务完成时调用."""
        self.progress_bar.setVisible(False)  # 隐藏进度条
        self.statusBar().showMessage("Summary completed")  # 更新状态栏
        self.save_summary_button.setEnabled(True)  # 启用保存摘要按钮
        self.open_summary_button.setEnabled(True)
        self.copy_summary_button.setEnabled(True)
        if self.summarization_worker:  # 清理worker
            self.summarization_worker.deleteLater()
            self.summarization_worker = None
        self.summary_text.setMarkdown(self.summary_text.toPlainText())  # 设置Markdown格式

    @Slot(str)
    def on_summary_error(self, error_message):
        """槽函数，当总结任务发生错误时调用."""
        self.progress_bar.setVisible(False)  # 隐藏进度条
        self.statusBar().showMessage("Summary failed", 5000)  # 状态栏显示错误
        QMessageBox.critical(self, "Summary Failed", error_message)  # 弹出错误提示框
        self.save_summary_button.setEnabled(False)  # 禁用保存摘要按钮
        if self.summarization_worker:  # 清理worker
            self.summarization_worker.deleteLater()
            self.summarization_worker = None

def main():
    app = QApplication(sys.argv)
    mainWin = AudioTranscriptionApp()
    mainWin.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()