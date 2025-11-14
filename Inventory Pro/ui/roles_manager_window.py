from PyQt5 import QtWidgets, QtGui, QtCore
from utils.db_manager import DatabaseManager
import json


class RolesManagerWindow(QtWidgets.QDialog):

    def __init__(self, parent, permissions):
        super().__init__(parent)

        self.db = DatabaseManager()
        self.permissions = permissions.get("roles", {
            "view": 1,
            "add": 1,
            "edit": 1,
            "delete": 1
        })

        self.setWindowTitle("إدارة الصلاحيات والأدوار")
        self.resize(800, 600)
        self.setStyleSheet("font-family: Cairo;")

        self.build_ui()
        self.load_roles()

    # ---------------------------------------------------------------
    def build_ui(self):

        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("إدارة الأدوار والصلاحيات")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Cairo", 18, QtGui.QFont.Bold))
        title.setStyleSheet("color:#0A3D91; margin:10px;")
        layout.addWidget(title)

        # جدول الأدوار
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "اسم الدور"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        btns = QtWidgets.QHBoxLayout()

        self.btn_add = QtWidgets.QPushButton("➕ إضافة دور")
        self.btn_edit = QtWidgets.QPushButton("📝 تعديل")
        self.btn_delete = QtWidgets.QPushButton("🗑 حذف")
        self.btn_close = QtWidgets.QPushButton("❌ إغلاق")

        if not self.permissions.get("add"): self.btn_add.setVisible(False)
        if not self.permissions.get("edit"): self.btn_edit.setVisible(False)
        if not self.permissions.get("delete"): self.btn_delete.setVisible(False)

        self.btn_add.clicked.connect(self.add_role)
        self.btn_edit.clicked.connect(self.edit_role)
        self.btn_delete.clicked.connect(self.delete_role)
        self.btn_close.clicked.connect(self.close)

        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_delete)
        btns.addWidget(self.btn_close)

        layout.addLayout(btns)

    # ---------------------------------------------------------------
    def load_roles(self):
        roles = self.db.get_roles()

        self.table.setRowCount(len(roles))
        for i, r in enumerate(roles):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(r["id"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(r["name"]))

    # ---------------------------------------------------------------
    def add_role(self):
        dlg = RoleEditDialog(self)
        if dlg.exec_():
            name, perms = dlg.get_result()
            self.db.add_role(name, perms)
            self.load_roles()

    # ---------------------------------------------------------------
    def edit_role(self):
        row = self.table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "خطأ", "اختر دور أولاً")
            return

        role_id = int(self.table.item(row, 0).text())

        roles = self.db.get_roles()
        role = next((r for r in roles if r["id"] == role_id), None)

        if role is None:
            return

        dlg = RoleEditDialog(self, role)
        if dlg.exec_():
            name, perms = dlg.get_result()
            self.db.update_role(role_id, name, perms)
            self.load_roles()

    # ---------------------------------------------------------------
    def delete_role(self):
        row = self.table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "خطأ", "اختر دور أولاً")
            return

        role_id = int(self.table.item(row, 0).text())

        c = QtWidgets.QMessageBox.question(
            self, "تأكيد", "هل تريد حذف هذا الدور؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if c == QtWidgets.QMessageBox.Yes:
            self.db.delete_role(role_id)
            self.load_roles()


# ===============================================================
# نافذة تعديل الصلاحيات
# ===============================================================

class RoleEditDialog(QtWidgets.QDialog):
    def __init__(self, parent, role=None):
        super().__init__(parent)

        self.role = role
        self.setWindowTitle("تعديل الصلاحيات")
        self.resize(550, 500)

        self.sections = [
            "dashboard", "items", "warehouses", "transactions",
            "partners", "users", "roles", "activity",
            "reports", "settings", "backup"
        ]

        self.build_ui()

        if role:
            self.load_role()

    # ---------------------------------------------------------------
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.name_input = QtWidgets.QLineEdit()
        layout.addWidget(QtWidgets.QLabel("اسم الدور:"))
        layout.addWidget(self.name_input)

        self.boxes = {}
        form = QtWidgets.QFormLayout()

        for sec in self.sections:
            container = QtWidgets.QHBoxLayout()

            v = QtWidgets.QCheckBox("عرض")
            a = QtWidgets.QCheckBox("إضافة")
            e = QtWidgets.QCheckBox("تعديل")
            d = QtWidgets.QCheckBox("حذف")
            x = QtWidgets.QCheckBox("مميزات خاصة")

            container.addWidget(v)
            container.addWidget(a)
            container.addWidget(e)
            container.addWidget(d)
            container.addWidget(x)

            form.addRow(sec + ":", container)

            self.boxes[sec] = {
                "view": v, "add": a, "edit": e, "delete": d, "extra": x
            }

        layout.addLayout(form)

        btn_save = QtWidgets.QPushButton("✔ حفظ")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

    # ---------------------------------------------------------------
    def load_role(self):
        self.name_input.setText(self.role["name"])

        perms = json.loads(self.role["permissions"])

        for sec in self.sections:
            if sec in perms:
                p = perms[sec]
                self.boxes[sec]["view"].setChecked(p["view"])
                self.boxes[sec]["add"].setChecked(p["add"])
                self.boxes[sec]["edit"].setChecked(p["edit"])
                self.boxes[sec]["delete"].setChecked(p["delete"])
                self.boxes[sec]["extra"].setChecked(p["extra"])

    # ---------------------------------------------------------------
    def get_result(self):
        name = self.name_input.text().strip()

        perms = {}
        for sec in self.sections:
            b = self.boxes[sec]
            perms[sec] = {
                "view": 1 if b["view"].isChecked() else 0,
                "add": 1 if b["add"].isChecked() else 0,
                "edit": 1 if b["edit"].isChecked() else 0,
                "delete": 1 if b["delete"].isChecked() else 0,
                "extra": 1 if b["extra"].isChecked() else 0
            }

        return name, perms
