import sys

from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtGui import QIcon, Qt, QDesktopServices
from PySide6.QtWidgets import QFrame, QHBoxLayout, QApplication, QVBoxLayout, QWidget, QLabel, QFileDialog
from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel, setFont, LineEdit, PasswordLineEdit, \
    ScrollArea, ExpandLayout, SettingCardGroup, FolderListSettingCard, PushSettingCard, SwitchSettingCard, \
    OptionsSettingCard, CustomColorSettingCard, ComboBoxSettingCard, HyperlinkCard, PrimaryPushSettingCard, setTheme, \
    setThemeColor, RangeSettingCard
from qfluentwidgets import FluentIcon as FIF
from ui.setting import SpeechSettingsInterface

class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        # self.label = SubtitleLabel(text, self)
        # self.hBoxLayout = QHBoxLayout(self)
        #
        # setFont(self.label, 24)
        # self.label.setAlignment(Qt.AlignCenter)
        # self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))


class SettingWidget(Widget):

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)

        self.vBoxLayout = QVBoxLayout(self)

        # Speech Transcription API Key Input
        self.speech_api_key_input = PasswordLineEdit()
        self.speech_api_key_input.setPlaceholderText("Your Speech Transcription API Key")
        self.speech_api_key_input.setFixedWidth(360)
        # 启用清空按钮
        self.speech_api_key_input.setClearButtonEnabled(True)

        self.vBoxLayout.addWidget(self.speech_api_key_input, 0, Qt.AlignCenter)

        # Speech Transcription API URL Input
        self.speech_api_url_input = LineEdit()
        self.speech_api_url_input.setPlaceholderText("Your Speech Transcription API URL")
        self.speech_api_url_input.setFixedWidth(360)
        self.speech_api_url_input.setClearButtonEnabled(True)

        self.vBoxLayout.addWidget(self.speech_api_url_input, 0, Qt.AlignCenter)

        # DeepSeek API Key Input
        self.deepseek_api_key_input = PasswordLineEdit()
        self.deepseek_api_key_input.setPlaceholderText("Your DeepSeek API Key")
        self.deepseek_api_key_input.setFixedWidth(360)
        self.deepseek_api_key_input.setClearButtonEnabled(True)

        self.vBoxLayout.addWidget(self.deepseek_api_key_input, 0, Qt.AlignCenter)

        # Recordings Folder Path Input
        self.recordings_folder_path_input = LineEdit()


        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))



class Window(FluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()

        # 创建子界面，实际使用时将 Widget 换成自己的子界面
        self.homeInterface = Widget('Home Interface', self)
        self.recordingInterface = Widget('Recording Interface', self)
        self.transcriptionInterface = Widget('Transcription Interface', self)
        self.settingInterface = SpeechSettingsInterface(self)
        self.summaryInterface = Widget('Summary Interface', self)
        self.deepseekInterface = Widget('Album Interface 1', self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.addSubInterface(self.recordingInterface, FIF.MICROPHONE, 'Recording 404')
        self.addSubInterface(self.transcriptionInterface, FIF.FEEDBACK, 'Transcript 404')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.summaryInterface, FIF.ROBOT, 'Summary 404', NavigationItemPosition.SCROLL)
        self.addSubInterface(self.deepseekInterface, QIcon("./assets/icon/deepseek-color.svg"),
                                                       'DeepSeek', parent=self.summaryInterface)

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('404 Not Sound')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()
