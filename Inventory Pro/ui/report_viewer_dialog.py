from PyQt5 import QtWidgets, QtGui, QtCore
from utils.db_manager import DatabaseManager
from utils.report_utils import ReportUtils


class ReportViewerDialog(QtWidgets.QDialog):
    def __init__(self, report_key):
        super().__init__()

        self.db = DatabaseManager()
        self.reporter = ReportUtils()
        self.report_key = report_key

        self.setWindowTitle("📄 عرض التقرير")
        self.setMinimumSize(900, 600)

        self.setStyleSheet("""
            QDialog {
                background-color: #0D0F12;
                color: white;
                font-family: Cairo;
            }
            QPushButton {
                background-color: #1E90FF;
                color: white;
                font-size: 14px;
                padding: 6px 14px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #4FC3F7;
            }
            QLineEdit, QDateEdit {
                padding: 4px;
                border-radius: 6px;
                border: 1px solid #455A64;
                background-color: #1A1C20;
                color: #E0E0E0;
            }
            QTableWidget {
                background-color: #1A1C20;
                color: white;
            }
            QHeaderView::section {
                background-color: #263238;
                color: #BBDEFB;
                padding: 5px;
            }
        """)

        self.build_ui()
        self.load_data()

    # =================================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel(self.get_title())
        title.setStyleSheet("font-size:22px; font-weight:bold; color:#4FC3F7; margin-bottom:10px;")
        layout.addWidget(title)

        # ---------------- Filters ----------------
        filters = QtWidgets.QHBoxLayout()

        self.date_from = QtWidgets.QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QtCore.QDate.currentDate().addMonths(-1))

        self.date_to = QtWidgets.QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QtCore.QDate.currentDate())

        self.txt_search = QtWidgets.QLineEdit()
        self.txt_search.setPlaceholderText("بحث...")

        btn_filter = QtWidgets.QPushButton("🔍 بحث")
        btn_filter.clicked.connect(self.filter_data)

        btn_pdf = QtWidgets.QPushButton("📄 PDF")
        btn_pdf.clicked.connect(self.export_pdf)

        btn_excel = QtWidgets.QPushButton("📊 Excel")
        btn_excel.clicked.connect(self.export_excel)

        btn_print = QtWidgets.QPushButton("🖨️ طباعة")
        btn_print.clicked.connect(self.print_report)

        filters.addWidget(QtWidgets.QLabel("من:"))
        filters.addWidget(self.date_from)
        filters.addWidget(QtWidgets.QLabel("إلى:"))
        filters.addWidget(self.date_to)
        filters.addWidget(self.txt_search)
        filters.addWidget(btn_filter)
        filters.addWidget(btn_pdf)
        filters.addWidget(btn_excel)
        filters.addWidget(btn_print)

        layout.addLayout(filters)

        # ---------------- Table ----------------
        self.table = QtWidgets.QTableWidget()
        layout.addWidget(self.table)

    # =================================================================
    def get_title(self):
        titles = {
            "items": "📦 تقرير الأصناف",
            "warehouses": "🏭 تقرير المخازن",
            "suppliers": "🤝 تقرير الموردين",
            "customers": "👥 تقرير العملاء",
            "transactions": "📝 تقرير الأذونات",
            "low_stock": "⚠️ تقرير المخزون المنخفض"
        }
        return titles.get(self.report_key, "Report")

    # =================================================================
    def load_data(self):
        # Load the detailed data model (best option B)
        if self.report_key == "items":
            self.data = self.db.get_items()
            headers = ["id", "name", "sku", "quantity", "min_quantity", "warehouse"]
        elif self.report_key == "warehouses":
            self.data = self.db.get_warehouses()
            headers = ["id", "name", "location"]
        elif self.report_key == "suppliers":
            self.data = self.db.get_suppliers()
            headers = ["id", "name", "phone", "address"]
        elif self.report_key == "customers":
            self.data = self.db.get_customers()
            headers = ["id", "name", "phone", "address"]
        elif self.report_key == "transactions":
            self.data = self.db.get_transactions()
            headers = ["id", "type", "item", "quantity", "from_wh", "to_wh", "user", "date", "notes"]
        elif self.report_key == "low_stock":
            items = self.db.get_items()
            self.data = [i for i in items if i["quantity"] <= i["min_quantity"]]
            headers = ["name", "quantity", "min_quantity", "warehouse"]
        else:
            self.data = []
            headers = []

        self.headers = headers
        self.refresh_table(self.data)

    # =================================================================
    def refresh_table(self, rows):
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, h in enumerate(self.headers):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(row.get(h, ""))))

    # =================================================================
    def filter_data(self):
        text = self.txt_search.text().strip()

        filtered = []
        for row in self.data:
            if text.lower() in str(row).lower():
                filtered.append(row)

        self.refresh_table(filtered)

    # =================================================================
    def export_pdf(self):
        path = self.reporter.export_pdf(
            data_list=self.table_to_list(),
            columns=self.headers,
            filename="report_export",
            report_title=self.get_title(),
            date_from=self.date_from.text(),
            date_to=self.date_to.text()
        )

        QtWidgets.QMessageBox.information(self, "✔", f"تم حفظ ملف PDF:\n{path}")

    # =================================================================
    def export_excel(self):
        path = self.reporter.export_excel(
            data_list=self.table_to_list(),
            columns=self.headers,
            filename="report_export",
            report_title=self.get_title(),
            date_from=self.date_from.text(),
            date_to=self.date_to.text()
        )

        QtWidgets.QMessageBox.information(self, "✔", f"تم حفظ Excel:\n{path}")

    # =================================================================
    def print_report(self):
        self.reporter.print_report(self.table)

    # =================================================================
    def table_to_list(self):
        output = []
        for r in range(self.table.rowCount()):
            entry = {}
            for c, h in enumerate(self.headers):
                item = self.table.item(r, c)
                entry[h] = item.text() if item else ""
            output.append(entry)
        return output
