# coding:utf-8
from PySide6.QtCore import Qt, QUrl, QStandardPaths, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QWidget, QLabel, QFileDialog, QFontDialog)
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, PushSettingCard,
                            OptionsSettingCard, HyperlinkCard, PrimaryPushSettingCard,
                            ScrollArea, CustomColorSettingCard, ExpandLayout,
                            FluentIcon as FIF, ComboBoxSettingCard,
                            setTheme, setThemeColor, isDarkTheme, FolderListSettingCard,
                            RangeSettingCard, ColorSettingCard, InfoBar)
from qfluentwidgets import Theme

from util.config import cfg, HELP_URL, YEAR, AUTHOR, VERSION
from util.ICON import MODEL, AUDIO_MODEL
from ui.ApiSettingCard import TransAPISettingCard, SummaryAPISettingCard


class SpeechSettingsInterface(ScrollArea):
    """ Setting interface """

    checkUpdateSig = Signal()
    audioFoldersChanged = Signal(list)
    acrylicEnableChanged = Signal(bool)
    downloadFolderChanged = Signal(str)
    minimizeToTrayChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("设置"), self)

        # music folders
        self.generalConfigGroup = SettingCardGroup(
            self.tr("通用配置"), self.scrollWidget)
        self.audioFolderCard = FolderListSettingCard(
            cfg.transcriptionFolders,
            self.tr("本地音频文件夹"),
            directory=QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
            parent=self.generalConfigGroup
        )
        self.transcriptionFolderCard = PushSettingCard(
            self.tr('选择文件夹'),
            FIF.FEEDBACK,
            self.tr("转录保存文件夹"),
            cfg.get(cfg.downloadFolder),
            self.generalConfigGroup
        )
        self.transcriptionModelSettingCard = OptionsSettingCard(
            cfg.transcriptionModel,
            AUDIO_MODEL,
            self.tr('转录模型'),
            self.tr('请选择转录模型'),
            texts=['Local SenseVoice', 'SenseVoice API', 'Google'],
            parent=self.generalConfigGroup
        )
        self.transcriptionAPIKeyCard = TransAPISettingCard()
        self.summaryLLMModelSettingCard = OptionsSettingCard(
            cfg.summaryLLMModel,
            MODEL,
            self.tr('大语言模型'),
            self.tr('请选择大语言总结模型'),
            texts=['DeepSeek-V3', 'DeepSeek-R1', 'GPT-4o'],
            parent=self.generalConfigGroup
        )
        self.summaryLLMModelAPIKeyCard = SummaryAPISettingCard()

        # personalization
        self.personalGroup = SettingCardGroup(self.tr('个性化'), self.scrollWidget)
        self.enableAcrylicCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("Use Acrylic effect"),
            self.tr("Acrylic effect has better visual experience, but it may cause the window to become stuck"),
            configItem=cfg.enableAcrylicBackground,
            parent=self.personalGroup
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('主题'),
            self.tr("请选择外观"),
            texts=[
                self.tr('亮色调'), self.tr('暗色调'),
                self.tr('跟随系统')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard=CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('主题颜色'),
            self.tr('改变应用的主题颜色'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("交互大小"),
            self.tr("改变组件和字体的大小"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("跟随系统")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('语言设置'),
            self.tr('设置UI界面的语言'),
            texts=['简体中文', '繁體中文', 'English', self.tr('跟随系统')],
            parent=self.personalGroup
        )


        # desktop lyric
        self.deskLyricGroup = SettingCardGroup(self.tr('Desktop Lyric'), self.scrollWidget)
        self.deskLyricFontCard = PushSettingCard(
            self.tr('选择字体'),
            FIF.FONT,
            self.tr('字体'),
            parent=self.deskLyricGroup
        )
        self.deskLyricHighlightColorCard = ColorSettingCard(
            cfg.deskLyricHighlightColor,
            FIF.PALETTE,
            self.tr('前景色'),
            parent=self.deskLyricGroup
        )
        self.deskLyricStrokeColorCard = ColorSettingCard(
            cfg.deskLyricStrokeColor,
            FIF.PENCIL_INK,
            self.tr('描边颜色'),
            parent=self.deskLyricGroup
        )
        self.deskLyricStrokeSizeCard = RangeSettingCard(
            cfg.deskLyricStrokeSize,
            FIF.HIGHTLIGHT,
            self.tr('描边大小'),
            parent=self.deskLyricGroup
        )
        self.deskLyricAlignmentCard = OptionsSettingCard(
            cfg.deskLyricAlignment,
            FIF.ALIGNMENT,
            self.tr('对齐方式'),
            texts=[
                self.tr('中心对齐'), self.tr('左对齐'),
                self.tr('右对齐')
            ],
            parent=self.deskLyricGroup
        )

        # main panel
        self.mainPanelGroup = SettingCardGroup(self.tr('主面板'), self.scrollWidget)
        self.minimizeToTrayCard = SwitchSettingCard(
            FIF.MINIMIZE,
            self.tr('Minimize to tray after closing'),
            self.tr('PyQt-Fluent-Widgets will continue to run in the background'),
            configItem=cfg.minimizeToTray,
            parent=self.mainPanelGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            self.tr('The new version will be more stable and have more features'),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('打开帮助文档'),
            FIF.HELP,
            self.tr('Help'),
            self.tr('Discover new features and learn useful tips about PyQt-Fluent-Widgets'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('反馈'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve PyQt-Fluent-Widgets by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('检查更新'),
            FIF.INFO,
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + f" {VERSION}",
            self.aboutGroup
        )

        self.setObjectName("Setting".replace(' ', '-'))

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(60, 63)

        # add cards to group
        self.generalConfigGroup.addSettingCard(self.audioFolderCard)
        self.generalConfigGroup.addSettingCard(self.transcriptionFolderCard)
        self.generalConfigGroup.addSettingCard(self.transcriptionModelSettingCard)
        self.generalConfigGroup.addSettingCard(self.transcriptionAPIKeyCard)
        self.generalConfigGroup.addSettingCard(self.summaryLLMModelSettingCard)
        self.generalConfigGroup.addSettingCard(self.summaryLLMModelAPIKeyCard)

        self.personalGroup.addSettingCard(self.enableAcrylicCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.deskLyricGroup.addSettingCard(self.deskLyricFontCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricHighlightColorCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricStrokeColorCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricStrokeSizeCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricAlignmentCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.generalConfigGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.deskLyricGroup)
        self.expandLayout.addWidget(self.mainPanelGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onDeskLyricFontCardClicked(self):
        """ desktop lyric font button clicked slot """
        isOk, font = QFontDialog.getFont(
            cfg.desktopLyricFont, self.window(), self.tr("Choose font"))
        if isOk:
            cfg.desktopLyricFont = font

    def __onTranscriptionFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.downloadFolder) == folder:
            return

        cfg.set(cfg.downloadFolder, folder)
        self.transcriptionFolderCard.setContent(folder)

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # music in the pc
        self.audioFolderCard.folderChanged.connect(
            self.audioFoldersChanged)
        self.transcriptionFolderCard.clicked.connect(
            self.__onTranscriptionFolderCardClicked)

        # personalization
        self.enableAcrylicCard.checkedChanged.connect(
            self.acrylicEnableChanged)
        self.themeColorCard.colorChanged.connect(setThemeColor)

        # playing interface
        self.deskLyricFontCard.clicked.connect(self.__onDeskLyricFontCardClicked)

        # main panel
        self.minimizeToTrayCard.checkedChanged.connect(
            self.minimizeToTrayChanged)

        # about
        self.aboutCard.clicked.connect(self.checkUpdateSig)
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(cfg.FEEDBACK_URL)))