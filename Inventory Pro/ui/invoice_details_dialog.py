from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from utils.export_utils import Exporter


class InvoiceDetailsDialog(QtWidgets.QDialog):
    def __init__(self, invoice_id):
        super().__init__()
        self.invoice_id = invoice_id
        self.db = DatabaseManager()

        self.setWindowTitle("تفاصيل الفاتورة")
        self.setMinimumSize(700, 500)

        self.build_ui()
        self.load_data()

    # -----------------------------------------------------------
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.lbl_title = QtWidgets.QLabel("تفاصيل الفاتورة")
        self.lbl_title.setStyleSheet("font-size:22px; font-weight:bold; color:#0A3D91;")
        layout.addWidget(self.lbl_title)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["الصنف", "الكمية", "السعر", "الإجمالي", "المخزن"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        btn_export = QtWidgets.QPushButton("📄 طباعة / حفظ PDF")
        btn_export.clicked.connect(self.export_pdf)
        layout.addWidget(btn_export)

    # -----------------------------------------------------------
    def load_data(self):
        data = self.db.get_sales_items(self.invoice_id)

        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(row["item_name"]))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(row["qty"])))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(row["price"])))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(row["total"])))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(row["warehouse"]))

    # -----------------------------------------------------------
    def export_pdf(self):
        invoice = self.db.get_sale_invoice_header(self.invoice_id)
        items = self.db.get_sales_items(self.invoice_id)

        Exporter.export_invoice_pdf(invoice, items)
        QtWidgets.QMessageBox.information(self, "✔", "تم إنشاء ملف PDF بنجاح.")
