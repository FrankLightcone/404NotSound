# from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import SimpleExpandGroupSettingCard, LineEdit, PasswordLineEdit, BodyLabel, SwitchButton, \
    IndicatorPosition, qconfig, ConfigItem, OptionsConfigItem, ColorConfigItem, OptionsValidator, EnumSerializer, \
    ConfigValidator, QConfig, Theme
from util.ICON import APIKEY


# 修改后的自定义 QConfig 类，包含所有配置项
class AppQConfig(QConfig):
    """ Custom QConfig including all configuration items """

    # 原有的主题配置
    themeMode = OptionsConfigItem(
        "QFluentWidgets", "ThemeMode", Theme.LIGHT, OptionsValidator(Theme), EnumSerializer(Theme))
    themeColor = ColorConfigItem("QFluentWidgets", "ThemeColor", '#009faa')

    # 用户新增的配置项
    TransAPI_api_url = ConfigItem("TransAPI", "api_url", "")
    TransAPI_api_key = ConfigItem("TransAPI", "api_key", "")
    TransAPI_output_tokens = ConfigItem("TransAPI", "output_tokens", False)
    SummaryAPI_api_url = ConfigItem("SummaryAPI", "api_url", "")
    SummaryAPI_api_key = ConfigItem("SummaryAPI", "api_key", "")
    SummaryAPI_output_tokens = ConfigItem("SummaryAPI", "output_tokens", False)


# 实例化自定义配置类
qconfig = AppQConfig()


class TransAPISettingCard(SimpleExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(APIKEY, "转录模型 API 配置", "设置语音转录模型API配置以使用语音转录服务", parent)

        # API Url Input
        self.api_url_input_label = BodyLabel("API URL")
        self.api_url_input = LineEdit()
        self.api_url_input.setPlaceholderText("Your API URL")
        self.api_url_input.setFixedWidth(360)
        self.api_url_input.setClearButtonEnabled(True)
        self.api_url_input.setText(qconfig.get(qconfig.TransAPI_api_url))
        self.api_url_input.textChanged.connect(self._onApiUrlChanged)

        # API Key Input
        self.api_key_input_label = BodyLabel("API Key")
        self.api_key_input = PasswordLineEdit()
        self.api_key_input.setPlaceholderText("Your API Key")
        self.api_key_input.setFixedWidth(360)
        self.api_key_input.setClearButtonEnabled(True)
        self.api_key_input.setText(qconfig.get(qconfig.TransAPI_api_key))
        self.api_key_input.textChanged.connect(self._onApiKeyChanged)

        # Is output tokens
        self.is_output_tokens_label = BodyLabel("是否输出使用 Tokens")
        self.lightnessSwitchButton = SwitchButton("No", self, IndicatorPosition.RIGHT)
        self.lightnessSwitchButton.setOnText("Yes")
        self.lightnessSwitchButton.setChecked(qconfig.get(qconfig.TransAPI_output_tokens))
        self.lightnessSwitchButton.checkedChanged.connect(self._onOutputTokensChanged)

        # Set Layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        # Add Widgets
        self.add(self.api_url_input_label, self.api_url_input)
        self.add(self.api_key_input_label, self.api_key_input)
        self.add(self.is_output_tokens_label, self.lightnessSwitchButton)

        # 连接信号到新的配置项
        qconfig.TransAPI_api_url.valueChanged.connect(self._updateApiUrlInput)
        qconfig.TransAPI_api_key.valueChanged.connect(self._updateApiKeyInput)
        qconfig.TransAPI_output_tokens.valueChanged.connect(self._updateOutputTokensSwitch)

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        self.addGroupWidget(w)

    def _onApiUrlChanged(self, text):
        qconfig.set(qconfig.TransAPI_api_url, text)

    def _onApiKeyChanged(self, text):
        qconfig.set(qconfig.TransAPI_api_key, text)

    def _onOutputTokensChanged(self, checked):
        qconfig.set(qconfig.TransAPI_output_tokens, checked)

    def _updateApiUrlInput(self):
        self.api_url_input.setText(qconfig.get(qconfig.TransAPI_api_url))

    def _updateApiKeyInput(self):
        self.api_key_input.setText(qconfig.get(qconfig.TransAPI_api_key))

    def _updateOutputTokensSwitch(self):
        self.lightnessSwitchButton.setChecked(qconfig.get(qconfig.TransAPI_output_tokens))


class SummaryAPISettingCard(SimpleExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(APIKEY, "总结模型 API 配置", "设置语言模型API配置以使用总结文本服务", parent)

        # API Url Input
        self.api_url_input_label = BodyLabel("API URL")
        self.api_url_input = LineEdit()
        self.api_url_input.setPlaceholderText("Your API URL")
        self.api_url_input.setFixedWidth(360)
        self.api_url_input.setClearButtonEnabled(True)
        self.api_url_input.setText(qconfig.get(qconfig.SummaryAPI_api_url))
        self.api_url_input.textChanged.connect(self._onApiUrlChanged)

        # API Key Input
        self.api_key_input_label = BodyLabel("API Key")
        self.api_key_input = PasswordLineEdit()
        self.api_key_input.setPlaceholderText("Your API Key")
        self.api_key_input.setFixedWidth(360)
        self.api_key_input.setClearButtonEnabled(True)
        self.api_key_input.setText(qconfig.get(qconfig.SummaryAPI_api_key))
        self.api_key_input.textChanged.connect(self._onApiKeyChanged)

        # Is output tokens
        self.is_output_tokens_label = BodyLabel("Output Tokens")
        self.lightnessSwitchButton = SwitchButton("No", self, IndicatorPosition.RIGHT)
        self.lightnessSwitchButton.setOnText("Yes")
        self.lightnessSwitchButton.setChecked(qconfig.get(qconfig.SummaryAPI_output_tokens))
        self.lightnessSwitchButton.checkedChanged.connect(self._onOutputTokensChanged)

        # Set Layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        # Add Widgets
        self.add(self.api_url_input_label, self.api_url_input)
        self.add(self.api_key_input_label, self.api_key_input)
        self.add(self.is_output_tokens_label, self.lightnessSwitchButton)

        # 连接信号到新的配置项
        qconfig.SummaryAPI_api_url.valueChanged.connect(self._updateApiUrlInput)
        qconfig.SummaryAPI_api_key.valueChanged.connect(self._updateApiKeyInput)
        qconfig.SummaryAPI_output_tokens.valueChanged.connect(self._updateOutputTokensSwitch)

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        self.addGroupWidget(w)

    def _onApiUrlChanged(self, text):
        qconfig.set(qconfig.SummaryAPI_api_url, text)

    def _onApiKeyChanged(self, text):
        qconfig.set(qconfig.SummaryAPI_api_key, text)

    def _onOutputTokensChanged(self, checked):
        qconfig.set(qconfig.SummaryAPI_output_tokens, checked)

    def _updateApiUrlInput(self):
        self.api_url_input.setText(qconfig.get(qconfig.SummaryAPI_api_url))

    def _updateApiKeyInput(self):
        self.api_key_input.setText(qconfig.get(qconfig.SummaryAPI_api_key))

    def _updateOutputTokensSwitch(self):
        self.lightnessSwitchButton.setChecked(qconfig.get(qconfig.SummaryAPI_output_tokens))