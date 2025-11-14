from PyQt5 import QtWidgets, QtGui, QtCore
from utils.db_manager import DatabaseManager
from utils.settings_manager import SettingsManager


class LoginWindow(QtWidgets.QWidget):
    login_success = QtCore.pyqtSignal(str, str, dict)

    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.settings = SettingsManager()

        self.setWindowTitle("Inventory Pro – تسجيل الدخول")
        self.resize(520, 420)

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0A0F1F,
                    stop:1 #1A2337
                );
                font-family: Cairo;
            }
        """)

        self.build_ui()

    # ===============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # ---------------- Glass Panel ----------------
        box = QtWidgets.QFrame()
        box.setFixedSize(380, 330)
        box.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.08);
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.2);
                backdrop-filter: blur(25px);
            }
        """)
        vbox = QtWidgets.QVBoxLayout(box)
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(box)

        # ---------------- Company Logo ----------------
        logo = QtWidgets.QLabel()
        logo.setAlignment(QtCore.Qt.AlignCenter)
        logo.setFixedHeight(70)

        if self.settings.get("logo_path") and self.settings.get("logo_path") != "":
            pix = QtGui.QPixmap(self.settings.get("logo_path")).scaled(
                90, 60, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
            logo.setPixmap(pix)
        else:
            logo.setText("Inventory Pro")
            logo.setStyleSheet("color:white; font-size:22px; font-weight:bold;")

        vbox.addWidget(logo)

        # ---------------- Username ----------------
        self.user = QtWidgets.QLineEdit()
        self.user.setPlaceholderText("اسم المستخدم")
        self.user.setStyleSheet(self.input_style())
        vbox.addWidget(self.user)

        # ---------------- Password ----------------
        self.password = QtWidgets.QLineEdit()
        self.password.setPlaceholderText("كلمة المرور")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setStyleSheet(self.input_style())
        vbox.addWidget(self.password)

        # ---------------- Login Button ----------------
        btn = QtWidgets.QPushButton("تسجيل الدخول")
        btn.clicked.connect(self.try_login)
        btn.setStyleSheet(self.button_style())
        vbox.addWidget(btn)

        # ---------------- Error Message ----------------
        self.error_lbl = QtWidgets.QLabel("")
        self.error_lbl.setStyleSheet("color:#FF6B6B; font-size:13px; font-weight:bold;")
        self.error_lbl.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(self.error_lbl)

    # ===============================================================
    def input_style(self):
        return """
        QLineEdit {
            padding: 10px;
            font-size: 14px;
            color: white;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.4);
            background: rgba(255,255,255,0.08);
        }
        QLineEdit:focus {
            border: 1px solid #4FC3F7;
            background: rgba(255,255,255,0.15);
            color:white;
        }
        """

    # ===============================================================
    def button_style(self):
        return """
        QPushButton {
            background-color: #1565C0;
            color: white;
            padding: 12px;
            font-size: 15px;
            border-radius: 10px;
            font-weight:bold;
        }
        QPushButton:hover {
            background-color: #1E88E5;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        """

    # ===============================================================
    def try_login(self):
        username = self.user.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            self.error_lbl.setText("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
            return

        user = self.db.validate_user(username, password)

        if not user:
            self.error_lbl.setText("❌ بيانات الدخول غير صحيحة")
            return

        # نجاح
        self.error_lbl.setText("")
        self.login_success.emit(user["username"], user["role"], user["permissions"])
