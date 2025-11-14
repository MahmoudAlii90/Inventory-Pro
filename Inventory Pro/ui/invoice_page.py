from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from ui.global_signals import global_signals


class InvoicePage(QtWidgets.QWidget):
    def __init__(self, username, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.username = username
        self.permissions = permissions

        self.items_data = []  # الأصناف داخل الفاتورة

        self.build_ui()
        self.load_items()

    # =======================================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # ------------------ Title ------------------
        title = QtWidgets.QLabel("🧾 إنشاء فاتورة جديدة")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #0A3D91;")
        layout.addWidget(title)

        # ===================== Customer Section ===========================
        customer_box = QtWidgets.QHBoxLayout()

        lbl_customer = QtWidgets.QLabel("العميل:")
        lbl_customer.setStyleSheet("font-size: 16px;")

        self.customer_input = QtWidgets.QLineEdit()
        self.customer_input.setPlaceholderText("اسم العميل")

        customer_box.addWidget(lbl_customer)
        customer_box.addWidget(self.customer_input)

        layout.addLayout(customer_box)

        # ===================== Add Item Section ===========================
        item_section = QtWidgets.QHBoxLayout()

        self.items_combo = QtWidgets.QComboBox()
        self.qty_input = QtWidgets.QSpinBox()
        self.qty_input.setRange(1, 99999)

        self.price_input = QtWidgets.QDoubleSpinBox()
        self.price_input.setRange(0, 999999)
        self.price_input.setDecimals(2)

        self.discount_input = QtWidgets.QDoubleSpinBox()
        self.discount_input.setSuffix(" %")
        self.discount_input.setRange(0, 100)

        btn_add = QtWidgets.QPushButton("➕ إضافة صنف")
        btn_add.clicked.connect(self.add_item_to_invoice)

        item_section.addWidget(self.items_combo)
        item_section.addWidget(QtWidgets.QLabel("كمية:"))
        item_section.addWidget(self.qty_input)
        item_section.addWidget(QtWidgets.QLabel("سعر:"))
        item_section.addWidget(self.price_input)
        item_section.addWidget(QtWidgets.QLabel("خصم:"))
        item_section.addWidget(self.discount_input)
        item_section.addWidget(btn_add)

        layout.addLayout(item_section)

        # ===================== Items Table ===========================
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["الصنف", "الكمية", "السعر", "خصم", "الإجمالي", "حذف"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # ===================== Totals Section ===========================
        totals = QtWidgets.QHBoxLayout()

        self.subtotal_lbl = QtWidgets.QLabel("الإجمالي الفرعي: 0.00")
        self.tax_lbl = QtWidgets.QLabel("الضريبة (14%): 0.00")
        self.shipping_input = QtWidgets.QDoubleSpinBox()
        self.shipping_input.setRange(0, 999999)
        self.shipping_input.setPrefix("الشحن: ")
        self.total_lbl = QtWidgets.QLabel("الإجمالي النهائي: 0.00")

        totals.addWidget(self.subtotal_lbl)
        totals.addWidget(self.tax_lbl)
        totals.addWidget(self.shipping_input)
        totals.addWidget(self.total_lbl)

        layout.addLayout(totals)

        # ===================== Footer Buttons ===========================
        footer = QtWidgets.QHBoxLayout()

        btn_save = QtWidgets.QPushButton("💾 حفظ الفاتورة")
        btn_save.clicked.connect(self.save_invoice)

        btn_pdf = QtWidgets.QPushButton("🖨 طباعة PDF")
        btn_pdf.clicked.connect(self.export_pdf)

        footer.addWidget(btn_save)
        footer.addWidget(btn_pdf)

        layout.addLayout(footer)

    # =======================================================================
    def load_items(self):
        """تحميل الأصناف من قاعدة البيانات إلى ComboBox"""
        self.items_combo.clear()
        self.all_items = self.db.get_items()
        for item in self.all_items:
            self.items_combo.addItem(item["name"], item["id"])

    # =======================================================================
    def add_item_to_invoice(self):
        """ إضافة صنف داخل الفاتورة """
        item_id = self.items_combo.currentData()
        qty = self.qty_input.value()
        price = self.price_input.value()
        discount = self.discount_input.value()

        if price == 0:
            QtWidgets.QMessageBox.warning(self, "خطأ", "يجب إدخال سعر الصنف.")
            return

        total = (qty * price) * (1 - discount / 100)

        self.items_data.append({
            "id": item_id,
            "name": self.items_combo.currentText(),
            "qty": qty,
            "price": price,
            "discount": discount,
            "total": total
        })

        self.refresh_table()
        self.calculate_totals()

    # =======================================================================
    def refresh_table(self):
        """ تحديث الجدول """
        self.table.setRowCount(len(self.items_data))

        for row, item in enumerate(self.items_data):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item["name"]))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item["qty"])))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(item["price"])))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(item["discount"])))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{item['total']:.2f}"))

            btn_delete = QtWidgets.QPushButton("❌")
            btn_delete.clicked.connect(lambda _, r=row: self.delete_row(r))
            self.table.setCellWidget(row, 5, btn_delete)

    # =======================================================================
    def delete_row(self, index):
        """ حذف صنف من الفاتورة """
        del self.items_data[index]
        self.refresh_table()
        self.calculate_totals()

    # =======================================================================
    def calculate_totals(self):
        """ حساب الإجماليات """
        subtotal = sum(x["total"] for x in self.items_data)
        tax = subtotal * 0.14
        shipping = self.shipping_input.value()
        total = subtotal + tax + shipping

        self.subtotal_lbl.setText(f"الإجمالي الفرعي: {subtotal:.2f}")
        self.tax_lbl.setText(f"الضريبة (14%): {tax:.2f}")
        self.total_lbl.setText(f"الإجمالي النهائي: {total:.2f}")

        self.current_total = total

    # =======================================================================
    def save_invoice(self):
        """ حفظ الفاتورة داخل قاعدة البيانات """
        if not self.items_data:
            QtWidgets.QMessageBox.warning(self, "خطأ", "لا توجد أصناف داخل الفاتورة.")
            return

        customer = self.customer_input.text().strip()
        if not customer:
            QtWidgets.QMessageBox.warning(self, "خطأ", "يجب إدخال اسم العميل.")
            return

        invoice_items = self.items_data.copy()

        self.db.add_invoice(customer, self.username, invoice_items, self.current_total)

        global_signals.data_changed.emit()

        QtWidgets.QMessageBox.information(self, "✔", "تم حفظ الفاتورة بنجاح.")

        self.items_data = []
        self.refresh_table()
        self.calculate_totals()

    # =======================================================================
    def export_pdf(self):
        """ تصدير PDF (يستخدم engine في invoice_print.py) """
        from utils.invoice_print import InvoicePrinter

        if not self.items_data:
            QtWidgets.QMessageBox.warning(self, "خطأ", "لا توجد أصناف داخل الفاتورة.")
            return

        printer = InvoicePrinter()
        printer.print_invoice(
            customer=self.customer_input.text(),
            items=self.items_data,
            subtotal=sum(x["total"] for x in self.items_data),
            shipping=self.shipping_input.value(),
            tax=sum(x["total"] for x in self.items_data) * 0.14,
            total=self.current_total
        )

        QtWidgets.QMessageBox.information(self, "✔", "تم إنشاء ملف PDF بنجاح.")
