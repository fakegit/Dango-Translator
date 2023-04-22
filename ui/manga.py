# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import base64

import ui.static.icon
import utils.translater
import translator.ocr.dango
import translator.api
import utils.thread


# 说明界面
class Manga(QWidget) :

    def __init__(self, object) :

        super(Manga, self).__init__()

        self.object = object
        self.logger = object.logger
        self.getInitConfig()
        self.ui()


    def ui(self) :

        # 窗口尺寸及不可拉伸
        self.resize(self.window_width, self.window_height)
        self.setMinimumSize(QSize(self.window_width, self.window_height))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # 窗口标题
        self.setWindowTitle("漫画翻译")
        # 窗口图标
        self.setWindowIcon(ui.static.icon.APP_LOGO_ICON)
        # 鼠标样式
        self.setCursor(ui.static.icon.PIXMAP_CURSOR)
        # 设置字体
        self.setStyleSheet("font: %spt '%s';"%(self.font_size, self.font_type))

        self.status_label = QLabel(self)
        self.customSetGeometry(self.status_label, 10, 670, 1200, 20)

        # 导入原图
        button = QPushButton(self)
        self.customSetGeometry(button, 0, 0, 120, 35)
        button.setText(" 导入原图")
        button.setStyleSheet("QPushButton {background: transparent;}"
                             "QPushButton:hover {background-color: #83AAF9;}"
                             "QPushButton:pressed {background-color: #4480F9;}")
        button.setIcon(ui.static.icon.OPEN_ICON)
        button.clicked.connect(self.openImageFiles)

        # 选择翻译源
        button = QPushButton(self)
        self.customSetGeometry(button, 120, 0, 120, 35)
        button.setText(" 选择翻译源")
        button.setStyleSheet("QPushButton {background: transparent;}"
                             "QPushButton:hover {background-color: #83AAF9;}"
                             "QPushButton:pressed {background-color: #4480F9;}")
        button.setIcon(ui.static.icon.TRANSLATE_ICON)
        # 翻译源菜单
        self.trans_menu = QMenu(button)
        self.trans_action_group = QActionGroup(self.trans_menu)
        self.trans_action_group.setExclusive(True)
        self.create_trans_action("私人-彩云翻译")
        self.create_trans_action("私人-腾讯翻译")
        self.create_trans_action("私人-百度翻译")
        self.create_trans_action("私人-ChatGPT翻译")
        # self.create_trans_action("公共-有道翻译")
        # self.create_trans_action("公共-百度翻译")
        # self.create_trans_action("公共-腾讯翻译")
        # self.create_trans_action("公共-DeepL翻译")
        # self.create_trans_action("公共-Bing翻译")
        # self.create_trans_action("公共-彩云翻译")
        # 将下拉菜单设置为按钮的菜单
        button.setMenu(self.trans_menu)
        self.trans_action_group.triggered.connect(self.change_select_trans)

        # 工具栏横向分割线
        label = QLabel(self)
        self.customSetGeometry(label, 0, 35, self.window_width, 1)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameShape(QFrame.Box)
        label.setStyleSheet("border-width: 1px; "
                            "border-style: solid; "
                            "border-color: rgba(62, 62, 62, 0.2);")

        # 原图按钮
        self.old_images_button = QPushButton(self)
        self.customSetGeometry(self.old_images_button, 0, 35, 75, 25)
        self.old_images_button.setText("原图")
        self.old_images_button.setStyleSheet("QPushButton {background: transparent;}"
                             "QPushButton:hover {background-color: #83AAF9;}")
        self.old_images_button.clicked.connect(self.clickOldImages)

        # 原图按钮 和 译图按钮 竖向分割线
        label = QLabel(self)
        self.customSetGeometry(label, 74, 35, 1, 25)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameShape(QFrame.Box)
        label.setStyleSheet("border-width: 1px; "
                            "border-style: solid; "
                            "border-color: rgba(62, 62, 62, 0.2);")

        # 译图按钮
        self.new_images_button = QPushButton(self)
        self.customSetGeometry(self.new_images_button, 75, 35, 75, 25)
        self.new_images_button.setText("译图")
        self.new_images_button.setStyleSheet("QPushButton {background: transparent;}"
                             "QPushButton:hover {background-color: #83AAF9;}")
        self.new_images_button.clicked.connect(self.clickNewImages)

        # 译图右侧竖向分割线
        label = QLabel(self)
        self.customSetGeometry(label, 149, 35, 1, 25)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameShape(QFrame.Box)
        label.setStyleSheet("border-width: 1px; "
                            "border-style: solid; "
                            "border-color: rgba(62, 62, 62, 0.2);")

        # 原图列表框
        self.old_image_widget = QListWidget(self)
        self.customSetGeometry(self.old_image_widget, 0, 60, 150, 610)
        self.old_image_widget.setIconSize(QSize(100*self.rate, 100*self.rate))
        self.old_image_widget.itemSelectionChanged.connect(self.loadOldImage)
        self.old_image_widget.hide()
        self.old_image_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.old_image_widget.customContextMenuRequested.connect(self.showOldListWidgetMenu)

        # 译图列表框
        self.new_image_widget = QListWidget(self)
        self.customSetGeometry(self.new_image_widget, 0, 60, 150, 610)
        self.new_image_widget.setIconSize(QSize(100*self.rate, 100*self.rate))
        self.new_image_widget.itemSelectionChanged.connect(self.loadNewImage)
        self.new_image_widget.hide()
        self.new_image_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.new_image_widget.customContextMenuRequested.connect(self.showNewListWidgetMenu)

        # 图片大图展示
        self.show_image_scroll_area = QScrollArea(self)
        self.customSetGeometry(self.show_image_scroll_area, 150, 35, 850, 635)
        self.show_image_scroll_area.setWidgetResizable(True)
        self.show_image_label = QLabel(self)
        self.show_image_scroll_area.setWidget(self.show_image_label)

        # 译文文本列表框
        self.text_list_widget = QListWidget(self)
        self.customSetGeometry(self.text_list_widget, 1000, 35, 200, 635)

        # 底部横向分割线
        label = QLabel(self)
        self.customSetGeometry(label, 150, 670, self.window_width, 1)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameShape(QFrame.Box)
        label.setStyleSheet("border-width: 1px; "
                            "border-style: solid; "
                            "border-color: rgba(62, 62, 62, 0.2);")


    # 初始化配置
    def getInitConfig(self):

        # 界面缩放比例
        self.rate = self.object.yaml["screen_scale_rate"]
        # 界面字体
        self.font_type = "华康方圆体W7"
        # 界面字体大小
        self.font_size = 10
        # 界面尺寸
        self.window_width = int(1200 * self.rate)
        self.window_height = int(700 * self.rate)
        # 原图路径字典
        self.old_image_path_list = []
        # 译图路径字典
        self.new_image_path_list = []
        # ocr结果保存路径
        self.ocr_result_map = {}
        # 翻译结果暂存
        self.trans_result_map = {}
        # 文字消除结果暂存
        self.ipt_result_map = {}
        # 文字渲染结果暂存
        self.rdr_result_map = {}


    # 根据分辨率定义控件位置尺寸
    def customSetGeometry(self, object, x, y, w, h):

        object.setGeometry(QRect(int(x * self.rate),
                                 int(y * self.rate), int(w * self.rate),
                                 int(h * self.rate)))


    # 创建下拉菜单
    def create_trans_action(self, label) :

        action = QAction(label, self.trans_menu)
        action.setCheckable(True)
        action.setData(label)
        self.trans_action_group.addAction(action)
        self.trans_menu.addAction(action)
        if self.object.config["mangaTrans"] == label :
            action.setChecked(True)
            self.status_label.setText("正在使用: {}".format(label))


    # 改变所使用的翻译源
    def change_select_trans(self, action) :

        self.object.config["mangaTrans"] = action.data()
        self.status_label.setText("正在使用: {}".format(action.data()))


    # 设置原图列表框右键菜单
    def showOldListWidgetMenu(self, pos) :

        item = self.old_image_widget.itemAt(pos)
        if item is not None:
            menu = QMenu(self)
            # 添加菜单项
            translater_action = menu.addAction("翻译")
            translater_action.triggered.connect(lambda: self.translaterItemWidget(item))
            delete_action = menu.addAction("移除")
            delete_action.triggered.connect(lambda: self.removeItemWidget(item))

            # 显示菜单
            cursorPos = QCursor.pos()
            menu.exec_(cursorPos)


    # 设置译图列表框右键菜单
    def showNewListWidgetMenu(self, pos):

        item = self.new_image_widget.itemAt(pos)
        if item is not None:
            menu = QMenu(self)
            # 添加菜单项
            output_action = menu.addAction("另存为")
            output_action.triggered.connect(lambda: self.saveImageItemWidget(item))

            # 显示菜单
            cursorPos = QCursor.pos()
            menu.exec_(cursorPos)


    # 译图框保存图片
    def saveImageItemWidget(self, item) :

        row = self.old_image_widget.indexFromItem(item).row()
        image_path = self.new_image_path_list[row]

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self,
                                                   "译图另存为",
                                                   image_path,
                                                   "图片类型(*.png *.jpg *.jpeg);;所有类型 (*)",
                                                   options=options)
        if file_path :
            rdr_result = self.rdr_result_map[image_path]
            with open(file_path, "wb") as file :
                file.write(base64.b64decode(rdr_result))


    # 列表框右键菜单删除子项
    def removeItemWidget(self, item) :

        row = self.old_image_widget.indexFromItem(item).row()
        self.old_image_widget.takeItem(row)
        image_path = self.old_image_path_list[row]

        # 列表框删除图片
        del self.old_image_path_list[row]
        if image_path in self.ocr_result_map :
            ocr_result = self.ocr_result_map[image_path]
            # 删除ocr缓存
            del self.ocr_result_map[image_path]
            for val in ocr_result["text_block"] :
                if not val["text"] :
                    continue
                original = ""
                for text in val["text"] :
                    original += text
                if not original :
                    continue
                if original in self.trans_result_map :
                    # 删除翻译缓存
                    del self.trans_result_map[original]


    # 打开图片文件列表
    def openImageFiles(self) :

        dir_path = self.object.yaml.get("manga_dir_path", os.getcwd())
        options = QFileDialog.Options()
        images, _ = QFileDialog.getOpenFileNames(self,
                                                 "选择要翻译的生肉漫画原图（可多选）",
                                                 dir_path,
                                                 "图片类型(*.png *.jpg *.jpeg);;所有类型 (*)",
                                                 options=options)
        # 遍历文件列表, 将每个文件路径添加到列表框中
        for image_path in images :
            if image_path in self.old_image_path_list :
                continue
            self.old_image_path_list.append(image_path)
            item = QListWidgetItem(image_path, self.old_image_widget)
            item.setIcon(QIcon(image_path))
            item.setText(os.path.basename(image_path))
            self.old_image_widget.addItem(item)

        for image_path in images :
            manga_dir_path = os.path.dirname(image_path)
            # 记忆上次操作的目录
            self.object.yaml["manga_dir_path"] = manga_dir_path

            break


    # 点击原图按钮
    def clickOldImages(self) :

        self.old_image_widget.show()
        self.new_image_widget.hide()
        self.old_images_button.setStyleSheet("background-color: #83AAF9;")
        self.new_images_button.setStyleSheet("QPushButton {background: transparent;}"
                                             "QPushButton:hover {background-color: #83AAF9;}")


    # 点击译图按钮
    def clickNewImages(self) :

        self.old_image_widget.hide()
        self.new_image_widget.show()
        self.new_images_button.setStyleSheet("background-color: #83AAF9;")
        self.old_images_button.setStyleSheet("QPushButton {background: transparent;}"
                                             "QPushButton:hover {background-color: #83AAF9;}")


    # 展示译图图片大图
    def loadNewImage(self) :

        index = self.new_image_widget.currentIndex().row()
        if index < len(self.new_image_path_list) :
            image_path = self.new_image_path_list[index]
            rdr_result = self.rdr_result_map[image_path]
            image = QImage.fromData(base64.b64decode(rdr_result))
            pixmap = QPixmap.fromImage(image)
            self.show_image_label.setPixmap(pixmap)
            self.show_image_label.resize(pixmap.width(), pixmap.height())
            # 刷新文本列表框
            self.refreshTextListWidget(image_path)


    # 展示原图图片大图
    def loadOldImage(self) :

        index = self.old_image_widget.currentIndex().row()
        if index < len(self.old_image_path_list) :
            image_path = self.old_image_path_list[index]
            with open(image_path, "rb") as file :
                image = QImage.fromData(file.read())
            pixmap = QPixmap.fromImage(image)
            self.show_image_label.setPixmap(pixmap)
            self.show_image_label.resize(pixmap.width(), pixmap.height())
            # 刷新文本列表框
            self.refreshTextListWidget(image_path)


    # 文本列表框添加子项
    def textListWidgetAdd(self, text) :

        text_edit = QTextEdit()
        text_edit.append(text)
        text_item = QListWidgetItem()
        text_item.setSizeHint(text_edit.sizeHint())
        self.text_list_widget.addItem(text_item)
        self.text_list_widget.setItemWidget(text_item, text_edit)


    # 刷新文本列表框
    def refreshTextListWidget(self, image_path) :

        # 重置文本列表
        self.text_list_widget.clear()
        # 提取ocr文本
        if image_path not in self.ocr_result_map :
            return
        for val in self.ocr_result_map[image_path]["text_block"]:
            if not val["text"]:
                continue
            original = ""
            for text in val["text"]:
                original += text
            if not original:
                continue
            # ocr结果加入文本列表
            self.textListWidgetAdd(original)
            # 翻译结果加入文本列表
            if original not in self.trans_result_map :
                continue
            self.textListWidgetAdd(self.trans_result_map[original])


    # 单图翻译
    def translaterItemWidget(self, item) :

        row = self.old_image_widget.indexFromItem(item).row()
        image_path = self.old_image_path_list[row]
        # 漫画OCR
        if image_path not in self.ocr_result_map :
            ocr_sign, ocr_result = translator.ocr.dango.mangaOCR(self.object, image_path)
            # 如果请求漫画OCR出错
            if not ocr_sign :
                # @TODO 补全出错逻辑
                return

            # 缓存ocr结果
            dango_manga_path, file_name = self.getDangoMangaPath(image_path)
            ocr_result_file = os.path.join(dango_manga_path, "{}.json".format(file_name))
            with open(ocr_result_file, "w", encoding="utf-8") as file :
                json.dump(ocr_result, file, indent=4)

            mask_result_file = os.path.join(dango_manga_path, "{}_mask.png".format(file_name))

            # ocr结果暂存
            self.ocr_result_map[image_path] = ocr_result
            # 文字消除
            ipt_thread = utils.thread.createThread(self.mangaTextInpaint, image_path, ocr_result["mask"])

        # 提取ocr文本
        for val in self.ocr_result_map[image_path]["text_block"] :
            if not val["text"] :
                continue
            original = ""
            for text in val["text"] :
                original += text
            if not original:
                continue
            # 翻译
            if original not in self.trans_result_map :
                trans_result = self.mangaTrans(self.object.config["mangaTrans"], original)
                self.trans_result_map[original] = trans_result

        # 刷新文本列表框
        self.refreshTextListWidget(image_path)
        # 如果有文字消除线程, 就等待文字消除完成
        if "ipt_thread" in locals() :
            ipt_thread.join()

        # 漫画文字渲染
        if image_path not in self.rdr_result_map :
            self.mangaTextRdr(image_path)

            # 渲染好的图片加入译图列表框
            rdr_result = self.rdr_result_map[image_path]
            image = QImage.fromData(base64.b64decode(rdr_result))
            pixmap = QPixmap.fromImage(image)
            item = QListWidgetItem(image_path, self.new_image_widget)
            item.setIcon(QIcon(pixmap))
            item.setText(os.path.basename(image_path))
            self.new_image_widget.addItem(item)
            self.new_image_path_list.append(image_path)

            # 跳转到译图栏
            self.new_image_widget.setCurrentItem(item)
            self.new_images_button.click()


    # 漫画文字渲染
    def mangaTextRdr(self, image_path) :

        trans_list = []
        for val in self.ocr_result_map[image_path]["text_block"]:
            if not val["text"]:
                continue
            original = ""
            for text in val["text"]:
                original += text
            if not original:
                continue
            trans_list.append(self.trans_result_map[original])

        rdr_sign, result = translator.ocr.dango.mangaRDR(
            object=self.object,
            mask=self.ocr_result_map[image_path]["mask"],
            trans_list=trans_list,
            inpainted_image=self.ipt_result_map[image_path],
            text_block=self.ocr_result_map[image_path]["text_block"]
        )
        if not rdr_sign :
            # @TODO 补全出错逻辑
            return
        self.rdr_result_map[image_path] = result["rendered_image"]


    # 漫画文字消除
    def mangaTextInpaint(self, image_path, mask) :

        ipt_sign, result = translator.ocr.dango.mangaIPT(self.object, image_path, mask)
        if not ipt_sign :
            # @TODO 补全出错逻辑
            return
        self.ipt_result_map[image_path] = result["inpainted_image"]


    # 漫画翻译
    def mangaTrans(self, manga_trans, original) :

        result = "未选择翻译源, 无法完成翻译"
        if manga_trans == "私人-彩云翻译":
            result = translator.api.caiyun(sentence=original,
                                           token=self.object.config["caiyunAPI"],
                                           logger=self.logger)
        elif manga_trans == "私人-腾讯翻译":
            result = translator.api.tencent(sentence=original,
                                            secret_id=self.object.config["tencentAPI"]["Key"],
                                            secret_key=self.object.config["tencentAPI"]["Secret"],
                                            logger=self.logger)
        elif manga_trans == "私人-百度翻译":
            result = translator.api.baidu(sentence=original,
                                          app_id=self.object.config["baiduAPI"]["Key"],
                                          secret_key=self.object.config["baiduAPI"]["Secret"],
                                          logger=self.logger)
        elif manga_trans == "私人-ChatGPT翻译":
            result = translator.api.chatgpt(api_key=self.object.config["chatgptAPI"],
                                            language=self.object.config["language"],
                                            proxy=self.object.config["chatgptProxy"],
                                            content=self.object.translation_ui.original,
                                            logger=self.logger)
        return result


    # 获取工作目录
    def getDangoMangaPath(self, image_path) :

        # 获取漫画翻译缓存目录
        base_path = os.path.dirname(image_path)
        dango_manga_path = os.path.join(base_path, "dango_manga")
        # 如果目录不存在就创建工作缓存目录
        if not os.path.exists(dango_manga_path) :
            os.mkdir(dango_manga_path)
        # 如果目录不存在就创建工作缓存目录
        tmp_path = os.path.join(dango_manga_path, "tmp")
        if not os.path.exists(tmp_path) :
            os.mkdir(tmp_path)
        # 获取不带拓展名的文件名
        file_name = os.path.splitext(os.path.basename(image_path))[0]

        return dango_manga_path, file_name


    # 获取某张图对应的Json结果文件缓存路径
    def getJsonFilePath(self, image_path) :

        dango_manga_path, file_name = self.getDangoMangaPath(image_path)
        tmp_path = os.path.join(dango_manga_path, "tmp")
        file_path = os.path.join(tmp_path, "{}.json".format(file_name))

        return file_path


    # 获取某张图对应的mask结果文件缓存路径
    def getMaskFilePath(self, image_path) :

        dango_manga_path, file_name = self.getDangoMangaPath(image_path)
        tmp_path = os.path.join(dango_manga_path, "tmp")
        file_path = os.path.join(tmp_path, "{}_mask.png".format(file_name))

        return file_path


    # 获取某张图对应的文字消除结果文件缓存路径
    def getIptFilePath(self, image_path) :

        dango_manga_path, file_name = self.getDangoMangaPath(image_path)
        tmp_path = os.path.join(dango_manga_path, "tmp")
        file_path = os.path.join(tmp_path, "{}_ipt.png".format(file_name))

        return file_path


    # 获取某张图对应的文字渲染结果文件缓存路径
    def getrdrFilePath(self, image_path) :

        dango_manga_path, file_name = self.getDangoMangaPath(image_path)
        file_path = os.path.join(dango_manga_path, "{}.png".format(file_name))

        return file_path


    # 窗口关闭处理
    def closeEvent(self, event) :

        self.hide()
        self.object.translation_ui.show()
        if self.object.range_ui.show_sign == True:
            self.object.range_ui.show()