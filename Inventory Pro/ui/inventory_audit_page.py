from PyQt5 import QtWidgets, QtCore, QtGui
from utils.db_manager import DatabaseManager
from utils.export_utils import Exporter
from ui.global_signals import global_signals


class InventoryAuditPage(QtWidgets.QWidget):
    def __init__(self, username, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.username = username
        self.permissions = permissions

        self.build_ui()
        self.load_data()

    # ===============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("📦 جرد المخزون — Inventory Audit")
        title.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
            color:#0A3D91;
        """)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        # ========================= FILTERS ==========================
        filter_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(filter_layout)

        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("🔍 بحث عن صنف...")
        self.search.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.search)

        self.filter_box = QtWidgets.QComboBox()
        self.filter_box.addItems([
            "الكل", "مطابق", "عجز", "زيادة"
        ])
        self.filter_box.currentIndexChanged.connect(self.filter_table)
        filter_layout.addWidget(self.filter_box)

        # ========================= TABLE ============================
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "الصنف", "الكمية الحالية", "الكمية الفعلية",
            "الفرق", "الحالة"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)

        layout.addWidget(self.table)

        # ========================= BUTTONS ============================
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.addLayout(btn_layout)

        self.btn_apply = QtWidgets.QPushButton("✔ تطبيق الجرد")
        self.btn_apply.setFixedWidth(200)
        self.btn_apply.clicked.connect(self.apply_audit)
        self.btn_apply.setStyleSheet("background:#0A3D91; color:white; padding:10px;")

        self.btn_export = QtWidgets.QPushButton("📄 تصدير تقرير PDF")
        self.btn_export.setFixedWidth(200)
        self.btn_export.clicked.connect(self.export_pdf)
        self.btn_export.setStyleSheet("background:#0A3D91; color:white; padding:10px;")

        # الصلاحيات
        if self.permissions.get("extra"):
            btn_layout.addWidget(self.btn_apply)
            btn_layout.addWidget(self.btn_export)
        else:
            # without adjustment rights → no action buttons
            pass

    # ===============================================================
    def load_data(self):
        items = self.db.get_items()

        self.raw_items = []
        for it in items:
            self.raw_items.append({
                "id": it["id"],
                "name": it["name"],
                "system_qty": it["quantity"],
                "actual_qty": it["quantity"],  # default = same
            })

        self.filter_table()

    # ===============================================================
    def filter_table(self):
        txt = self.search.text().strip().lower()
        status_filter = self.filter_box.currentText()

        filtered = []
        for item in self.raw_items:
            name = item["name"].lower()

            if txt and txt not in name:
                continue

            diff = item["actual_qty"] - item["system_qty"]

            if status_filter == "مطابق" and diff != 0:
                continue
            if status_filter == "عجز" and diff >= 0:
                continue
            if status_filter == "زيادة" and diff <= 0:
                continue

            filtered.append(item)

        self.refresh_table(filtered)

    # ===============================================================
    def refresh_table(self, items):
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            diff = item["actual_qty"] - item["system_qty"]

            # حالة الصنف
            if diff == 0:
                status = "مطابق"
            elif diff < 0:
                status = "عجز"
            else:
                status = "زيادة"

            # =========== Fill Table ===========
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item["id"])))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(item["name"]))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(item["system_qty"])))

            # editable cell
            actual_item = QtWidgets.QTableWidgetItem(str(item["actual_qty"]))
            actual_item.setFlags(actual_item.flags() | QtCore.Qt.ItemIsEditable)
            self.table.setItem(row, 3, actual_item)

            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(diff)))
            self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(status))

        self.table.itemChanged.connect(self.update_actual_qty)

    # ===============================================================
    def update_actual_qty(self, item):
        row = item.row()
        col = item.column()

        if col != 3:  # only actual_qty column
            return

        try:
            new_qty = int(item.text())
        except:
            QtWidgets.QMessageBox.warning(self, "⚠", "الكمية يجب أن تكون رقم صحيح.")
            return

        item_id = int(self.table.item(row, 0).text())

        # update in memory
        for original in self.raw_items:
            if original["id"] == item_id:
                original["actual_qty"] = new_qty
                break

        self.filter_table()

    # ===============================================================
    def apply_audit(self):
        if not self.permissions.get("extra"):
            QtWidgets.QMessageBox.warning(self, "🚫", "ليس لديك صلاحية تطبيق الجرد.")
            return

        confirm = QtWidgets.QMessageBox.question(
            self, "تأكيد",
            "هل تريد تطبيق الجرد وتحديث الكميات الفعلية؟"
        )
        if confirm != QtWidgets.QMessageBox.Yes:
            return

        for item in self.raw_items:
            item_id = item["id"]
            actual = item["actual_qty"]
            system = item["system_qty"]

            if actual != system:
                self.db.update_item_quantity(item_id, actual)
                self.db.log_audit_adjustment(self.username, item_id, system, actual)

        global_signals.data_changed.emit()

        QtWidgets.QMessageBox.information(self, "✔", "تم تطبيق الجرد بنجاح.")

        self.load_data()

    # ===============================================================
    def export_pdf(self):
        Exporter.export_inventory_audit_pdf(self.raw_items)
        QtWidgets.QMessageBox.information(self, "✔", "تم إنشاء تقرير الجرد.")        
