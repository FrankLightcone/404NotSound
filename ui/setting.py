# coding:utf-8
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, PushSettingCard,
                            OptionsSettingCard, HyperlinkCard, PrimaryPushSettingCard,
                            ScrollArea, CustomColorSettingCard, ExpandLayout,
                            FluentIcon as FIF, ComboBoxSettingCard,
                            PasswordLineEdit, LineEdit, setTheme, setThemeColor)
from PySide6.QtCore import Qt, QUrl, QStandardPaths
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QWidget, QLabel, QFileDialog, QVBoxLayout)
from qfluentwidgets import ConfigItem, Theme
from util.config import cfg



class ConfigManager:
    """ A simple configuration manager to handle settings """

    def __init__(self):
        # Theme mode settings
        self.themeMode = 'light'  # Default to light theme

        # API Keys and URLs
        self.speechApiKey = ''
        self.speechApiUrl = ''
        self.deepseekApiKey = ''

        # Recordings folder
        self.recordingsFolder = ''

    def setThemeMode(self, mode):
        """ Set theme mode: 'light', 'dark', or 'system' """
        self.themeMode = mode

    def setSpeechApiKey(self, key):
        """ Set Speech API Key """
        self.speechApiKey = key

    def setSpeechApiUrl(self, url):
        """ Set Speech API URL """
        self.speechApiUrl = url

    def setDeepseekApiKey(self, key):
        """ Set DeepSeek API Key """
        self.deepseekApiKey = key

    def setRecordingsFolder(self, folder):
        """ Set recordings folder path """
        self.recordingsFolder = folder


class SpeechSettingsInterface(ScrollArea):
    """ Speech Transcription Settings Interface """

    def __init__(self, parent=None, config=None):
        super().__init__(parent=parent)


        # Use provided config or create a new one
        self.cfg = config if config is not None else ConfigManager()

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # Setting label
        self.settingLabel = QLabel(self.tr("Speech Transcription Settings"), self)

        # API Configuration Group
        self.apiGroup = SettingCardGroup(
            self.tr("API Configuration"), self.scrollWidget)

        # Speech Transcription API Key Input Card
        self.speechApiKeyCard = PushSettingCard(
            self.tr("Edit API Key"),
            FIF.EDIT,
            self.tr("Speech Transcription API Key"),
            self.tr("Configure your speech transcription API credentials"),
            self.apiGroup
        )

        # Speech Transcription API URL Input Card
        self.speechApiUrlCard = PushSettingCard(
            self.tr("Edit API URL"),
            FIF.LINK,
            self.tr("Speech Transcription API URL"),
            self.tr("Configure your speech transcription API endpoint"),
            self.apiGroup
        )

        # DeepSeek API Key Input Card
        self.deepseekApiKeyCard = PushSettingCard(
            self.tr("Edit API Key"),
            FIF.EDIT,
            self.tr("DeepSeek API Key"),
            self.tr("Configure your DeepSeek API credentials"),
            self.apiGroup
        )

        # Recordings Folder Group
        self.recordingsGroup = SettingCardGroup(
            self.tr("Recordings"), self.scrollWidget)
        self.recordingsFolderCard = PushSettingCard(
            self.tr('Choose folder'),
            FIF.FOLDER,
            self.tr("Recordings Directory"),
            self.tr("Select the directory to store your recordings"),
            self.recordingsGroup
        )

        # Personalization Group
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)

        # Theme Card with actual configuration
        # 然后在 __init__ 方法中修改 themeCard 的初始化
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,  # 使用 ConfigItem
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )

        # Theme Color Card
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,  # You might want to add a theme color to your config
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of your application'),
            self.personalGroup
        )

        # About Group
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve the application by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('About'),
            FIF.INFO,
            self.tr('About'),
            self.tr('Speech Transcription Application\nVersion 1.0.0'),
            self.aboutGroup
        )

        # Initialize the interface
        self.__initWidget()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

    def __initLayout(self):
        # Add groups to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)

        # Add API Configuration Group
        self.apiGroup.addSettingCard(self.speechApiKeyCard)
        self.apiGroup.addSettingCard(self.speechApiUrlCard)
        self.apiGroup.addSettingCard(self.deepseekApiKeyCard)
        self.expandLayout.addWidget(self.apiGroup)

        # Add Recordings Group
        self.recordingsGroup.addSettingCard(self.recordingsFolderCard)
        self.expandLayout.addWidget(self.recordingsGroup)

        # Add Personalization Group
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.expandLayout.addWidget(self.personalGroup)

        # Add About Group
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)
        self.expandLayout.addWidget(self.aboutGroup)

    def __connectSignalToSlot(self):
        """ Connect signals to slots """
        # Recordings folder selection
        self.recordingsFolderCard.clicked.connect(self.__onRecordingsFolderCardClicked)

        # Feedback card
        self.feedbackCard.clicked.connect(self.__onFeedbackCardClicked)

        # Theme mode change
        self.themeCard.optionChanged.connect(self.__onThemeModeChanged)

    def __onRecordingsFolderCardClicked(self):
        """ Handle recordings folder selection """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose Recordings Folder"), "./")
        if folder:
            self.cfg.setRecordingsFolder(folder)
            self.recordingsFolderCard.setContent(folder)

    def __onFeedbackCardClicked(self):
        """ Open feedback URL """
        feedback_url = "https://github.com/yourusername/yourproject/issues"
        QDesktopServices.openUrl(QUrl(feedback_url))

    def __onThemeModeChanged(self, index):
        """ Handle theme mode change """
        theme_modes = ['light', 'dark', 'system']
        self.cfg.setThemeMode(theme_modes[index])
        # 这里可以添加实际的主题切换逻辑


# 使用示例
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    config = ConfigManager()  # 创建配置管理器
    window = SpeechSettingsInterface(config=config)
    window.show()
    sys.exit(app.exec())