import os
import shutil
from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox

from utils.settings_manager import SettingsManager
from utils.db_manager import DatabaseManager


class AutoBackupScheduler(QtCore.QObject):
    backup_done = QtCore.pyqtSignal(str)     # إشعار بعد النسخ

    def __init__(self):
        super().__init__()

        self.settings = SettingsManager()
        self.db = DatabaseManager()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.perform_backup)

        self.load_settings_and_start()

    # ==========================================================
    def load_settings_and_start(self):
        auto = self.settings.get("auto_backup", False)
        interval = self.settings.get("backup_interval", "none")
        path = self.settings.get("backup_path", "")

        if not auto or interval == "none" or not path:
            self.timer.stop()
            return

        minutes = {
            "1h": 60,
            "6h": 360,
            "12h": 720,
            "1d": 1440,
            "1w": 10080
        }.get(interval, 0)

        if minutes > 0:
            self.timer.start(minutes * 60 * 1000)  # تحويل لملي ثانية

    # ==========================================================
    def perform_backup(self):
        try:
            backup_dir = self.settings.get("backup_path", "")
            if not backup_dir:
                return

            # ملف قاعدة البيانات
            src = "database.db"
            if not os.path.exists(src):
                return

            # مجلد AutoBackups داخل المسار
            folder_path = os.path.join(backup_dir, "AutoBackups")
            os.makedirs(folder_path, exist_ok=True)

            # اسم النسخة
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            dst = os.path.join(folder_path, f"backup_{timestamp}.db")

            shutil.copy2(src, dst)

            # سجل النشاط
            self.db.add_log("Auto-Backup", "نسخ تلقائي", "النظام", dst)

            # إشعار
            self.backup_done.emit(dst)

        except Exception as e:
            print("AutoBackup Error:", e)
