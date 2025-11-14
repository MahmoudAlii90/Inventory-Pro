import os
import json
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore

from utils.settings_manager import SettingsManager
from utils.backup_manager import AutoBackupScheduler


class SettingsPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.permissions = permissions.get("settings", {"view":1, "edit":1})
        self.settings = SettingsManager()

        self.build_ui()

    # ===============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("⚙️ إعدادات النظام")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Cairo", 20, QtGui.QFont.Bold))
        title.setStyleSheet("color:#4FC3F7; margin-bottom:20px;")
        layout.addWidget(title)

        form = QtWidgets.QFormLayout()

        # اسم الشركة
        self.input_name = QtWidgets.QLineEdit(self.settings.get("company_name", ""))
        form.addRow("اسم الشركة:", self.input_name)

        # اللوجو
        logo_layout = QtWidgets.QHBoxLayout()
        self.lbl_logo = QtWidgets.QLabel(self.settings.get("logo_path", "—"))
        btn_logo = QtWidgets.QPushButton("📁 اختيار لوجو")
        btn_logo.clicked.connect(self.pick_logo)
        logo_layout.addWidget(self.lbl_logo)
        logo_layout.addWidget(btn_logo)
        form.addRow("لوجو الشركة:", logo_layout)

        # -------- BACKUP PATH --------
        backup_layout = QtWidgets.QHBoxLayout()
        self.lbl_backup_path = QtWidgets.QLabel(self.settings.get("backup_path", "غير محدد"))
        btn_backup = QtWidgets.QPushButton("📁 اختيار مسار")
        btn_backup.clicked.connect(self.pick_backup_path)
        backup_layout.addWidget(self.lbl_backup_path)
        backup_layout.addWidget(btn_backup)
        form.addRow("مسار النسخ الاحتياطي:", backup_layout)

        # -------- AUTOBACKUP SWITCH --------
        self.check_auto = QtWidgets.QCheckBox("تفعيل النسخ التلقائي")
        self.check_auto.setChecked(self.settings.get("auto_backup", False))
        form.addRow("نسخ تلقائي:", self.check_auto)

        # -------- BACKUP INTERVAL --------
        self.combo_interval = QtWidgets.QComboBox()
        self.combo_interval.addItems(["none", "1h", "6h", "12h", "1d", "1w"])
        self.combo_interval.setCurrentText(self.settings.get("backup_interval", "none"))
        form.addRow("التكرار:", self.combo_interval)

        layout.addLayout(form)

        # -------------------- Buttons --------------------
        btn_manual = QtWidgets.QPushButton("💾 نسخ احتياطي يدوي")
        btn_manual.clicked.connect(self.manual_backup)

        btn_restore = QtWidgets.QPushButton("♻️ استعادة نسخة")
        btn_restore.clicked.connect(self.restore_backup)

        btn_save = QtWidgets.QPushButton("✔ حفظ الإعدادات")
        btn_save.clicked.connect(self.save_settings)

        layout.addWidget(btn_manual)
        layout.addWidget(btn_restore)
        layout.addWidget(btn_save)

    # -------------------- Pick logo --------------------
    def pick_logo(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "اختر لوجو", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self.lbl_logo.setText(path)

    # -------------------- Pick backup folder --------------------
    def pick_backup_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "اختر مجلد النسخ الاحتياطي"
        )
        if path:
            self.lbl_backup_path.setText(path)

    # ============================================================
    def save_settings(self):
        self.settings.set("company_name", self.input_name.text().strip())
        self.settings.set("logo_path", self.lbl_logo.text())
        self.settings.set("backup_path", self.lbl_backup_path.text())
        self.settings.set("auto_backup", self.check_auto.isChecked())
        self.settings.set("backup_interval", self.combo_interval.currentText())

        QtWidgets.QMessageBox.information(self, "✔", "تم حفظ الإعدادات بنجاح.")

        # إعادة تشغيل المؤقت
        AutoBackupScheduler().load_settings_and_start()

    # ============================================================
    def manual_backup(self):
        import shutil

        backup_dir = self.lbl_backup_path.text()
        if "غير" in backup_dir:
            QtWidgets.QMessageBox.warning(self, "❌", "اختر مسار النسخ أولًا.")
            return

        src = "database.db"
        name = f"manual_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.db"
        dst = os.path.join(backup_dir, name)

        try:
            shutil.copy2(src, dst)
            QtWidgets.QMessageBox.information(self, "✔", f"تم إنشاء النسخة:\n{dst}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "❌ خطأ", str(e))

    # ============================================================
    def restore_backup(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "اختر النسخة الاحتياطية", "", "DB Files (*.db)"
        )
        if not path:
            return

        try:
            import shutil
            shutil.copy2(path, "database.db")

            QtWidgets.QMessageBox.information(
                self, "✔", "تم استعادة النسخة.\nأعد تشغيل البرنامج."
            )

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "❌", str(e))
