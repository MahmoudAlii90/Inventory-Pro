from PyQt5 import QtWidgets, QtGui, QtCore

from utils.db_manager import DatabaseManager
from utils.report_utils import ReportUtils


class WarehousesPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions.get("warehouses", {"view": 1})
        self.reporter = ReportUtils()

        self.warehouses = []

        self.build_ui()
        self.load_warehouses()

    # ===============================================================
    # BUILD UI
    # ===============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("🏬 المخازن")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Cairo", 20, QtGui.QFont.Bold))
        title.setStyleSheet("color:#0A3D91; margin-bottom:10px;")
        layout.addWidget(title)

        if not self.permissions.get("view"):
            layout.addWidget(QtWidgets.QLabel("🚫 ليس لديك صلاحية عرض المخازن"))
            return

        # ---------------- FILTER + EXPORT BAR ----------------
        bar = QtWidgets.QHBoxLayout()

        # بحث
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("بحث... (اسم المخزن، العنوان)")
        self.search_box.textChanged.connect(self.apply_filters)
        bar.addWidget(self.search_box)

        bar.addStretch()

        # EXPORT BUTTONS
        btn_pdf = QtWidgets.QPushButton("📄 PDF")
        btn_excel = QtWidgets.QPushButton("📊 Excel")
        btn_print = QtWidgets.QPushButton("🖨️ طباعة")

        btn_pdf.clicked.connect(self.export_pdf)
        btn_excel.clicked.connect(self.export_excel)
        btn_print.clicked.connect(self.print_page)

        bar.addWidget(btn_pdf)
        bar.addWidget(btn_excel)
        bar.addWidget(btn_print)

        layout.addLayout(bar)

        # ---------------- TABLE ----------------
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "اسم المخزن", "العنوان"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        layout.addWidget(self.table)

        # زر إضافة مخزن (لو مسموح)
        if self.permissions.get("add"):
            btn_add = QtWidgets.QPushButton("➕ إضافة مخزن")
            btn_add.clicked.connect(self.add_warehouse_dialog)
            layout.addWidget(btn_add)

    # ===============================================================
    # LOAD WAREHOUSES
    # ===============================================================
    def load_warehouses(self):
        self.warehouses = self.db.get_warehouses()
        self.refresh_table(self.warehouses)

    # ===============================================================
    def refresh_table(self, data):
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(row["name"]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(row["location"]))

    # ===============================================================
    # FILTER
    # ===============================================================
    def apply_filters(self):
        search = self.search_box.text().strip()

        filtered = []

        for wh in self.warehouses:
            if search:
                if (search not in wh["name"] and search not in wh["location"]):
                    continue
            filtered.append(wh)

        self.refresh_table(filtered)

    # ===============================================================
    # EXPORT PDF
    # ===============================================================
    def export_pdf(self):
        data = self.collect_table_data()
        if not data:
            QtWidgets.QMessageBox.warning(self, "⚠", "لا توجد بيانات للتصدير")
            return

        file_path = self.reporter.export_pdf(
            data_list=data,
            columns=["id", "name", "location"],
            filename="warehouses_report",
            report_title="Warehouses Report",
            date_from="N/A",
            date_to="N/A"
        )

        QtWidgets.QMessageBox.information(self, "✔", f"PDF تم إنشاؤه:\n{file_path}")

    # ===============================================================
    # EXPORT EXCEL
    # ===============================================================
    def export_excel(self):
        data = self.collect_table_data()
        if not data:
            QtWidgets.QMessageBox.warning(self, "⚠", "لا توجد بيانات للتصدير")
            return

        file_path = self.reporter.export_excel(
            data_list=data,
            columns=["id", "name", "location"],
            filename="warehouses_report",
            report_title="Warehouses Report",
            date_from="N/A",
            date_to="N/A"
        )

        QtWidgets.QMessageBox.information(self, "✔", f"Excel تم حفظه:\n{file_path}")

    # ===============================================================
    # PRINT PAGE
    # ===============================================================
    def print_page(self):
        self.reporter.print_report(self.table)

    # ===============================================================
    # Collect Data
    # ===============================================================
    def collect_table_data(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()

        headers = ["id", "name", "location"]

        data = []

        for r in range(rows):
            entry = {}
            for c in range(cols):
                item = self.table.item(r, c)
                entry[headers[c]] = item.text() if item else ""
            data.append(entry)

        return data

    # ===============================================================
    # ADD WAREHOUSE
    # ===============================================================
    def add_warehouse_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("إضافة مخزن")
        dialog.setLayout(QtWidgets.QFormLayout())

        name = QtWidgets.QLineEdit()
        location = QtWidgets.QLineEdit()

        dialog.layout().addRow("اسم المخزن:", name)
        dialog.layout().addRow("العنوان:", location)

        btn_add = QtWidgets.QPushButton("✔ إضافة")
        btn_add.clicked.connect(lambda: self.save_new_warehouse(dialog, name, location))

        dialog.layout().addWidget(btn_add)
        dialog.exec_()

    # ===============================================================
    def save_new_warehouse(self, dialog, name, location):
        if not name.text().strip():
            QtWidgets.QMessageBox.warning(self, "⚠", "اسم المخزن مطلوب")
            return

        self.db.add_warehouse(name.text().strip(), location.text().strip())

        dialog.close()
        QtWidgets.QMessageBox.information(self, "✔", "تم إضافة المخزن بنجاح")
        self.load_warehouses()
