from PyQt5 import QtWidgets, QtGui, QtCore

from utils.db_manager import DatabaseManager
from utils.report_utils import ReportUtils


class TransactionsPage(QtWidgets.QWidget):
    def __init__(self, username, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.username = username
        self.permissions = permissions.get("transactions", {"view": 1})

        self.reporter = ReportUtils()

        self.transactions = []

        self.build_ui()
        self.load_transactions()

    # ===============================================================
    # BUILD UI
    # ===============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("🧾 الأذونات (عمليات المخزون)")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Cairo", 20, QtGui.QFont.Bold))
        title.setStyleSheet("color:#0A3D91; margin-bottom:15px;")
        layout.addWidget(title)

        if not self.permissions.get("view"):
            layout.addWidget(QtWidgets.QLabel("🚫 ليس لديك صلاحية عرض الأذونات"))
            return

        # ---------------- FILTER BAR ----------------
        filter_layout = QtWidgets.QHBoxLayout()

        # Date Filters
        self.date_from = QtWidgets.QDateEdit(calendarPopup=True)
        self.date_to = QtWidgets.QDateEdit(calendarPopup=True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDisplayFormat("yyyy-MM-dd")

        self.date_from.setDate(QtCore.QDate.currentDate().addDays(-7))
        self.date_to.setDate(QtCore.QDate.currentDate())

        # Type filter
        self.type_filter = QtWidgets.QComboBox()
        self.type_filter.addItems(["الكل", "صرف", "استلام", "تحويل"])

        # Search box
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("بحث... (الصنف، المستخدم، ملاحظات...)")

        btn_filter = QtWidgets.QPushButton("🔍 بحث")
        btn_filter.clicked.connect(self.apply_filters)

        filter_layout.addWidget(QtWidgets.QLabel("من:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QtWidgets.QLabel("إلى:"))
        filter_layout.addWidget(self.date_to)

        filter_layout.addWidget(QtWidgets.QLabel("النوع:"))
        filter_layout.addWidget(self.type_filter)

        filter_layout.addWidget(self.search_box)
        filter_layout.addWidget(btn_filter)

        filter_layout.addStretch()

        # EXPORT BUTTONS
        btn_pdf = QtWidgets.QPushButton("📄 PDF")
        btn_excel = QtWidgets.QPushButton("📊 Excel")
        btn_print = QtWidgets.QPushButton("🖨️ طباعة")

        btn_pdf.clicked.connect(self.export_pdf)
        btn_excel.clicked.connect(self.export_excel)
        btn_print.clicked.connect(self.print_report)

        filter_layout.addWidget(btn_pdf)
        filter_layout.addWidget(btn_excel)
        filter_layout.addWidget(btn_print)

        layout.addLayout(filter_layout)

        # ---------------- TABLE ----------------
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["ID", "النوع", "الصنف", "الكمية", "من مخزن", "إلى مخزن", "المستخدم", "ملاحظات", "التاريخ"]
        )

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        layout.addWidget(self.table)

    # ===============================================================
    # LOAD TRANSACTIONS
    # ===============================================================
    def load_transactions(self):
        self.transactions = self.db.get_transactions()
        self.refresh_table(self.transactions)

    # ===============================================================
    def refresh_table(self, data):
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(row["type"]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(row["item"]))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(row["quantity"])))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(row.get("from_wh", "")))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(row.get("to_wh", "")))
            self.table.setItem(i, 6, QtWidgets.QTableWidgetItem(row["user"]))
            self.table.setItem(i, 7, QtWidgets.QTableWidgetItem(row["notes"]))
            self.table.setItem(i, 8, QtWidgets.QTableWidgetItem(row["date"]))

    # ===============================================================
    # FILTER
    # ===============================================================
    def apply_filters(self):
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        type_filter = self.type_filter.currentText()
        search = self.search_box.text().strip()

        filtered = []

        for t in self.transactions:
            date_val = t["date"][:10]

            if not (date_from <= date_val <= date_to):
                continue

            if type_filter != "الكل" and t["type"] != type_filter:
                continue

            if search:
                if search not in t["item"] and search not in t["user"] and search not in t["notes"]:
                    continue

            filtered.append(t)

        self.refresh_table(filtered)

    # ===============================================================
    # EXPORT PDF
    # ===============================================================
    def export_pdf(self):
        items = self.collect_current_table()
        if not items:
            QtWidgets.QMessageBox.warning(self, "خطأ", "لا توجد بيانات للتصدير")
            return

        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")

        file_path = self.reporter.export_pdf(
            data_list=items,
            columns=["id", "type", "item", "quantity", "from_wh", "to_wh", "user", "notes", "date"],
            filename="transactions_report",
            report_title="Transactions Report",
            date_from=date_from,
            date_to=date_to
        )

        QtWidgets.QMessageBox.information(self, "✔", f"تم إنشاء PDF:\n{file_path}")

    # ===============================================================
    # EXPORT EXCEL
    # ===============================================================
    def export_excel(self):
        items = self.collect_current_table()
        if not items:
            QtWidgets.QMessageBox.warning(self, "خطأ", "لا توجد بيانات للتصدير")
            return

        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")

        file_path = self.reporter.export_excel(
            data_list=items,
            columns=["id", "type", "item", "quantity", "from_wh", "to_wh", "user", "notes", "date"],
            filename="transactions_report",
            report_title="Transactions Report",
            date_from=date_from,
            date_to=date_to
        )

        QtWidgets.QMessageBox.information(self, "✔", f"تم حفظ ملف Excel:\n{file_path}")

    # ===============================================================
    # PRINT
    # ===============================================================
    def print_report(self):
        self.reporter.print_report(self.table)

    # ===============================================================
    # Convert Table to List of Dicts
    # ===============================================================
    def collect_current_table(self):
        data = []

        rows = self.table.rowCount()
        cols = self.table.columnCount()

        headers = ["id", "type", "item", "quantity", "from_wh",
                   "to_wh", "user", "notes", "date"]

        for r in range(rows):
            entry = {}
            for c in range(cols):
                item = self.table.item(r, c)
                entry[headers[c]] = item.text() if item else ""
            data.append(entry)

        return data
