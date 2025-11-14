from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from utils.export_utils import Exporter
from ui.global_signals import global_signals


class PriceListPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions
        self.data = []

        self.build_ui()
        self.load_prices()

        global_signals.data_changed.connect(self.load_prices)

    # ======================================================================
    def build_ui(self):

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("💲 قائمة الأسعار — Price List")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
            color:#0A3D91;
            margin-bottom:20px;
        """)
        layout.addWidget(title)

        # ======================================================================
        # SEARCH BOX
        # ======================================================================
        search_box = QtWidgets.QHBoxLayout()
        self.txt_search = QtWidgets.QLineEdit()
        self.txt_search.setPlaceholderText("بحث عن صنف...")
        self.txt_search.textChanged.connect(self.filter_search)

        search_box.addWidget(QtWidgets.QLabel("بحث:"))
        search_box.addWidget(self.txt_search)

        layout.addLayout(search_box)

        # ======================================================================
        # TABLE
        # ======================================================================
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "الصنف", "المخزن", "سعر الشراء", "سعر البيع"])
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.itemChanged.connect(self.edit_price)

        layout.addWidget(self.table)

        # ======================================================================
        # EXPORT BUTTONS
        # ======================================================================
        btns = QtWidgets.QHBoxLayout()

        btn_excel = QtWidgets.QPushButton("📘 Excel")
        btn_excel.clicked.connect(self.export_excel)

        btn_pdf = QtWidgets.QPushButton("📕 PDF")
        btn_pdf.clicked.connect(self.export_pdf)

        btn_print = QtWidgets.QPushButton("🖨 طباعة")
        btn_print.clicked.connect(self.print_report)

        btns.addWidget(btn_excel)
        btns.addWidget(btn_pdf)
        btns.addWidget(btn_print)

        layout.addLayout(btns)

    # ======================================================================
    def load_prices(self):
        """Load items with prices."""
        items = self.db.get_items()

        # تأكد أنها موجودة في DB
        for i in items:
            if "buy_price" not in i:
                i["buy_price"] = 0
            if "sell_price" not in i:
                i["sell_price"] = 0

        self.data = items
        self.fill_table(items)

    # ======================================================================
    def fill_table(self, data):
        self.table.blockSignals(True)  # لمنع التريجر أثناء التحميل

        self.table.setRowCount(len(data))

        for r, i in enumerate(data):
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(i["id"])))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(i["name"]))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(str(i.get("warehouse", ""))))

            # BUY PRICE
            buy_item = QtWidgets.QTableWidgetItem(str(i["buy_price"]))
            buy_item.setFlags(buy_item.flags() | QtCore.Qt.ItemIsEditable)
            self.table.setItem(r, 3, buy_item)

            # SELL PRICE
            sell_item = QtWidgets.QTableWidgetItem(str(i["sell_price"]))
            sell_item.setFlags(sell_item.flags() | QtCore.Qt.ItemIsEditable)
            self.table.setItem(r, 4, sell_item)

        self.table.blockSignals(False)
        self.table.resizeColumnsToContents()

    # ======================================================================
    def filter_search(self):
        text = self.txt_search.text().strip()
        filtered = [i for i in self.data if text in i["name"]]
        self.fill_table(filtered)

    # ======================================================================
    def edit_price(self, item):
        """When user edits buy/sell price"""
        if not self.permissions.get("edit"):
            QtWidgets.QMessageBox.warning(self, "❌", "ليس لديك صلاحية تعديل الأسعار")
            return

        row = item.row()
        col = item.column()

        if col not in (3, 4):
            return

        try:
            new_price = float(item.text())
        except:
            QtWidgets.QMessageBox.warning(self, "خطأ", "السعر يجب أن يكون رقماً")
            return

        item_id = int(self.table.item(row, 0).text())

        if col == 3:   # buy price
            self.db.update_item_buy_price(item_id, new_price)
            self.db.add_log("admin", "تعديل سعر شراء", "price_list",
                            f"item {item_id}: buy -> {new_price}")

        elif col == 4: # sell price
            self.db.update_item_sell_price(item_id, new_price)
            self.db.add_log("admin", "تعديل سعر بيع", "price_list",
                            f"item {item_id}: sell -> {new_price}")

        global_signals.data_changed.emit()

    # ======================================================================
    def export_excel(self):
        if not self.data:
            QtWidgets.QMessageBox.warning(self, "❌", "لا يوجد بيانات")
            return

        Exporter().export_excel(self.data, "Price_List")
        QtWidgets.QMessageBox.information(self, "✔", "تم التصدير إلى Excel.")

    # ======================================================================
    def export_pdf(self):
        if not self.data:
            QtWidgets.QMessageBox.warning(self, "❌", "لا يوجد بيانات")
            return

        Exporter().export_pdf(self.data, "Price_List")
        QtWidgets.QMessageBox.information(self, "✔", "تم إنشاء PDF.")

    # ======================================================================
    def print_report(self):
        if not self.data:
            QtWidgets.QMessageBox.warning(self, "❌", "لا يوجد بيانات للطباعة")
            return

        printer = QtWidgets.QPrinter()
        dialog = QtWidgets.QPrintDialog(printer)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            self.table.render(painter)
            painter.end()

            QtWidgets.QMessageBox.information(self, "✔", "تمت الطباعة.")
