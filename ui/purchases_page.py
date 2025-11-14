from PyQt5 import QtWidgets, QtCore
from utils.db_manager import DatabaseManager
from utils.global_signals import global_signals


class PurchasesPage(QtWidgets.QWidget):
    def __init__(self, username, permissions):
        super().__init__()

        self.username = username
        self.permissions = permissions
        self.db = DatabaseManager()

        self.items = self.db.get_items()
        self.suppliers = self.db.get_suppliers()

        self.build_ui()

    # ============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("📥 فاتورة مشتريات جديدة")
        title.setStyleSheet("font-size:22px; font-weight:bold; color:#0A3D91;")
        layout.addWidget(title)

        form = QtWidgets.QFormLayout()

        # =================== اختيار المورّد ===================
        self.supplier_combo = QtWidgets.QComboBox()
        for c in self.suppliers:
            self.supplier_combo.addItem(c["name"], c["id"])
        form.addRow("المورّد:", self.supplier_combo)

        # =================== جدول الأصناف ===================
        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["الصنف", "السعر", "الكمية", "الإجمالي", ""])
        self.table.horizontalHeader().setStretchLastSection(True)

        btn_add_item = QtWidgets.QPushButton("➕ إضافة صنف")
        btn_add_item.clicked.connect(self.add_row)

        layout.addLayout(form)
        layout.addWidget(self.table)
        layout.addWidget(btn_add_item)

        # =================== المجاميع ===================
        totals_box = QtWidgets.QHBoxLayout()

        self.total_lbl = QtWidgets.QLabel("0")
        self.discount_input = QtWidgets.QSpinBox()
        self.discount_input.setSuffix(" %")
        self.discount_input.setMaximum(100)
        self.net_total_lbl = QtWidgets.QLabel("0")

        totals_box.addWidget(QtWidgets.QLabel("المجموع:"))
        totals_box.addWidget(self.total_lbl)
        totals_box.addWidget(QtWidgets.QLabel("الخصم:"))
        totals_box.addWidget(self.discount_input)
        totals_box.addWidget(QtWidgets.QLabel("الصافي:"))
        totals_box.addWidget(self.net_total_lbl)

        self.discount_input.valueChanged.connect(self.calculate_totals)

        layout.addLayout(totals_box)

        # =================== حفظ الفاتورة ===================
        btn_save = QtWidgets.QPushButton("💾 حفظ الفاتورة")
        btn_save.clicked.connect(self.save_invoice)
        layout.addWidget(btn_save)

    # ============================================================
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # اختيار صنف
        item_combo = QtWidgets.QComboBox()
        for it in self.items:
            item_combo.addItem(it["name"], it["id"])

        item_combo.currentIndexChanged.connect(self.calculate_totals)

        # السعر
        price = QtWidgets.QDoubleSpinBox()
        price.setMaximum(999999)
        price.setValue(1)
        price.valueChanged.connect(self.calculate_totals)

        # الكمية
        qty = QtWidgets.QSpinBox()
        qty.setMaximum(99999)
        qty.setValue(1)
        qty.valueChanged.connect(self.calculate_totals)

        # الإجمالي
        total = QtWidgets.QLabel("0")

        # زر حذف
        btn_del = QtWidgets.QPushButton("❌")
        btn_del.clicked.connect(lambda: self.delete_row(row))

        self.table.setCellWidget(row, 0, item_combo)
        self.table.setCellWidget(row, 1, price)
        self.table.setCellWidget(row, 2, qty)
        self.table.setCellWidget(row, 3, total)
        self.table.setCellWidget(row, 4, btn_del)

        self.calculate_totals()

    # ============================================================
    def delete_row(self, row):
        self.table.removeRow(row)
        self.calculate_totals()

    # ============================================================
    def calculate_totals(self):
        total = 0

        for row in range(self.table.rowCount()):
            price = self.table.cellWidget(row, 1).value()
            qty = self.table.cellWidget(row, 2).value()
            subtotal = price * qty

            self.table.cellWidget(row, 3).setText(str(subtotal))
            total += subtotal

        discount = self.discount_input.value()
        net = total - (total * discount / 100)

        self.total_lbl.setText(str(total))
        self.net_total_lbl.setText(str(net))

    # ============================================================
    def save_invoice(self):
        if self.table.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self, "خطأ", "أضف صنف واحد على الأقل!")
            return

        supplier_id = self.supplier_combo.currentData()
        total = float(self.total_lbl.text())
        discount = self.discount_input.value()
        net_total = float(self.net_total_lbl.text())

        paid = net_total  # فاتورة كاش
        remain = 0

        invoice_id = self.db.add_purchase_invoice(
            supplier_id, total, discount, net_total, paid, remain, self.username
        )

        # حفظ الأصناف
        for row in range(self.table.rowCount()):
            item_id = self.table.cellWidget(row, 0).currentData()
            price = self.table.cellWidget(row, 1).value()
            qty = self.table.cellWidget(row, 2).value()
            total = price * qty

            self.db.add_purchase_item(invoice_id, item_id, qty, price, total)

        QtWidgets.QMessageBox.information(self, "✔", "تم حفظ الفاتورة بنجاح.")

        global_signals.data_changed.emit()  # تحديث dashboard وباقي الصفحات
