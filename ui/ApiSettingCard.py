from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import SimpleExpandGroupSettingCard, LineEdit, PasswordLineEdit, BodyLabel, SwitchButton, \
    IndicatorPosition
from util.ICON import APIKEY

class TransAPISettingCard(SimpleExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(APIKEY, "Transcription API Config", "Set Audio Recognition Model API Url and API Key to use the API Service", parent)

        # API Url Input
        self.api_url_input_label = BodyLabel("API URL")
        self.api_url_input = LineEdit()
        self.api_url_input.setPlaceholderText("Your API URL")
        self.api_url_input.setFixedWidth(360)
        self.api_url_input.setClearButtonEnabled(True)

        # API Key Input
        self.api_key_input_label = BodyLabel("API Key")
        self.api_key_input = PasswordLineEdit()
        self.api_key_input.setPlaceholderText("Your API Key")
        self.api_key_input.setFixedWidth(360)
        self.api_key_input.setClearButtonEnabled(True)

        # Is output tokens
        self.is_output_tokens_label = BodyLabel("Output Tokens")
        self.lightnessSwitchButton = SwitchButton("No", self, IndicatorPosition.RIGHT)
        self.lightnessSwitchButton.setOnText("Yes")

        # Set Layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        # Add Widgets
        self.add(self.api_url_input_label, self.api_url_input)
        self.add(self.api_key_input_label, self.api_key_input)
        self.add(self.is_output_tokens_label, self.lightnessSwitchButton)

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        # 添加组件到设置卡
        self.addGroupWidget(w)

class SummaryAPISettingCard(SimpleExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(APIKEY, "Summary LLM API Config", "Set LLM API Url and API Key to use the API Service", parent)

        # API Url Input
        self.api_url_input_label = BodyLabel("API URL")
        self.api_url_input = LineEdit()
        self.api_url_input.setPlaceholderText("Your API URL")
        self.api_url_input.setFixedWidth(360)
        self.api_url_input.setClearButtonEnabled(True)

        # API Key Input
        self.api_key_input_label = BodyLabel("API Key")
        self.api_key_input = PasswordLineEdit()
        self.api_key_input.setPlaceholderText("Your API Key")
        self.api_key_input.setFixedWidth(360)
        self.api_key_input.setClearButtonEnabled(True)

        # Is output tokens
        self.is_output_tokens_label = BodyLabel("Output Tokens")
        self.lightnessSwitchButton = SwitchButton("No", self, IndicatorPosition.RIGHT)
        self.lightnessSwitchButton.setOnText("Yes")

        # Set Layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        # Add Widgets
        self.add(self.api_url_input_label, self.api_url_input)
        self.add(self.api_key_input_label, self.api_key_input)
        self.add(self.is_output_tokens_label, self.lightnessSwitchButton)


    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        # 添加组件到设置卡
        self.addGroupWidget(w)