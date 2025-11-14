from PyQt5 import QtWidgets, QtCore
from utils.db_manager import DatabaseManager
from utils.export_utils import Exporter
from utils.invoice_print import InvoicePrinter
from ui.purchase_details_dialog import PurchaseDetailsDialog



class PurchasesViewer(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()
        self.permissions = permissions
        self.db = DatabaseManager()

        self.invoices = []
        self.build_ui()
        self.load_data()

    # ============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("📗 عرض فواتير المشتريات")
        title.setStyleSheet("font-size:22px; font-weight:bold; color:#0A3D91;")
        layout.addWidget(title)

        # ------------------- شريط الأدوات -------------------
        tools = QtWidgets.QHBoxLayout()

        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("بحث برقم الفاتورة / المورّد ...")
        self.search_box.textChanged.connect(self.search)

        btn_export_excel = QtWidgets.QPushButton("🟩 Excel")
        btn_export_excel.clicked.connect(self.export_excel)

        btn_export_pdf = QtWidgets.QPushButton("📄 PDF")
        btn_export_pdf.clicked.connect(self.export_pdf)

        tools.addWidget(self.search_box)
        tools.addWidget(btn_export_excel)
        tools.addWidget(btn_export_pdf)

        layout.addLayout(tools)

        # ------------------- جدول الفواتير -------------------
        self.table = QtWidgets.QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["رقم", "المورّد", "الإجمالي", "الخصم", "الصافي", "المستخدم", "التاريخ"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.doubleClicked.connect(self.open_invoice_details)

        layout.addWidget(self.table)

    # ============================================================
    def load_data(self):
        self.invoices = self.db.get_purchase_invoices()
        self.refresh_table(self.invoices)

    # ============================================================
    def refresh_table(self, data):
        self.table.setRowCount(len(data))

        for row, inv in enumerate(data):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(inv["id"])))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(inv["supplier"]))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(inv["total"])))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(inv["discount"])))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(inv["net_total"])))
            self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(inv["created_by"]))
            self.table.setItem(row, 6, QtWidgets.QTableWidgetItem(inv["date"]))

    # ============================================================
    def search(self, text):
        text = text.strip()

        if text == "":
            self.refresh_table(self.invoices)
            return

        result = []
        for inv in self.invoices:
            if text in str(inv["id"]) or text in inv["supplier"]:
                result.append(inv)

        self.refresh_table(result)

    # ============================================================
    def open_invoice_details(self):
        row = self.table.currentRow()
        if row < 0:
            return

        invoice_id = int(self.table.item(row, 0).text())
        items = self.db.get_purchase_items(invoice_id)

        dlg = PurchaseDetailsDialog(invoice_id, items)
        dlg.exec_()

    # ============================================================
    def export_excel(self):
        Exporter.export_purchases_excel(self.invoices)
        QtWidgets.QMessageBox.information(self, "✔", "تم تصدير Excel بنجاح.")

    # ============================================================
    def export_pdf(self):
        Exporter.export_purchases_pdf(self.invoices)
        QtWidgets.QMessageBox.information(self, "✔", "تم تصدير PDF بنجاح.")
