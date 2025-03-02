import os
import time
import wave
import pyaudio
import tempfile
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from openai import OpenAI


class AudioRecorder:
    """
    Class for handling audio recording functionality.
    """

    def __init__(self, channels=1, rate=16000, chunk=4096, format=pyaudio.paInt16):
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.format = format
        self.p = None
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.temp_file = None

    def start_recording(self) -> None:
        """Start recording audio from microphone."""
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.is_recording = True

    def stop_recording(self) -> str:
        """
        Stop recording audio and save to a temporary WAV file.

        Returns:
            str: Path to the saved temporary WAV file
        """
        if not self.is_recording:
            return ""

        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if self.p:
            self.p.terminate()

        # Create a unique temporary file
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_filename = self.temp_file.name
        self.temp_file.close()

        # Save recorded audio to the temporary file
        with wave.open(temp_filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))

        return temp_filename

    def record_chunk(self) -> None:
        """Record a chunk of audio data."""
        if self.is_recording and self.stream:
            data = self.stream.read(self.chunk)
            self.frames.append(data)

    def save_to_file(self, filepath: str) -> None:
        """
        Save the recorded audio to a specified file path.

        Args:
            filepath (str): Path where to save the WAV file
        """
        if not self.frames:
            return

        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))


@dataclass
class TranscriptionTask:
    """Data class to hold transcription task information."""
    task_id: str
    file_path: str
    created_at: str
    language: str
    is_final: bool
    status: str = "queued"
    result: str = ""
    error: str = ""


class DeepSeekAPI:
    """
    Class for handling DeepSeek API interactions for both speech recognition and LLM.
    """

    def __init__(self, speech_api_key: str, speech_api_url: str, llm_api_key: str):
        self.speech_api_key = speech_api_key
        self.speech_api_url = speech_api_url
        self.llm_api_key = llm_api_key
        self.llm_client = OpenAI(api_key=llm_api_key, base_url="https://api.deepseek.com")
        self.tasks: Dict[str, TranscriptionTask] = {}

    def transcribe_audio(self, file_path: str, language: str = "auto", is_final: bool = False) -> Optional[
        TranscriptionTask]:
        """
        Submit audio file for transcription.

        Args:
            file_path (str): Path to the audio file
            language (str): Language code or 'auto' for auto-detection
            is_final (bool): Whether this is a final transcription

        Returns:
            Optional[TranscriptionTask]: The created transcription task or None if failed
        """
        try:
            # Prepare request
            url = f"{self.speech_api_url}/recognize"
            headers = {"X-API-Key": self.speech_api_key}

            with open(file_path, "rb") as audio_file:
                files = {"file": audio_file}
                data = {"language": language, "is_final": str(is_final).lower()}

                # Send request
                response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code == 200:
                response_data = response.json()
                task_id = response_data.get("task_id")

                # Create and store task info
                task = TranscriptionTask(
                    task_id=task_id,
                    file_path=file_path,
                    created_at=datetime.now().isoformat(),
                    language=language,
                    is_final=is_final
                )
                self.tasks[task_id] = task
                return task
            else:
                print(f"Transcription request failed: {response.text}")
                return None

        except Exception as e:
            print(f"Error submitting transcription: {e}")
            return None

    def check_transcription_status(self, task_id: str) -> Optional[TranscriptionTask]:
        """
        Check the status of a transcription task.

        Args:
            task_id (str): ID of the task to check

        Returns:
            Optional[TranscriptionTask]: Updated task info or None if failed
        """
        if task_id not in self.tasks:
            print(f"Task ID {task_id} not found")
            return None

        try:
            url = f"{self.speech_api_url}/status/{task_id}"
            headers = {"X-API-Key": self.speech_api_key}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                status_data = response.json()
                task = self.tasks[task_id]

                # Update task info
                task.status = status_data.get("status", "unknown")

                if task.status == "completed":
                    task.result = status_data.get("result", "")
                elif task.status == "failed":
                    task.error = status_data.get("error", "Unknown error")

                return task
            else:
                print(f"Status check failed: {response.text}")
                return None

        except Exception as e:
            print(f"Error checking transcription status: {e}")
            return None

    # def summarize_text(self, text: str, instruction: str) -> str:
    #     """
    #     Use DeepSeek LLM to summarize or process the transcribed text.
    #
    #     Args:
    #         text (str): The transcribed text to process
    #         instruction (str): Instruction for how to process the text
    #
    #     Returns:
    #         str: The processed/summarized text
    #     """
    #     try:
    #         system_prompt = "You are a helpful assistant that processes lecture transcripts. Organize the content into clear sections with headings, bullet points, and highlight key concepts."
    #
    #         if instruction:
    #             system_prompt = instruction
    #
    #         response = self.llm_client.chat.completions.create(
    #             model="deepseek-chat",
    #             messages=[
    #                 {"role": "system", "content": system_prompt},
    #                 {"role": "user", "content": f"Here is the transcript to process:\n\n{text}"},
    #             ],
    #             stream=False
    #         )
    #
    #         return response.choices[0].message.content
    #
    #     except Exception as e:
    #         print(f"Error summarizing with LLM: {e}")
    #         return f"Error processing text: {str(e)}"

    def summarize_text(self, text: str, instruction: str):  # 去掉 -> str 返回值类型注解，改为生成器
        """
        Use DeepSeek LLM to summarize or process the transcribed text (流式输出).

        Args:
            text (str): The transcribed text to process
            instruction (str): Instruction for how to process the text

        Yields:
            str:  Summary text chunks from the stream.
        """
        try:
            system_prompt = "You are a helpful assistant that processes lecture transcripts. Organize the content into clear sections with headings, bullet points, and highlight key concepts."

            if instruction:
                system_prompt = instruction

            response_stream = self.llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the transcript to process:\n\n{text}"},
                ],
                stream=True  # 启用流式输出
            )

            for chunk in response_stream:  # 迭代流式响应
                if chunk.choices:
                    text_chunk = chunk.choices[0].delta.content
                    if text_chunk:
                        yield text_chunk  # 使用 yield 返回文本块

        except Exception as e:
            error_str = f"Error summarizing with LLM: {e}"
            print(error_str)
            yield error_str  # 出错时也 yield 错误信息 (或者可以抛出异常，根据具体需求)


class TranscriptionManager:
    """
    Main class to manage the entire workflow of recording, transcribing, and summarizing.
    """

    def __init__(self,
                 speech_api_key: str,
                 speech_api_url: str,
                 llm_api_key: str,
                 output_dir: str = "transcriptions"):
        self.recorder = AudioRecorder()
        self.api = DeepSeekAPI(speech_api_key, speech_api_url, llm_api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.current_task: Optional[TranscriptionTask] = None

    def start_recording(self) -> None:
        """Start recording audio."""
        self.recorder.start_recording()

    def stop_recording(self) -> str:
        """Stop recording and return the path to the recorded file."""
        return self.recorder.stop_recording()

    def record_chunk(self) -> None:
        """Record a chunk of audio data."""
        self.recorder.record_chunk()

    def is_recording(self) -> bool:
        """Check if recording is in progress."""
        return self.recorder.is_recording

    def submit_for_transcription(self, file_path: str, language: str = "auto", is_final: bool = False) -> bool:
        """
        Submit a recorded audio file for transcription.

        Returns:
            bool: True if submission was successful, False otherwise
        """
        task = self.api.transcribe_audio(file_path, language, is_final)
        if task:
            self.current_task = task
            return True
        return False

    def check_transcription_status(self) -> Dict[str, Any]:
        """
        Check the status of the current transcription task.

        Returns:
            Dict[str, Any]: A dictionary with the current status info
        """
        if not self.current_task:
            return {"status": "no_task", "message": "No active transcription task"}

        task = self.api.check_transcription_status(self.current_task.task_id)
        if not task:
            return {"status": "error", "message": "Failed to check task status"}

        if task.status == "completed":
            return {
                "status": "completed",
                "result": task.result,
                "task_id": task.task_id
            }
        elif task.status == "failed":
            return {
                "status": "failed",
                "error": task.error,
                "task_id": task.task_id
            }
        else:
            return {
                "status": task.status,
                "message": f"Task is {task.status}",
                "task_id": task.task_id
            }

    def summarize_transcript(self, text: str, instruction: str = "") -> str:
        """
        Summarize or process the transcribed text.

        Args:
            text (str): The text to process
            instruction (str): Custom instruction for the LLM

        Returns:
            str: The processed/summarized text
        """
        return self.api.summarize_text(text, instruction)

    def save_transcript(self, text: str, filename: str = "") -> str:
        """
        Save the transcript to a file.

        Args:
            text (str): The text to save
            filename (str): Optional custom filename

        Returns:
            str: Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{timestamp}.txt"

        file_path = self.output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        return str(file_path)

    def save_summary(self, text: str, filename: str = "") -> str:
        """
        Save the summary to a file.

        Args:
            text (str): The text to save
            filename (str): Optional custom filename

        Returns:
            str: Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_{timestamp}.txt"

        file_path = self.output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        return str(file_path)

    def process_audio_file(self, file_path: str,
                           language: str = "auto",
                           wait_for_completion: bool = True,
                           summarize: bool = True,
                           instruction: str = "") -> Dict[str, Any]:
        """
        Process an existing audio file (transcribe and optionally summarize).

        Args:
            file_path (str): Path to the audio file
            language (str): Language code or 'auto'
            wait_for_completion (bool): Whether to wait for transcription to complete
            summarize (bool): Whether to summarize the transcript
            instruction (str): Custom instruction for summarization

        Returns:
            Dict[str, Any]: Dictionary with results
        """
        # Submit for transcription
        if not self.submit_for_transcription(file_path, language, True):
            return {"status": "error", "message": "Failed to submit for transcription"}

        # Wait for completion if requested
        if wait_for_completion:
            while True:
                status_info = self.check_transcription_status()
                if status_info["status"] in ["completed", "failed", "error"]:
                    break
                time.sleep(2)

            if status_info["status"] != "completed":
                return status_info

            # Save transcript
            transcript = status_info["result"]
            transcript_path = self.save_transcript(transcript)

            # Summarize if requested
            if summarize and transcript:
                summary = self.summarize_transcript(transcript, instruction)
                summary_path = self.save_summary(summary)
                return {
                    "status": "success",
                    "transcript": transcript,
                    "transcript_path": transcript_path,
                    "summary": summary,
                    "summary_path": summary_path
                }
            else:
                return {
                    "status": "success",
                    "transcript": transcript,
                    "transcript_path": transcript_path
                }
        else:
            # Just return the task info if not waiting
            return {
                "status": "submitted",
                "task_id": self.current_task.task_id,
                "message": "Transcription submitted, check status later"
            }