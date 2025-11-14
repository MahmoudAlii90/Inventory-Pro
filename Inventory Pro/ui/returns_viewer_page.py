from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from utils.export_utils import ExportUtils
from ui.global_signals import global_signals


class ReturnsViewerPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions

        self.build_ui()
        self.load_data()

        global_signals.data_changed.connect(self.load_data)

    # =============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("📄 عرض المرتجعات (مبيعات + مشتريات)")
        title.setStyleSheet("""
            font-size: 26px;
            color: #0A3D91;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        layout.addWidget(title)

        # ====================== FILTERS ======================
        filters = QtWidgets.QHBoxLayout()

        # نوع المرتجع
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["الكل", "مرتجع مبيعات", "مرتجع مشتريات"])
        self.type_combo.currentIndexChanged.connect(self.load_data)
        filters.addWidget(self.type_combo)

        # البحث
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("بحث: رقم الفاتورة، الصنف…")
        self.search_box.textChanged.connect(self.load_data)
        filters.addWidget(self.search_box)

        # التاريخ من
        self.date_from = QtWidgets.QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setDate(QtCore.QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.load_data)
        filters.addWidget(self.date_from)

        # التاريخ إلى
        self.date_to = QtWidgets.QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDate(QtCore.QDate.currentDate())
        self.date_to.dateChanged.connect(self.load_data)
        filters.addWidget(self.date_to)

        layout.addLayout(filters)

        # ====================== TABLE ======================
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Type", "Invoice", "Item", "Qty", "Note", "User", "Date"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # ====================== EXPORT ======================
        exp_layout = QtWidgets.QHBoxLayout()

        btn_pdf = QtWidgets.QPushButton("📄 تصدير PDF")
        btn_pdf.setStyleSheet("padding: 8px;")
        btn_pdf.clicked.connect(self.export_pdf)
        exp_layout.addWidget(btn_pdf)

        btn_xls = QtWidgets.QPushButton("📊 تصدير Excel")
        btn_xls.setStyleSheet("padding: 8px;")
        btn_xls.clicked.connect(self.export_excel)
        exp_layout.addWidget(btn_xls)

        layout.addLayout(exp_layout)

    # =============================================================
    def load_data(self):
        search = self.search_box.text().strip()
        t = self.type_combo.currentText()
        d_from = self.date_from.date().toString("yyyy-MM-dd")
        d_to = self.date_to.date().toString("yyyy-MM-dd")

        # جلب جميع البيانات
        sales_ret = self.db.get_sales_returns()
        purch_ret = self.db.get_purchase_returns()

        rows = []

        # ================= SALES =================
        if t in ["الكل", "مرتجع مبيعات"]:
            for r in sales_ret:
                if search and search not in str(r["invoice_no"]) and search not in r["item_name"]:
                    continue

                if not (d_from <= r["date"][:10] <= d_to):
                    continue

                rows.append({
                    "type": "مرتجع مبيعات",
                    "invoice": r["invoice_no"],
                    "item": r["item_name"],
                    "qty": r["qty"],
                    "note": r["note"],
                    "user": r["user"],
                    "date": r["date"]
                })

        # ================= PURCHASE =================
        if t in ["الكل", "مرتجع مشتريات"]:
            for r in purch_ret:
                if search and search not in str(r["invoice_no"]) and search not in r["item_name"]:
                    continue

                if not (d_from <= r["date"][:10] <= d_to):
                    continue

                rows.append({
                    "type": "مرتجع مشتريات",
                    "invoice": r["invoice_no"],
                    "item": r["item_name"],
                    "qty": r["qty"],
                    "note": r["note"],
                    "user": r["user"],
                    "date": r["date"]
                })

        # ================= FILL TABLE =================
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(r["type"]))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(r["invoice"])))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(r["item"]))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(r["qty"])))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(r["note"]))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(r["user"]))
            self.table.setItem(i, 6, QtWidgets.QTableWidgetItem(r["date"]))

        self.current_rows = rows

    # =============================================================
    def export_pdf(self):
        ExportUtils.export_generic_report(
            title="Returns Report",
            columns=["Type", "Invoice", "Item", "Qty", "Note", "User", "Date"],
            rows=self.current_rows
        )
        QtWidgets.QMessageBox.information(self, "✔", "تم تصدير PDF بنجاح.")

    # =============================================================
    def export_excel(self):
        ExportUtils.export_generic_excel(
            file_name="returns_report.xlsx",
            sheet_name="Returns",
            columns=["Type", "Invoice", "Item", "Qty", "Note", "User", "Date"],
            rows=self.current_rows
        )
        QtWidgets.QMessageBox.information(self, "✔", "تم تصدير Excel بنجاح.")
