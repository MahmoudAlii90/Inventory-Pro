# utils/global_signals.py

from PyQt5 import QtCore


class GlobalSignals(QtCore.QObject):
    # إشارة تحدث عند تغيير البيانات (إضافة، حذف، تعديل)
    data_changed = QtCore.pyqtSignal()

    # إشارة تحديث للداشبورد فقط
    dashboard_update = QtCore.pyqtSignal()

    # إشارة لحفظ الإعدادات
    settings_saved = QtCore.pyqtSignal()

    # إشارة لتحديث الصلاحيات في الواجهة
    permissions_updated = QtCore.pyqtSignal()


# كائن واحد عالمي يتم استيراده في كل الصفحات
global_signals = GlobalSignals()
