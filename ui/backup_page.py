import os
import zipfile
from datetime import datetime, timedelta
from PyQt5 import QtWidgets, QtCore
from utils.settings_manager import SettingsManager
from ui.global_signals import global_signals


class BackupPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.permissions = permissions
        self.settings = SettingsManager()
        self.current_settings = self.settings.load()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.auto_backup_check)

        self.build_ui()

        # تشغيل الـ Scheduler تلقائياً
        self.start_auto_scheduler()

    # ============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("🛡 النسخ الاحتياطي وإدارة ملفات النظام")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0A3D91;
            margin-bottom: 15px;
        """)
        layout.addWidget(title)

        # ------------------- مسار النسخ الاحتياطي -------------------
        form = QtWidgets.QFormLayout()

        self.lbl_path = QtWidgets.QLabel(self.current_settings.get("backup_path", "غير محدد"))
        btn_change = QtWidgets.QPushButton("📁 اختيار مسار")
        btn_change.clicked.connect(self.change_backup_path)

        h_path = QtWidgets.QHBoxLayout()
        h_path.addWidget(self.lbl_path)
        h_path.addWidget(btn_change)
        form.addRow("📂 مسار النسخ الاحتياطي:", h_path)

        # ------------------- النسخ التلقائي -------------------
        self.chk_auto = QtWidgets.QCheckBox("تفعيل النسخ الاحتياطي التلقائي")
        self.chk_auto.setChecked(self.current_settings.get("auto_backup", False))
        form.addRow("⚡ النسخ التلقائي:", self.chk_auto)

        # مدة النسخ التلقائي
        self.spin_interval = QtWidgets.QSpinBox()
        self.spin_interval.setRange(1, 168)  # حد أقصى 7 أيام
        self.spin_interval.setValue(self.current_settings.get("auto_backup_interval", 24))
        form.addRow("⏳ كل (ساعات):", self.spin_interval)

        layout.addLayout(form)

        # ------------------- زر النسخ اليدوي -------------------
        btn_manual = QtWidgets.QPushButton("💾 إنشاء نسخة احتياطية الآن")
        btn_manual.setStyleSheet("font-size:18px; padding:8px;")
        btn_manual.clicked.connect(self.manual_backup)
        layout.addWidget(btn_manual)

        layout.addStretch()

    # ============================================================
    def change_backup_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "اختر مجلد النسخ الاحتياطي")
        if path:
            self.current_settings["backup_path"] = path
            self.lbl_path.setText(path)
            self.settings.update("backup_path", path)

    # ============================================================
    def manual_backup(self):
        """إنشاء نسخة احتياطية الآن — يدوي"""
        try:
            path = self.current_settings.get("backup_path", "")
            if not path:
                QtWidgets.QMessageBox.warning(self, "خطأ", "لم يتم تحديد مسار النسخ الاحتياطي.")
                return

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"backup_{timestamp}.zip"
            backup_file = os.path.join(path, filename)

            with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                if os.path.exists("database.db"):
                    zipf.write("database.db")

                if os.path.exists("settings.json"):
                    zipf.write("settings.json")

                # تضمين جميع الفواتير
                if os.path.exists("invoices"):
                    for root, _, files in os.walk("invoices"):
                        for f in files:
                            full = os.path.join(root, f)
                            arc = os.path.relpath(full, "invoices")
                            zipf.write(full, f"invoices/{arc}")

            QtWidgets.QMessageBox.information(self, "✔ نجاح", "تم إنشاء النسخة الاحتياطية بنجاح.")
            global_signals.data_changed.emit()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "خطأ", f"تعذر إنشاء النسخة:\n{e}")

    # ============================================================
    # AUTO BACKUP SCHEDULER
    # ============================================================
    def start_auto_scheduler(self):
        """تشغيل السكينة — تنتظر الوقت وتعمل Backup تلقائي"""
        if not self.current_settings.get("auto_backup", False):
            return

        hours = self.current_settings.get("auto_backup_interval", 24)
        interval_ms = hours * 60 * 60 * 1000

        self.timer.start(interval_ms)

    # ============================================================
    def auto_backup_check(self):
        """ينفذ نسخ احتياطي تلقائي عند انتهاء المدة"""
        if not self.chk_auto.isChecked():
            return

        self.manual_backup()

        # إعادة ضبط المؤقت مرّة أخرى
        self.start_auto_scheduler()
