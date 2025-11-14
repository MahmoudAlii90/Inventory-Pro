import os
import json
from PyQt5 import QtWidgets, QtGui, QtCore

CONFIG_FILE = "config.json"

class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ إعدادات النظام")
        self.setFixedSize(480, 280)
        self.setStyleSheet("""
            QDialog {
                background-color: #E8EEF7;
                font-family: 'Cairo';
            }
            QLabel {
                color: #0A3D91;
                font-weight: bold;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #0A3D91;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #0A3D91;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #257CFF;
            }
        """)

        layout = QtWidgets.QVBoxLayout()

        # ---- اسم الشركة ----
        lbl_company = QtWidgets.QLabel("🏢 اسم الشركة:")
        self.company_name = QtWidgets.QLineEdit()
        self.company_name.setPlaceholderText("اكتب اسم الشركة هنا")

        # ---- شعار الشركة ----
        lbl_logo = QtWidgets.QLabel("🖼️ شعار الشركة:")
        self.logo_path = QtWidgets.QLineEdit()
        self.logo_path.setPlaceholderText("مسار صورة الشعار (PNG أو JPG)")
        btn_browse = QtWidgets.QPushButton("📁 اختيار شعار")
        btn_browse.clicked.connect(self.choose_logo)

        logo_layout = QtWidgets.QHBoxLayout()
        logo_layout.addWidget(self.logo_path)
        logo_layout.addWidget(btn_browse)

        # ---- زر الحفظ ----
        btn_save = QtWidgets.QPushButton("💾 حفظ الإعدادات")
        btn_save.clicked.connect(self.save_config)

        layout.addWidget(lbl_company)
        layout.addWidget(self.company_name)
        layout.addSpacing(15)
        layout.addWidget(lbl_logo)
        layout.addLayout(logo_layout)
        layout.addStretch()
        layout.addWidget(btn_save)

        self.setLayout(layout)
        self.load_config()

    # =====================================
    # اختيار الشعار
    # =====================================
    def choose_logo(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "اختر لوجو الشركة", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.logo_path.setText(file_path)

    # =====================================
    # تحميل الإعدادات من config.json
    # =====================================
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.company_name.setText(cfg.get("company_name", ""))
                self.logo_path.setText(cfg.get("logo_path", ""))
            except Exception as e:
                print("خطأ أثناء تحميل الإعدادات:", e)

    # =====================================
    # حفظ الإعدادات في config.json
    # =====================================
    def save_config(self):
        data = {
            "company_name": self.company_name.text(),
            "logo_path": self.logo_path.text()
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        QtWidgets.QMessageBox.information(self, "تم", "✅ تم حفظ الإعدادات بنجاح")
        self.close()
