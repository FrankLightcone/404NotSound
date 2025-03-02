from PySide6.QtCore import QThread, Signal, Slot

class SummarizationWorker(QThread):
    """
    后台执行总结任务的工作线程。
    """
    summary_chunk_ready = Signal(str)  # 用于发送总结文本块的信号
    summary_finished = Signal()       # 用于通知总结完成的信号
    summary_error = Signal(str)        # 用于通知总结错误的信号

    def __init__(self, api, text: str, instruction: str = ""):
        super().__init__()
        self.api = api
        self.text = text
        self.instruction = instruction

    def run(self):
        """
        在线程中执行总结任务。
        """
        try:
            system_prompt = "You are a helpful assistant that processes lecture transcripts. Organize the content into clear sections with headings, bullet points, and highlight key concepts."
            if self.instruction:
                system_prompt = self.instruction

            response_stream = self.api.llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the transcript to process:\n\n{self.text}"},
                ],
                stream=True # 启用流式输出
            )

            for chunk in response_stream:
                if chunk.choices:
                    text_chunk = chunk.choices[0].delta.content
                    if text_chunk:
                        self.summary_chunk_ready.emit(text_chunk) # 发射信号，传递文本块

            self.summary_finished.emit() # 发射信号，通知总结完成

        except Exception as e:
            error_str = f"Error summarizing with LLM: {str(e)}"
            print(error_str)
            self.summary_error.emit(error_str) # 发射信号，通知错误