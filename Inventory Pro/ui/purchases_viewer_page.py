from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from utils.export_utils import Exporter
from utils.invoice_print import InvoicePrinter
from ui.global_signals import global_signals


class PurchasesViewerPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions

        self.build_ui()
        self.load_data()

        # تحديث تلقائي عند إضافة فاتورة شراء جديدة
        global_signals.data_changed.connect(self.load_data)

    # ======================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("📥 عرض فواتير المشتريات")
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
        self.search.setPlaceholderText("🔍 بحث (رقم الفاتورة / المورد)...")
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
            "ID", "رقم الفاتورة", "المورد", "الإجمالي", "التاريخ", "عرض"
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
        self.purchases = self.db.get_purchases_full()
        self.apply_filters()

    # ======================================================
    def apply_filters(self):
        txt = self.search.text().strip().lower()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")

        filtered = []
        for p in self.purchases:
            if txt and txt not in str(p["invoice_no"]).lower() and txt not in p["supplier"].lower():
                continue

            if self.date_from.date().isValid() and p["date"] < date_from:
                continue

            if self.date_to.date().isValid() and p["date"] > date_to:
                continue

            filtered.append(p)

        self.update_table(filtered)

    # ======================================================
    def update_table(self, data):
        self.table.setRowCount(len(data))

        for i, p in enumerate(data):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(p["id"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(p["invoice_no"]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(p["supplier"]))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(p["total"])))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(p["date"]))

            btn_view = QtWidgets.QPushButton("🔍")
            btn_view.clicked.connect(lambda _, sid=p["id"]: self.open_invoice(sid))
            self.table.setCellWidget(i, 5, btn_view)

    # ======================================================
    def open_invoice(self, purchase_id):
        """طباعة أو عرض فاتورة مشتريات"""
        invoice_data = self.db.get_purchase_invoice(purchase_id)
        InvoicePrinter().print_invoice(invoice_data, size="A4")
        QtWidgets.QMessageBox.information(self, "✔", "تم تجهيز الفاتورة للطباعة.")

    # ======================================================
    def export_excel(self):
        Exporter.export_purchases_excel(self.purchases)
        QtWidgets.QMessageBox.information(self, "✔", "تم تصدير Excel.")

    # ======================================================
    def export_pdf(self):
        Exporter.export_purchases_pdf(self.purchases)
        QtWidgets.QMessageBox.information(self, "✔", "تم إنشاء PDF.")
