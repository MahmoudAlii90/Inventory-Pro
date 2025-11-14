from PyQt5 import QtWidgets, QtGui, QtCore

from utils.db_manager import DatabaseManager
from utils.report_utils import ReportUtils


class ItemsPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions.get("items", {"view": 1})
        self.reporter = ReportUtils()

        self.items = []

        self.build_ui()
        self.load_items()

    # ===============================================================
    # BUILD UI
    # ===============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("📦 الأصناف")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Cairo", 20, QtGui.QFont.Bold))
        title.setStyleSheet("color:#0A3D91; margin-bottom:10px;")
        layout.addWidget(title)

        if not self.permissions.get("view"):
            layout.addWidget(QtWidgets.QLabel("🚫 ليس لديك صلاحية عرض الأصناف"))
            return

        # ---------------- FILTER BAR ----------------
        filter_layout = QtWidgets.QHBoxLayout()

        # البحث
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("بحث... (الاسم، كود الصنف، المخزن)")
        self.search_box.textChanged.connect(self.apply_filters)

        # فلترة بالمخزن
        self.wh_filter = QtWidgets.QComboBox()
        self.wh_filter.addItem("كل المخازن")
        for wh in self.db.get_warehouses():
            self.wh_filter.addItem(wh["name"])

        self.wh_filter.currentIndexChanged.connect(self.apply_filters)

        # فلتر المخزون المنخفض
        self.low_stock_check = QtWidgets.QCheckBox("عرض المخزون المنخفض فقط")
        self.low_stock_check.stateChanged.connect(self.apply_filters)

        filter_layout.addWidget(self.search_box)
        filter_layout.addWidget(self.wh_filter)
        filter_layout.addWidget(self.low_stock_check)

        filter_layout.addStretch()

        # EXPORT BUTTONS
        btn_pdf = QtWidgets.QPushButton("📄 PDF")
        btn_excel = QtWidgets.QPushButton("📊 Excel")
        btn_print = QtWidgets.QPushButton("🖨️ طباعة")

        btn_pdf.clicked.connect(self.export_pdf)
        btn_excel.clicked.connect(self.export_excel)
        btn_print.clicked.connect(self.print_items)

        filter_layout.addWidget(btn_pdf)
        filter_layout.addWidget(btn_excel)
        filter_layout.addWidget(btn_print)

        layout.addLayout(filter_layout)

        # ---------------- TABLE ----------------
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "الاسم", "الكود", "الكمية", "الحد الأدنى", "المخزن"]
        )

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        layout.addWidget(self.table)

        # زر إضافة صنف (إن وجد صلاحية)
        if self.permissions.get("add"):
            btn_add = QtWidgets.QPushButton("➕ إضافة صنف")
            btn_add.clicked.connect(self.add_item_dialog)
            layout.addWidget(btn_add)

    # ===============================================================
    # LOAD ITEMS
    # ===============================================================
    def load_items(self):
        self.items = self.db.get_items()
        self.refresh_table(self.items)

    # ===============================================================
    def refresh_table(self, data):
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(row["name"]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(row["sku"]))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(row["quantity"])))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(row["min_quantity"])))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(row["warehouse"]))

            # لون للحد الأدنى
            if row["quantity"] <= row["min_quantity"]:
                for col in range(6):
                    self.table.item(i, col).setBackground(QtGui.QColor("#FFCCCC"))

    # ===============================================================
    # FILTERS
    # ===============================================================
    def apply_filters(self):
        search = self.search_box.text().strip()
        wh = self.wh_filter.currentText()
        low_only = self.low_stock_check.isChecked()

        filtered = []

        for item in self.items:

            # البحث
            if search:
                if (search not in item["name"] and
                        search not in item["sku"] and
                        search not in item["warehouse"]):
                    continue

            # المخزن
            if wh != "كل المخازن" and item["warehouse"] != wh:
                continue

            # المخزون المنخفض
            if low_only and not (item["quantity"] <= item["min_quantity"]):
                continue

            filtered.append(item)

        self.refresh_table(filtered)

    # ===============================================================
    # EXPORT PDF
    # ===============================================================
    def export_pdf(self):
        items = self.collect_current_table()
        if not items:
            QtWidgets.QMessageBox.warning(self, "⚠", "لا توجد بيانات للتصدير")
            return

        file_path = self.reporter.export_pdf(
            data_list=items,
            columns=["id", "name", "sku", "quantity", "min_quantity", "warehouse"],
            filename="items_report",
            report_title="Items Report",
            date_from="N/A",
            date_to="N/A"
        )

        QtWidgets.QMessageBox.information(self, "✔", f"تم إنشاء PDF:\n{file_path}")

    # ===============================================================
    # EXPORT EXCEL
    # ===============================================================
    def export_excel(self):
        items = self.collect_current_table()
        if not items:
            QtWidgets.QMessageBox.warning(self, "⚠", "لا توجد بيانات للتصدير")
            return

        file_path = self.reporter.export_excel(
            data_list=items,
            columns=["id", "name", "sku", "quantity", "min_quantity", "warehouse"],
            filename="items_report",
            report_title="Items Report",
            date_from="N/A",
            date_to="N/A"
        )

        QtWidgets.QMessageBox.information(self, "✔", f"تم حفظ Excel:\n{file_path}")

    # ===============================================================
    # PRINT
    # ===============================================================
    def print_items(self):
        self.reporter.print_report(self.table)

    # ===============================================================
    # Collect Data from Table
    # ===============================================================
    def collect_current_table(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()

        headers = ["id", "name", "sku", "quantity", "min_quantity", "warehouse"]

        data = []

        for r in range(rows):
            entry = {}
            for c in range(cols):
                item = self.table.item(r, c)
                entry[headers[c]] = item.text() if item else ""
            data.append(entry)

        return data

    # ===============================================================
    # ADD ITEM (Dialog)
    # ===============================================================
    def add_item_dialog(self):
        if not self.permissions.get("add"):
            QtWidgets.QMessageBox.warning(self, "🚫", "ليس لديك صلاحية إضافة صنف")
            return

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("إضافة صنف")
        dialog.setLayout(QtWidgets.QFormLayout())

        name = QtWidgets.QLineEdit()
        sku = QtWidgets.QLineEdit()
        qty = QtWidgets.QSpinBox()
        qty.setMaximum(1000000)

        min_qty = QtWidgets.QSpinBox()
        min_qty.setMaximum(1000000)

        wh_box = QtWidgets.QComboBox()
        warehouses = self.db.get_warehouses()
        for wh in warehouses:
            wh_box.addItem(wh["name"], wh["id"])

        dialog.layout().addRow("اسم الصنف:", name)
        dialog.layout().addRow("الكود:", sku)
        dialog.layout().addRow("الكمية:", qty)
        dialog.layout().addRow("الحد الأدنى:", min_qty)
        dialog.layout().addRow("المخزن:", wh_box)

        btn_add = QtWidgets.QPushButton("✔ إضافة")
        btn_add.clicked.connect(lambda: self.save_new_item(dialog, name, sku, qty, min_qty, wh_box))

        dialog.layout().addWidget(btn_add)
        dialog.exec_()

    # ===============================================================
    def save_new_item(self, dialog, name, sku, qty, min_qty, wh_box):
        if not name.text().strip():
            QtWidgets.QMessageBox.warning(self, "⚠", "اسم الصنف مطلوب")
            return

        wh_id = wh_box.currentData()

        self.db.add_item(
            name.text().strip(),
            sku.text().strip(),
            qty.value(),
            min_qty.value(),
            wh_id
        )

        dialog.close()
        QtWidgets.QMessageBox.information(self, "✔", "تم إضافة الصنف بنجاح")
        self.load_items()
