from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from utils.invoice_print import InvoicePrinter
from ui.global_signals import global_signals


class PurchasesEntryPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions

        self.items_list = self.db.get_items()
        self.suppliers = self.db.get_suppliers()

        self.cart = []  # [{id, name, qty, price, total}]
        self.build_ui()

    # ===================================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("📥 إنشاء فاتورة مشتريات")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0A3D91;
        """)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        # ============= Supplier Selection ==================
        form = QtWidgets.QFormLayout()
        self.supplier_combo = QtWidgets.QComboBox()
        self.supplier_combo.addItem("— اختر المورد —", -1)

        for s in self.suppliers:
            self.supplier_combo.addItem(s["name"], s["id"])

        form.addRow("المورد:", self.supplier_combo)
        layout.addLayout(form)

        # ============= Items Search ==================
        search_layout = QtWidgets.QHBoxLayout()
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("اكتب اسم الصنف للبحث…")
        self.search_box.textChanged.connect(self.search_items)

        search_layout.addWidget(QtWidgets.QLabel("🔍 بحث:"))
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # ============= Items Table ==================
        self.table_items = QtWidgets.QTableWidget()
        self.table_items.setColumnCount(4)
        self.table_items.setHorizontalHeaderLabels(["ID", "الصنف", "الكمية الحالية", "سعر التكلفة"])
        self.table_items.horizontalHeader().setStretchLastSection(True)
        self.table_items.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.table_items.doubleClicked.connect(self.add_item_to_cart)

        layout.addWidget(self.table_items)
        self.refresh_items_table(self.items_list)

        # ============= CART ==================
        cart_lbl = QtWidgets.QLabel("🧾 محتويات الفاتورة")
        cart_lbl.setStyleSheet("font-size:20px; font-weight:bold;")
        layout.addWidget(cart_lbl)

        self.table_cart = QtWidgets.QTableWidget()
        self.table_cart.setColumnCount(5)
        self.table_cart.setHorizontalHeaderLabels(["الصنف", "الكمية", "سعر التكلفة", "الإجمالي", "—"])
        self.table_cart.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_cart)

        # Total
        total_layout = QtWidgets.QHBoxLayout()
        self.lbl_total = QtWidgets.QLabel("الإجمالي: 0.00")
        self.lbl_total.setStyleSheet("font-size: 22px; font-weight: bold; color:#0A3D91;")
        total_layout.addStretch()
        total_layout.addWidget(self.lbl_total)
        layout.addLayout(total_layout)

        # ============= ACTION BUTTONS ==================
        btns = QtWidgets.QHBoxLayout()
        btns.addStretch()

        self.btn_save = QtWidgets.QPushButton("💾 حفظ الفاتورة")
        self.btn_save.clicked.connect(self.save_invoice)

        self.btn_print = QtWidgets.QPushButton("🖨 طباعة")
        self.btn_print.clicked.connect(self.print_invoice)
        self.btn_print.setEnabled(False)

        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_print)
        layout.addLayout(btns)

    # ===================================================================
    def search_items(self):
        text = self.search_box.text().strip()
        if text == "":
            self.refresh_items_table(self.items_list)
            return

        result = [i for i in self.items_list if text in i["name"]]
        self.refresh_items_table(result)

    # ===================================================================
    def refresh_items_table(self, data):
        self.table_items.setRowCount(len(data))
        for i, it in enumerate(data):
            self.table_items.setItem(i, 0, QtWidgets.QTableWidgetItem(str(it["id"])))
            self.table_items.setItem(i, 1, QtWidgets.QTableWidgetItem(it["name"]))
            self.table_items.setItem(i, 2, QtWidgets.QTableWidgetItem(str(it["quantity"])))
            self.table_items.setItem(i, 3, QtWidgets.QTableWidgetItem("0"))

    # ===================================================================
    def add_item_to_cart(self):
        row = self.table_items.currentRow()
        if row < 0:
            return

        item_id = int(self.table_items.item(row, 0).text())
        name = self.table_items.item(row, 1).text()

        qty, ok = QtWidgets.QInputDialog.getInt(self, "الكمية", "ادخل الكمية:", 1, 1)
        if not ok:
            return

        cost, ok = QtWidgets.QInputDialog.getDouble(self, "سعر التكلفة", "ادخل السعر:", 0, 0)
        if not ok:
            return

        total = qty * cost

        self.cart.append({
            "id": item_id,
            "name": name,
            "qty": qty,
            "price": cost,
            "total": total
        })

        self.refresh_cart()
        self.update_total()

    # ===================================================================
    def refresh_cart(self):
        self.table_cart.setRowCount(len(self.cart))

        for i, item in enumerate(self.cart):
            self.table_cart.setItem(i, 0, QtWidgets.QTableWidgetItem(item["name"]))
            self.table_cart.setItem(i, 1, QtWidgets.QTableWidgetItem(str(item["qty"])))
            self.table_cart.setItem(i, 2, QtWidgets.QTableWidgetItem(str(item["price"])))
            self.table_cart.setItem(i, 3, QtWidgets.QTableWidgetItem(str(item["total"])))

            btn_remove = QtWidgets.QPushButton("❌")
            btn_remove.clicked.connect(lambda _, r=i: self.remove_from_cart(r))
            self.table_cart.setCellWidget(i, 4, btn_remove)

    # ===================================================================
    def remove_from_cart(self, index):
        del self.cart[index]
        self.refresh_cart()
        self.update_total()

    # ===================================================================
    def update_total(self):
        total = sum([i["total"] for i in self.cart])
        self.lbl_total.setText(f"الإجمالي: {total:.2f}")

    # ===================================================================
    def save_invoice(self):
        if len(self.cart) == 0:
            QtWidgets.QMessageBox.warning(self, "⚠", "لا توجد أصناف داخل الفاتورة.")
            return

        supplier_id = self.supplier_combo.currentData()
        if supplier_id == -1:
            QtWidgets.QMessageBox.warning(self, "⚠", "اختر المورد.")
            return

        invoice_id = self.db.create_purchase_invoice(supplier_id, self.cart)

        QtWidgets.QMessageBox.information(self, "✔", f"تم حفظ الفاتورة.\nرقم الفاتورة: {invoice_id}")

        self.btn_print.setEnabled(True)
        global_signals.data_changed.emit()

    # ===================================================================
    def print_invoice(self):
        if len(self.cart) == 0:
            return

        supplier = self.supplier_combo.currentText()
        total_value = self.lbl_total.text().replace("الإجمالي: ", "")

        InvoicePrinter().print_purchase_invoice(supplier, self.cart, total_value)

        QtWidgets.QMessageBox.information(self, "✔", "تم طباعة الفاتورة بنجاح.")
