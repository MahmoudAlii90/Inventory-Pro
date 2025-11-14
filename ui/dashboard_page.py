# ui/dashboard_page.py

from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from ui.global_signals import global_signals


class DashboardPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions

        self.setStyleSheet("background:#F2F4F8; font-family:Cairo;")

        self.build_ui()
        self.load_data()

        # تحديث تلقائي
        global_signals.data_changed.connect(self.load_data)

    # =============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("📊 لوحة التحكم")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
            color:#0A3D91;
            margin-bottom:20px;
        """)
        layout.addWidget(title)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(20)
        layout.addLayout(grid)

        # === Panels ===
        def make_panel(label):
            frame = QtWidgets.QFrame()
            frame.setFixedSize(250, 110)
            frame.setStyleSheet("""
                QFrame {
                    background:white;
                    border-radius:12px;
                    border:1px solid #D0D7E3;
                }
            """)
            v = QtWidgets.QVBoxLayout(frame)
            v.setContentsMargins(5, 5, 5, 5)
            v.setAlignment(QtCore.Qt.AlignCenter)

            value = QtWidgets.QLabel("0")
            value.setAlignment(QtCore.Qt.AlignCenter)
            value.setStyleSheet("font-size:34px; font-weight:bold; color:#0A3D91;")

            text = QtWidgets.QLabel(label)
            text.setAlignment(QtCore.Qt.AlignCenter)
            text.setStyleSheet("color:#555; font-size:15px;")

            v.addWidget(value)
            v.addWidget(text)

            return frame, value

        self.pan_items, self.lbl_items = make_panel("عدد الأصناف")
        self.pan_low, self.lbl_low = make_panel("أصناف منخفضة")
        self.pan_wh, self.lbl_wh = make_panel("عدد المخازن")
        self.pan_sup, self.lbl_sup = make_panel("عدد الموردين")
        self.pan_cus, self.lbl_cus = make_panel("عدد العملاء")
        self.pan_sales, self.lbl_sales = make_panel("عدد فواتير المبيعات")
        self.pan_purch, self.lbl_purch = make_panel("عدد فواتير المشتريات")

        panels = [
            self.pan_items, self.pan_low, self.pan_wh,
            self.pan_sup, self.pan_cus, self.pan_sales, self.pan_purch
        ]

        row = col = 0
        for p in panels:
            grid.addWidget(p, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        # Recent Transactions
        recent_lbl = QtWidgets.QLabel("🧾 آخر 10 عمليات")
        recent_lbl.setStyleSheet("font-size:20px; font-weight:bold; margin-top:25px;")
        layout.addWidget(recent_lbl)

        self.table_recent = QtWidgets.QTableWidget()
        self.table_recent.setColumnCount(5)
        self.table_recent.setHorizontalHeaderLabels(
            ["ID", "النوع", "الصنف", "المستخدم", "الوقت"]
        )
        layout.addWidget(self.table_recent)

    # =============================================================
    def load_data(self):
        items = self.db.get_items()
        low = [i for i in items if i["quantity"] <= i["min_quantity"]]

        warehouses = self.db.get_warehouses()
        suppliers = self.db.get_suppliers()
        customers = self.db.get_customers()

        sales = self.db.get_sales_invoices()
        purchases = self.db.get_purchase_invoices()

        self.lbl_items.setText(str(len(items)))
        self.lbl_low.setText(str(len(low)))
        self.lbl_wh.setText(str(len(warehouses)))
        self.lbl_sup.setText(str(len(suppliers)))
        self.lbl_cus.setText(str(len(customers)))
        self.lbl_sales.setText(str(len(sales)))
        self.lbl_purch.setText(str(len(purchases)))

        # Recent
        all_ops = sales + purchases
        all_ops_sorted = sorted(all_ops, key=lambda x: x["id"], reverse=True)[:10]

        self.table_recent.setRowCount(len(all_ops_sorted))

        for i, op in enumerate(all_ops_sorted):
            self.table_recent.setItem(i, 0, QtWidgets.QTableWidgetItem(str(op["id"])))
            self.table_recent.setItem(i, 1, QtWidgets.QTableWidgetItem(op["type"]))
            self.table_recent.setItem(i, 2, QtWidgets.QTableWidgetItem(op["date"]))
            self.table_recent.setItem(i, 3, QtWidgets.QTableWidgetItem(op["user"]))
            self.table_recent.setItem(i, 4, QtWidgets.QTableWidgetItem(op["date"]))
