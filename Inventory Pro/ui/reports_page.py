# ui/reports_page.py
from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from utils.export_utils import ExportUtils
from utils.settings_manager import SettingsManager


class ReportsPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.permissions = permissions
        self.db = DatabaseManager()
        self.settings = SettingsManager()

        self.setStyleSheet("font-family: Cairo; background:#F5F6FA;")
        self.build_ui()

    # =====================================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("📘 التقارير — Reports Center")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
            color:#0A3D91;
            margin-bottom:25px;
        """)
        layout.addWidget(title)

        # ====================== REPORT SELECTOR =======================
        selector_box = QtWidgets.QFrame()
        selector_box.setStyleSheet("""
            background:white;
            border-radius:10px;
            border:1px solid #DDD;
        """)
        selector_layout = QtWidgets.QHBoxLayout(selector_box)

        self.report_types = QtWidgets.QComboBox()
        self.report_types.addItems([
            "تقرير الأصناف",
            "تقرير المخازن",
            "تقرير الموردين",
            "تقرير العملاء",
            "تقرير المبيعات",
            "تقرير المشتريات",
            "تقرير الأذونات",
            "تقرير المخزون المنخفض",
            "تقرير الأرباح"
        ])

        selector_layout.addWidget(QtWidgets.QLabel("نوع التقرير:"))
        selector_layout.addWidget(self.report_types)

        # ====================== DATE FILTERS ==========================
        self.date_from = QtWidgets.QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")

        self.date_to = QtWidgets.QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")

        selector_layout.addWidget(QtWidgets.QLabel("من:"))
        selector_layout.addWidget(self.date_from)
        selector_layout.addWidget(QtWidgets.QLabel("إلى:"))
        selector_layout.addWidget(self.date_to)

        btn_load = QtWidgets.QPushButton("📊 عرض التقرير")
        btn_load.setStyleSheet("background:#0A3D91; color:white; padding:8px;")
        btn_load.clicked.connect(self.load_report)
        selector_layout.addWidget(btn_load)

        layout.addWidget(selector_box)

        # ====================== TABLE ================================
        self.table = QtWidgets.QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background:white;
                border-radius:8px;
                border:1px solid #DDD;
            }
        """)
        layout.addWidget(self.table)

        # ====================== FOOTER BUTTONS =======================
        btns_layout = QtWidgets.QHBoxLayout()

        btn_pdf = QtWidgets.QPushButton("📄 Export PDF")
        btn_pdf.clicked.connect(self.export_pdf)

        btn_excel = QtWidgets.QPushButton("📊 Export Excel")
        btn_excel.clicked.connect(self.export_excel)

        btns_layout.addWidget(btn_pdf)
        btns_layout.addWidget(btn_excel)
        btns_layout.addStretch(1)

        layout.addLayout(btns_layout)

    # =====================================================================
    def load_report(self):
        report = self.report_types.currentText()
        date_from = self.date_from.text()
        date_to = self.date_to.text()

        if report == "تقرير الأصناف":
            data = self.db.get_items()
            headers = ["ID", "الاسم", "SKU", "الكمية", "الحد الأدنى", "المخزن"]

        elif report == "تقرير المخازن":
            data = self.db.get_warehouses()
            headers = ["ID", "اسم المخزن", "الموقع"]

        elif report == "تقرير الموردين":
            data = self.db.get_suppliers()
            headers = ["ID", "الاسم", "التليفون", "العنوان"]

        elif report == "تقرير العملاء":
            data = self.db.get_customers()
            headers = ["ID", "الاسم", "التليفون", "العنوان"]

        elif report == "تقرير المبيعات":
            data = self.db.get_sales_invoices()
            headers = ["ID", "التاريخ", "العميل", "عدد الأصناف", "الإجمالي", "المستخدم"]

        elif report == "تقرير المشتريات":
            data = self.db.get_purchase_invoices()
            headers = ["ID", "التاريخ", "المورد", "عدد الأصناف", "الإجمالي", "المستخدم"]

        elif report == "تقرير الأذونات":
            data = self.db.get_transactions()
            headers = ["ID", "النوع", "الصنف", "الكمية", "من", "إلى", "المستخدم", "التاريخ"]

        elif report == "تقرير المخزون المنخفض":
            items = self.db.get_items()
            data = [i for i in items if i["quantity"] <= i["min_quantity"]]
            headers = ["ID", "الصنف", "الكمية", "الحد الأدنى", "المخزن"]

        elif report == "تقرير الأرباح":
            data = self.db.get_profit_report(date_from, date_to)
            headers = ["التاريخ", "المبيعات", "المشتريات", "الربح"]

        else:
            return

        self.fill_table(headers, data)

    # =====================================================================
    def fill_table(self, headers, data):
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setRowCount(len(data))

        for r, row in enumerate(data):
            for c, h in enumerate(headers):
                value = row.get(h, row.get(h.lower(), row.get(c, "")))
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(str(value)))

        self.table.horizontalHeader().setStretchLastSection(True)

    # =====================================================================
    def export_pdf(self):
        ExportUtils.export_pdf(
            self.table,
            "Report",
            self.settings.get("company_name"),
            self.settings.get("logo_path")
        )

    def export_excel(self):
        ExportUtils.export_excel(
            self.table,
            "Report"
        )
