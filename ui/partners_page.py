from PyQt5 import QtWidgets, QtGui, QtCore

from utils.db_manager import DatabaseManager
from utils.report_utils import ReportUtils


class PartnersPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions.get("partners", {"view": 1})
        self.reporter = ReportUtils()

        self.suppliers = []
        self.customers = []

        self.build_ui()
        self.load_suppliers()
        self.load_customers()

    # ===============================================================
    # BUILD UI
    # ===============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("🤝 الموردين و العملاء")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Cairo", 20, QtGui.QFont.Bold))
        title.setStyleSheet("color:#0A3D91; margin-bottom: 10px;")
        layout.addWidget(title)

        if not self.permissions.get("view"):
            layout.addWidget(QtWidgets.QLabel("🚫 ليس لديك صلاحية عرض الموردين / العملاء"))
            return

        # ---------------- Tabs ----------------
        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)

        # Suppliers Tab
        self.suppliers_tab = QtWidgets.QWidget()
        self.build_suppliers_tab()
        self.tabs.addTab(self.suppliers_tab, "📦 الموردين")

        # Customers Tab
        self.customers_tab = QtWidgets.QWidget()
        self.build_customers_tab()
        self.tabs.addTab(self.customers_tab, "👥 العملاء")

    # ===============================================================
    # SUPPLIERS TAB
    # ===============================================================
    def build_suppliers_tab(self):
        layout = QtWidgets.QVBoxLayout(self.suppliers_tab)

        bar = QtWidgets.QHBoxLayout()

        # Search bar
        self.sup_search = QtWidgets.QLineEdit()
        self.sup_search.setPlaceholderText("بحث...")
        self.sup_search.textChanged.connect(self.filter_suppliers)
        bar.addWidget(self.sup_search)

        bar.addStretch()

        # Export buttons
        btn_pdf = QtWidgets.QPushButton("📄 PDF")
        btn_excel = QtWidgets.QPushButton("📊 Excel")
        btn_print = QtWidgets.QPushButton("🖨️ طباعة")

        btn_pdf.clicked.connect(self.export_suppliers_pdf)
        btn_excel.clicked.connect(self.export_suppliers_excel)
        btn_print.clicked.connect(self.print_suppliers)

        bar.addWidget(btn_pdf)
        bar.addWidget(btn_excel)
        bar.addWidget(btn_print)

        layout.addLayout(bar)

        # ---------------- Suppliers Table ----------------
        self.sup_table = QtWidgets.QTableWidget()
        self.sup_table.setColumnCount(4)
        self.sup_table.setHorizontalHeaderLabels(["ID", "الاسم", "التليفون", "العنوان"])
        self.sup_table.horizontalHeader().setStretchLastSection(True)
        self.sup_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        layout.addWidget(self.sup_table)

        if self.permissions.get("add"):
            btn_add = QtWidgets.QPushButton("➕ إضافة مورد")
            btn_add.clicked.connect(self.add_supplier_dialog)
            layout.addWidget(btn_add)

    # ===============================================================
    # CUSTOMERS TAB
    # ===============================================================
    def build_customers_tab(self):
        layout = QtWidgets.QVBoxLayout(self.customers_tab)

        bar = QtWidgets.QHBoxLayout()

        # Search bar
        self.cus_search = QtWidgets.QLineEdit()
        self.cus_search.setPlaceholderText("بحث...")
        self.cus_search.textChanged.connect(self.filter_customers)
        bar.addWidget(self.cus_search)

        bar.addStretch()

        # Export buttons
        btn_pdf = QtWidgets.QPushButton("📄 PDF")
        btn_excel = QtWidgets.QPushButton("📊 Excel")
        btn_print = QtWidgets.QPushButton("🖨️ طباعة")

        btn_pdf.clicked.connect(self.export_customers_pdf)
        btn_excel.clicked.connect(self.export_customers_excel)
        btn_print.clicked.connect(self.print_customers)

        bar.addWidget(btn_pdf)
        bar.addWidget(btn_excel)
        bar.addWidget(btn_print)

        layout.addLayout(bar)

        # ---------------- Customers Table ----------------
        self.cus_table = QtWidgets.QTableWidget()
        self.cus_table.setColumnCount(4)
        self.cus_table.setHorizontalHeaderLabels(["ID", "الاسم", "التليفون", "العنوان"])
        self.cus_table.horizontalHeader().setStretchLastSection(True)
        self.cus_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        layout.addWidget(self.cus_table)

        if self.permissions.get("add"):
            btn_add = QtWidgets.QPushButton("➕ إضافة عميل")
            btn_add.clicked.connect(self.add_customer_dialog)
            layout.addWidget(btn_add)

    # ===============================================================
    # LOAD DATA
    # ===============================================================
    def load_suppliers(self):
        self.suppliers = self.db.get_suppliers()
        self.refresh_suppliers(self.suppliers)

    def load_customers(self):
        self.customers = self.db.get_customers()
        self.refresh_customers(self.customers)

    # ===============================================================
    def refresh_suppliers(self, data):
        self.sup_table.setRowCount(len(data))

        for i, row in enumerate(data):
            self.sup_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.sup_table.setItem(i, 1, QtWidgets.QTableWidgetItem(row["name"]))
            self.sup_table.setItem(i, 2, QtWidgets.QTableWidgetItem(row["phone"]))
            self.sup_table.setItem(i, 3, QtWidgets.QTableWidgetItem(row["address"]))

    def refresh_customers(self, data):
        self.cus_table.setRowCount(len(data))

        for i, row in enumerate(data):
            self.cus_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.cus_table.setItem(i, 1, QtWidgets.QTableWidgetItem(row["name"]))
            self.cus_table.setItem(i, 2, QtWidgets.QTableWidgetItem(row["phone"]))
            self.cus_table.setItem(i, 3, QtWidgets.QTableWidgetItem(row["address"]))

    # ===============================================================
    # FILTER
    # ===============================================================
    def filter_suppliers(self):
        text = self.sup_search.text().strip()
        filtered = []

        for row in self.suppliers:
            if text in row["name"] or text in row["phone"] or text in row["address"]:
                filtered.append(row)

        self.refresh_suppliers(filtered)

    def filter_customers(self):
        text = self.cus_search.text().strip()
        filtered = []

        for row in self.customers:
            if text in row["name"] or text in row["phone"] or text in row["address"]:
                filtered.append(row)

        self.refresh_customers(filtered)

    # ===============================================================
    # EXPORT SUPPLIERS
    # ===============================================================
    def export_suppliers_pdf(self):
        data = self.table_to_list(self.sup_table, ["id", "name", "phone", "address"])
        if not data:
            QtWidgets.QMessageBox.warning(self, "⚠", "لا يوجد بيانات للتصدير")
            return

        file_path = self.reporter.export_pdf(
            data_list=data,
            columns=["id", "name", "phone", "address"],
            filename="suppliers_report",
            report_title="Suppliers Report",
            date_from="N/A",
            date_to="N/A"
        )
        QtWidgets.QMessageBox.information(self, "✔", f"PDF تم إنشاؤه:\n{file_path}")

    def export_suppliers_excel(self):
        data = self.table_to_list(self.sup_table, ["id", "name", "phone", "address"])
        if not data:
            QtWidgets.QMessageBox.warning(self, "⚠", "لا يوجد بيانات للتصدير")
            return

        file_path = self.reporter.export_excel(
            data_list=data,
            columns=["id", "name", "phone", "address"],
            filename="suppliers_report",
            report_title="Suppliers Report",
            date_from="N/A",
            date_to="N/A"
        )
        QtWidgets.QMessageBox.information(self, "✔", f"Excel تم حفظه:\n{file_path}")

    def print_suppliers(self):
        self.reporter.print_report(self.sup_table)

    # ===============================================================
    # EXPORT CUSTOMERS
    # ===============================================================
    def export_customers_pdf(self):
        data = self.table_to_list(self.cus_table, ["id", "name", "phone", "address"])
        if not data:
            QtWidgets.QMessageBox.warning(self, "⚠", "لا يوجد بيانات للتصدير")
            return

        file_path = self.reporter.export_pdf(
            data_list=data,
            columns=["id", "name", "phone", "address"],
            filename="customers_report",
            report_title="Customers Report",
            date_from="N/A",
            date_to="N/A"
        )
        QtWidgets.QMessageBox.information(self, "✔", f"PDF تم إنشاؤه:\n{file_path}")

    def export_customers_excel(self):
        data = self.table_to_list(self.cus_table, ["id", "name", "phone", "address"])
        if not data:
            QtWidgets.QMessageBox.warning(self, "⚠", "لا يوجد بيانات للتصدير")
            return

        file_path = self.reporter.export_excel(
            data_list=data,
            columns=["id", "name", "phone", "address"],
            filename="customers_report",
            report_title="Customers Report",
            date_from="N/A",
            date_to="N/A"
        )
        QtWidgets.QMessageBox.information(self, "✔", f"Excel تم حفظه:\n{file_path}")

    def print_customers(self):
        self.reporter.print_report(self.cus_table)

    # ===============================================================
    # Utility: Convert table to list of dicts
    # ===============================================================
    def table_to_list(self, table, headers):
        data = []

        rows = table.rowCount()
        cols = table.columnCount()

        for r in range(rows):
            entry = {}
            for c in range(cols):
                item = table.item(r, c)
                entry[headers[c]] = item.text() if item else ""
            data.append(entry)

        return data

    # ===============================================================
    # ADD SUPPLIER
    # ===============================================================
    def add_supplier_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("إضافة مورد")
        dialog.setLayout(QtWidgets.QFormLayout())

        name = QtWidgets.QLineEdit()
        phone = QtWidgets.QLineEdit()
        address = QtWidgets.QLineEdit()

        dialog.layout().addRow("الاسم:", name)
        dialog.layout().addRow("التليفون:", phone)
        dialog.layout().addRow("العنوان:", address)

        btn_add = QtWidgets.QPushButton("✔ إضافة")
        btn_add.clicked.connect(lambda: self.save_new_supplier(dialog, name, phone, address))

        dialog.layout().addWidget(btn_add)
        dialog.exec_()

    def save_new_supplier(self, dialog, name, phone, address):
        if not name.text().strip():
            QtWidgets.QMessageBox.warning(self, "⚠", "اسم المورد مطلوب")
            return

        self.db.add_supplier(name.text().strip(), phone.text().strip(), address.text().strip())
        dialog.close()

        QtWidgets.QMessageBox.information(self, "✔", "تم إضافة المورد بنجاح")
        self.load_suppliers()

    # ===============================================================
    # ADD CUSTOMER
    # ===============================================================
    def add_customer_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("إضافة عميل")
        dialog.setLayout(QtWidgets.QFormLayout())

        name = QtWidgets.QLineEdit()
        phone = QtWidgets.QLineEdit()
        address = QtWidgets.QLineEdit()

        dialog.layout().addRow("الاسم:", name)
        dialog.layout().addRow("التليفون:", phone)
        dialog.layout().addRow("العنوان:", address)

        btn_add = QtWidgets.QPushButton("✔ إضافة")
        btn_add.clicked.connect(lambda: self.save_new_customer(dialog, name, phone, address))

        dialog.layout().addWidget(btn_add)
        dialog.exec_()

    def save_new_customer(self, dialog, name, phone, address):
        if not name.text().strip():
            QtWidgets.QMessageBox.warning(self, "⚠", "اسم العميل مطلوب")
            return

        self.db.add_customer(name.text().strip(), phone.text().strip(), address.text().strip())
        dialog.close()

        QtWidgets.QMessageBox.information(self, "✔", "تم إضافة العميل بنجاح")
        self.load_customers()
