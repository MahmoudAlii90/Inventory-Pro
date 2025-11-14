import os
import json


class SettingsManager:
    def __init__(self, path="settings.json"):
        self.path = path
        self.default_settings = {
            "company_name": "Company Name",
            "company_address": "",
            "company_phone": "",
            "company_email": "",
            "logo_path": "",
            "backup_path": "",
            "auto_backup": False,
            "auto_backup_interval": 24,   # بالساعات
        }

    # ============================================================
    #  LOAD SETTINGS
    # ============================================================
    def load(self):
        """Loads settings.json or creates a default one."""
        if not os.path.exists(self.path):
            self.save(self.default_settings)
            return self.default_settings

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # تأكيد وجود كل القيم
            for key, val in self.default_settings.items():
                if key not in settings:
                    settings[key] = val

            return settings

        except Exception as e:
            print(f"Settings load error: {e}")
            return self.default_settings

    # ============================================================
    #  SAVE SETTINGS
    # ============================================================
    def save(self, settings: dict):
        """Saves updated settings to file."""
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Settings save error: {e}")

    # ============================================================
    #  UPDATE SINGLE FIELD
    # ============================================================
    def update(self, key, value):
        """Updates only one setting field."""
        settings = self.load()
        settings[key] = value
        self.save(settings)

    # ============================================================
    #  GET VALUE
    # ============================================================
    def get(self, key, default=None):
        settings = self.load()
        return settings.get(key, default)
