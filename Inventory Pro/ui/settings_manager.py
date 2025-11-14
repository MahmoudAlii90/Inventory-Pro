import os
import json


class SettingsManager:
    def __init__(self, file_path="settings.json"):
        self.file_path = file_path

        # لو الملف مش موجود نعمل واحد جديد
        if not os.path.exists(self.file_path):
            self.create_default_settings()

    # ======================= إنشاء إعدادات افتراضية =======================
    def create_default_settings(self):
        default_settings = {
            "company_name": "My Company",
            "logo_path": "",
            "backup_path": "",
            "auto_backup": False,
            "auto_backup_interval": 24  # ساعات
        }

        self.save(default_settings)

    # ======================= تحميل الإعدادات =======================
    def load(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            self.create_default_settings()
            return self.load()

    # ======================= حفظ الإعدادات =======================
    def save(self, settings_dict):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(settings_dict, f, ensure_ascii=False, indent=4)
