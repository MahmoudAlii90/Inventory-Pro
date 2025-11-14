import sys
from PyQt5 import QtWidgets

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from utils.db_manager import DatabaseManager


class InventoryApp(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.db = DatabaseManager()
        self.main_window = None

        # فتح شاشة تسجيل الدخول
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.start_main_app)
        self.login_window.show()

    # -------------------------------------------------------------
    def start_main_app(self, username, role, permissions):
        # غلق شاشة تسجيل الدخول
        self.login_window.close()

        # فتح الشاشة الرئيسية
        self.main_window = MainWindow(username, role, permissions)
        self.main_window.logout_requested.connect(self.show_login_again)
        self.main_window.showMaximized()

    # -------------------------------------------------------------
    def show_login_again(self):
        # الرجوع لصفحة تسجيل الدخول بعد تسجيل خروج
        if self.main_window:
            self.main_window.close()

        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.start_main_app)
        self.login_window.show()


# -------------------------------------------------------------
if __name__ == "__main__":
    app = InventoryApp(sys.argv)
    sys.exit(app.exec_())
