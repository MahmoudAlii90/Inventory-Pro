from PyQt5.QtCore import QObject, pyqtSignal

class GlobalSignals(QObject):
    # إشارة عامة تُرسل عند أي تغيير في البيانات
    data_changed = pyqtSignal()

# كائن عالمي يستخدمه كل الصفحات
global_signals = GlobalSignals()
