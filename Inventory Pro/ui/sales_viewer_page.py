from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from utils.export_utils import Exporter
from utils.invoice_print import InvoicePrinter
from ui.global_signals import global_signals


class SalesViewerPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions

        self.build_ui()
        self.load_data()

        # تحديث تلقائي عند حصول عملية جديدة
        global_signals.data_changed.connect(self.load_data)

    # ======================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("💰 عرض فواتير المبيعات")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0A3D91;
        """)
        layout.addWidget(title)

        # ==================== FILTER BAR ======================
        filter_bar = QtWidgets.QHBoxLayout()
        layout.addLayout(filter_bar)

        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("🔍 بحث (رقم الفاتورة / العميل)...")
        self.search.textChanged.connect(self.apply_filters)
        filter_bar.addWidget(self.search)

        self.date_from = QtWidgets.QDateEdit()
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setCalendarPopup(True)
        filter_bar.addWidget(QtWidgets.QLabel("من:"))
        filter_bar.addWidget(self.date_from)

        self.date_to = QtWidgets.QDateEdit()
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setCalendarPopup(True)
        filter_bar.addWidget(QtWidgets.QLabel("إلى:"))
        filter_bar.addWidget(self.date_to)

        btn_filter = QtWidgets.QPushButton("✔ تطبيق")
        btn_filter.clicked.connect(self.apply_filters)
        filter_bar.addWidget(btn_filter)

        # ================= TABLE ===================
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "رقم الفاتورة", "العميل", "الإجمالي", "التاريخ", "عرض"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # ================= BUTTONS ===================
        buttons = QtWidgets.QHBoxLayout()
        buttons.setAlignment(QtCore.Qt.AlignCenter)
        layout.addLayout(buttons)

        btn_excel = QtWidgets.QPushButton("📄 تصدير Excel")
        btn_excel.clicked.connect(self.export_excel)
        buttons.addWidget(btn_excel)

        btn_pdf = QtWidgets.QPushButton("🖨 تقرير PDF")
        btn_pdf.clicked.connect(self.export_pdf)
        buttons.addWidget(btn_pdf)

    # ======================================================
    def load_data(self):
        self.sales = self.db.get_sales_full()
        self.apply_filters()

    # ======================================================
    def apply_filters(self):
        txt = self.search.text().strip().lower()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")

        filtered = []
        for s in self.sales:
            # النص
            if txt and txt not in str(s["invoice_no"]).lower() and txt not in s["customer"].lower():
                continue

            # التاريخ
            if self.date_from.date().isValid() and s["date"] < date_from:
                continue

            if self.date_to.date().isValid() and s["date"] > date_to:
                continue

            filtered.append(s)

        self.update_table(filtered)

    # ======================================================
    def update_table(self, data):
        self.table.setRowCount(len(data))

        for i, s in enumerate(data):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(s["id"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(s["invoice_no"]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(s["customer"]))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(s["total"])))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(s["date"]))

            btn_view = QtWidgets.QPushButton("🔍")
            btn_view.clicked.connect(lambda _, sid=s["id"]: self.open_invoice(sid))
            self.table.setCellWidget(i, 5, btn_view)

    # ======================================================
    def open_invoice(self, sale_id):
        InvoicePrinter().print_invoice(
            self.db.get_sale_invoice(sale_id),
            size="A4"
        )
        QtWidgets.QMessageBox.information(self, "✔", "تم فتح الفاتورة للطباعة.")

    # ======================================================
    def export_excel(self):
        Exporter.export_sales_excel(self.sales)
        QtWidgets.QMessageBox.information(self, "✔", "تم تصدير Excel.")

    # ======================================================
    def export_pdf(self):
        Exporter.export_sales_pdf(self.sales)
        QtWidgets.QMessageBox.information(self, "✔", "تم إنشاء PDF.")
