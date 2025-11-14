from PyQt5 import QtWidgets, QtCore
from utils.db_manager import DatabaseManager
from utils.purchase_return_invoice_print import PurchaseReturnInvoicePrinter
from ui.global_signals import global_signals
import datetime


class PurchaseReturnPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions

        self.build_ui()

    # =================================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("↩️ مرتجعات المشتريات")
        title.setStyleSheet(
            "font-size:22px; font-weight:bold; color:#0A3D91; margin-bottom:20px;"
        )
        layout.addWidget(title)

        # ===================== PURCHASE INVOICE SELECT ======================
        h = QtWidgets.QHBoxLayout()
        self.invoice_id = QtWidgets.QLineEdit()
        self.invoice_id.setPlaceholderText("رقم فاتورة المشتريات...")

        btn_load = QtWidgets.QPushButton("📄 تحميل الفاتورة")
        btn_load.clicked.connect(self.load_invoice)

        h.addWidget(self.invoice_id)
        h.addWidget(btn_load)
        layout.addLayout(h)

        # ===================== ITEMS TABLE ======================
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["الصنف", "الكمية المستلمة", "إرجاع", "السعر", "الإجمالي"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # ===================== TOTAL ======================
        self.lbl_total = QtWidgets.QLabel("إجمالي المرتجع: 0")
        self.lbl_total.setStyleSheet("font-size:18px; font-weight:bold; margin-top:15px;")
        layout.addWidget(self.lbl_total)

        # ===================== ACTIONS ======================
        h2 = QtWidgets.QHBoxLayout()

        btn_process = QtWidgets.QPushButton("💾 حفظ المرتجع")
        btn_process.clicked.connect(self.save_return)
        h2.addWidget(btn_process)

        btn_print = QtWidgets.QPushButton("🖨 طباعة إشعار")
        btn_print.clicked.connect(self.print_return)
        h2.addWidget(btn_print)

        layout.addLayout(h2)

    # =================================================================
    def load_invoice(self):
        invoice_id = self.invoice_id.text().strip()
        if not invoice_id:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "الرجاء إدخال رقم الفاتورة.")
            return

        items = self.db.get_purchase_invoice_items(invoice_id)

        if not items:
            QtWidgets.QMessageBox.warning(self, "خطأ", "لم يتم العثور على الفاتورة.")
            return

        self.table.setRowCount(len(items))

        for r, it in enumerate(items):
            name = QtWidgets.QLabel(it["item_name"])
            qty = QtWidgets.QLabel(str(it["qty"]))
            price = QtWidgets.QLabel(str(it["price"]))

            return_qty = QtWidgets.QSpinBox()
            return_qty.setRange(0, it["qty"])
            return_qty.valueChanged.connect(self.update_totals)

            total = QtWidgets.QLabel("0")

            self.table.setCellWidget(r, 0, name)
            self.table.setCellWidget(r, 1, qty)
            self.table.setCellWidget(r, 2, return_qty)
            self.table.setCellWidget(r, 3, price)
            self.table.setCellWidget(r, 4, total)

        self.update_totals()

    # =================================================================
    def update_totals(self):
        total = 0
        for r in range(self.table.rowCount()):
            qty = self.table.cellWidget(r, 2).value()
            price = float(self.table.cellWidget(r, 3).text())
            row_total = qty * price
            self.table.cellWidget(r, 4).setText(f"{row_total:.2f}")
            total += row_total

        self.lbl_total.setText(f"إجمالي المرتجع: {total:.2f}")

    # =================================================================
    def gather_return_data(self):
        invoice_id = self.invoice_id.text().strip()
        items = []

        for r in range(self.table.rowCount()):
            qty = self.table.cellWidget(r, 2).value()
            if qty == 0:
                continue

            name = self.table.cellWidget(r, 0).text()
            price = float(self.table.cellWidget(r, 3).text())
            total = qty * price

            items.append({
                "name": name,
                "qty": qty,
                "price": price,
                "total": total
            })

        return invoice_id, items

    # =================================================================
    def save_return(self):
        invoice_id, items = self.gather_return_data()

        if not items:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "لا توجد كميات مرتجعة.")
            return

        return_id = self.db.save_purchase_return(invoice_id, items)

        global_signals.data_changed.emit()

        QtWidgets.QMessageBox.information(
            self, "✔", f"تم حفظ المرتجع بنجاح.\nرقم المرتجع: {return_id}"
        )

    # =================================================================
    def print_return(self):
        invoice_id, items = self.gather_return_data()

        if not items:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "لا توجد كميات مرتجعة.")
            return

        data = {
            "return_id": int(datetime.datetime.now().timestamp()),
            "invoice_id": invoice_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total": sum(i["total"] for i in items)
        }

        filename = f"Purchase_Return_{data['return_id']}.pdf"

        printer = PurchaseReturnInvoicePrinter()
        printer.generate_pdf(data, items, filename, size="A4")

        QtWidgets.QMessageBox.information(
            self,
            "✔",
            f"تم إنشاء إشعار المرتجع بنجاح.\n{filename}"
        )