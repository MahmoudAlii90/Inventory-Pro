from PyQt5 import QtWidgets, QtCore
from utils.db_manager import DatabaseManager
from ui.global_signals import global_signals


class UsersPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.db = DatabaseManager()
        self.permissions = permissions

        self.roles = []
        self.users = []

        self.build_ui()
        self.load_roles()
        self.load_users()

    # ================= UI =================
    def build_ui(self):

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("👤 إدارة المستخدمين")
        title.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
            color:#0A3D91;
            margin-bottom:15px;
        """)
        layout.addWidget(title)

        form = QtWidgets.QFormLayout()

        self.in_user = QtWidgets.QLineEdit()
        self.in_pass = QtWidgets.QLineEdit()
        self.in_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.in_name = QtWidgets.QLineEdit()
        self.cb_roles = QtWidgets.QComboBox()

        form.addRow("اسم المستخدم:", self.in_user)
        form.addRow("كلمة المرور:", self.in_pass)
        form.addRow("الاسم الكامل:", self.in_name)
        form.addRow("الدور:", self.cb_roles)

        frame = QtWidgets.QFrame()
        frame.setStyleSheet("background:white; border-radius:10px; padding:10px;")
        f_lay = QtWidgets.QVBoxLayout(frame)
        f_lay.addLayout(form)

        layout.addWidget(frame)

        btns = QtWidgets.QHBoxLayout()
        btn_add = QtWidgets.QPushButton("➕ إضافة")
        btn_del = QtWidgets.QPushButton("🗑 حذف")

        btn_add.clicked.connect(self.add_user)
        btn_del.clicked.connect(self.delete_user)

        btns.addWidget(btn_add)
        btns.addWidget(btn_del)
        btns.addStretch()
        layout.addLayout(btns)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "المستخدم", "الاسم الكامل", "الدور", "إنشاء", "تعديل"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    # ================= LOAD =================
    def load_roles(self):
        self.cb_roles.clear()
        self.roles = self.db.get_roles()
        self.role_map = {}

        for r in self.roles:
            self.cb_roles.addItem(r["name"])
            self.role_map[r["name"]] = r["id"]

    def load_users(self):
        self.users = self.db.get_users()
        self.table.setRowCount(len(self.users))

        for i, u in enumerate(self.users):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(u["id"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(u["username"]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(u["full_name"]))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(u["role_name"]))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(u["created_at"]))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(u["updated_at"]))

    # ================= ADD =================
    def add_user(self):
        username = self.in_user.text()
        password = self.in_pass.text()
        fullname = self.in_name.text()
        role_name = self.cb_roles.currentText()
        role_id = self.role_map[role_name]

        self.db.add_user(username, password, fullname, role_id)
        global_signals.data_changed.emit()

        self.in_user.clear()
        self.in_pass.clear()
        self.in_name.clear()

        self.load_users()

    # ================= DELETE =================
    def delete_user(self):
        row = self.table.currentRow()
        if row < 0:
            return

        uid = int(self.table.item(row, 0).text())
        self.db.delete_user(uid)

        global_signals.data_changed.emit()

        self.load_users()
