from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from utils.export_utils import Exporter
from ui.global_signals import global_signals


class ActivityLogPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions
        self.data = []

        self.build_ui()
        self.load_logs()

        global_signals.data_changed.connect(self.load_logs)

    # ======================================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("📝 سجل النشاطات — Activity Log")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
            color:#0A3D91;
            margin-bottom:20px;
        """)
        layout.addWidget(title)

        # ======================================================================
        # FILTERS
        # ======================================================================
        filter_box = QtWidgets.QGroupBox("🔍 فلترة النشاطات")
        f = QtWidgets.QGridLayout(filter_box)

        # -------- Users --------
        self.cbo_user = QtWidgets.QComboBox()
        self.cbo_user.addItem("الكل")
        for u in self.db.get_users():
            self.cbo_user.addItem(u["username"])
        f.addWidget(QtWidgets.QLabel("المستخدم:"), 0, 0)
        f.addWidget(self.cbo_user, 0, 1)

        # -------- Section --------
        self.cbo_section = QtWidgets.QComboBox()
        self.cbo_section.addItems(["الكل", "items", "purchases", "sales", "warehouses",
                                   "partners", "transactions", "users", "roles",
                                   "settings", "backup", "reports"])
        f.addWidget(QtWidgets.QLabel("القسم:"), 1, 0)
        f.addWidget(self.cbo_section, 1, 1)

        # -------- Action --------
        self.cbo_action = QtWidgets.QComboBox()
        self.cbo_action.addItems(["الكل", "إضافة", "تعديل", "حذف", "تصدير", "طباعة", "تسجيل دخول"])
        f.addWidget(QtWidgets.QLabel("الإجراء:"), 2, 0)
        f.addWidget(self.cbo_action, 2, 1)

        # -------- Date From --------
        self.date_from = QtWidgets.QDateEdit(QtCore.QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)

        self.date_to = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.date_to.setCalendarPopup(True)

        f.addWidget(QtWidgets.QLabel("من:"), 3, 0)
        f.addWidget(self.date_from, 3, 1)
        f.addWidget(QtWidgets.QLabel("إلى:"), 4, 0)
        f.addWidget(self.date_to, 4, 1)

        # -------- Search Text --------
        self.txt_search = QtWidgets.QLineEdit()
        self.txt_search.setPlaceholderText("بحث...")
        self.txt_search.textChanged.connect(self.filter_search)

        f.addWidget(QtWidgets.QLabel("بحث:"), 5, 0)
        f.addWidget(self.txt_search, 5, 1)

        # -------- Filter Button --------
        btn_filter = QtWidgets.QPushButton("🔎 تطبيق الفلتر")
        btn_filter.clicked.connect(self.apply_filters)
        f.addWidget(btn_filter, 6, 0, 1, 2)

        layout.addWidget(filter_box)

        # ======================================================================
        # TABLE
        # ======================================================================
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["المستخدم", "الإجراء", "القسم", "تفاصيل", "الوقت"])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # ======================================================================
        # EXPORT BUTTONS
        # ======================================================================
        btns = QtWidgets.QHBoxLayout()

        btn_excel = QtWidgets.QPushButton("📘 Excel")
        btn_excel.clicked.connect(self.export_excel)

        btn_pdf = QtWidgets.QPushButton("📕 PDF")
        btn_pdf.clicked.connect(self.export_pdf)

        btn_print = QtWidgets.QPushButton("🖨 طباعة")
        btn_print.clicked.connect(self.print_report)

        btns.addWidget(btn_excel)
        btns.addWidget(btn_pdf)
        btns.addWidget(btn_print)
        layout.addLayout(btns)

    # ======================================================================
    def load_logs(self):
        self.data = self.db.get_logs()
        self.fill_table(self.data)

    # ======================================================================
    def fill_table(self, logs):
        self.table.setRowCount(len(logs))

        for i, log in enumerate(logs):
            row_color = QtGui.QColor("#F8F9FC")

            if "حذف" in log["action"]:
                row_color = QtGui.QColor("#FFE5E5")
            elif "تعديل" in log["action"]:
                row_color = QtGui.QColor("#FFF6D8")
            elif "إضافة" in log["action"]:
                row_color = QtGui.QColor("#E9FFE8")

            for col, key in enumerate(["user", "action", "section", "details", "timestamp"]):
                item = QtWidgets.QTableWidgetItem(str(log[key]))
                item.setBackground(row_color)
                self.table.setItem(i, col, item)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    # ======================================================================
    def apply_filters(self):
        user = self.cbo_user.currentText()
        section = self.cbo_section.currentText()
        action = self.cbo_action.currentText()

        start = self.date_from.date().toString("yyyy-MM-dd")
        end = self.date_to.date().toString("yyyy-MM-dd")

        filtered = []
        for log in self.db.get_logs():

            if user != "الكل" and log["user"] != user:
                continue

            if section != "الكل" and log["section"] != section:
                continue

            if action != "الكل" and action not in log["action"]:
                continue

            if not (start <= log["timestamp"][:10] <= end):
                continue

            filtered.append(log)

        self.data = filtered
        self.fill_table(filtered)

    # ======================================================================
    def filter_search(self):
        text = self.txt_search.text().strip()

        filtered = [
            x for x in self.data
            if text in x["user"] or text in x["action"] or text in x["details"]
        ]

        self.fill_table(filtered)

    # ======================================================================
    def export_excel(self):
        if not self.data:
            QtWidgets.QMessageBox.warning(self, "❌", "لا يوجد بيانات للتصدير")
            return

        Exporter().export_excel(self.data, "Activity_Log")
        QtWidgets.QMessageBox.information(self, "✔", "تم التصدير إلى Excel.")

    # ======================================================================
    def export_pdf(self):
        if not self.data:
            QtWidgets.QMessageBox.warning(self, "❌", "لا يوجد بيانات للتصدير")
            return

        Exporter().export_pdf(self.data, "Activity_Log")
        QtWidgets.QMessageBox.information(self, "✔", "تم إنشاء ملف PDF.")

    # ======================================================================
    def print_report(self):
        if not self.data:
            QtWidgets.QMessageBox.warning(self, "❌", "لا يوجد بيانات للطباعة")
            return

        printer = QtWidgets.QPrinter()
        dialog = QtWidgets.QPrintDialog(printer)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            self.table.render(painter)
            painter.end()

            QtWidgets.QMessageBox.information(self, "✔", "تمت الطباعة بنجاح.")
