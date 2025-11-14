from PyQt5 import QtWidgets, QtGui, QtCore
from utils.db_manager import DatabaseManager

class UserManagerWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("👥 إدارة المستخدمين")
        self.setFixedSize(850, 550)
        self.db = DatabaseManager()
        self.users = []
        self.roles = self.db.get_roles()
        self.build_ui()
        self.load_users()

    def build_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #E8EEF7; font-family: 'Cairo'; }
            QLineEdit, QComboBox {
                background-color: #fff;
                border: 1px solid #0A3D91;
                border-radius: 6px;
                padding: 4px;
                color: #000;
            }
            QPushButton {
                background-color: #0A3D91;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover { background-color: #257CFF; }
            QLabel { color: #0A3D91; font-weight: bold; }
        """)

        layout = QtWidgets.QVBoxLayout(self)

        # ==== البحث ====
        search_layout = QtWidgets.QHBoxLayout()
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("🔍 ابحث عن مستخدم بالاسم أو البريد...")
        self.search_box.textChanged.connect(self.filter_users)
        btn_add = QtWidgets.QPushButton("➕ إضافة مستخدم جديد")
        btn_add.clicked.connect(self.add_user_dialog)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(btn_add)

        # ==== الجدول ====
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["الاسم", "البريد الإلكتروني", "الدور", "تاريخ الإنشاء", "✏️ تعديل", "🔑 كلمة المرور", "🗑️ حذف"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)

        layout.addLayout(search_layout)
        layout.addWidget(self.table)

    # ============================================================
    # تحميل / تصفية المستخدمين
    # ============================================================
    def load_users(self):
        self.users = self.db.get_users()
        self.refresh_table(self.users)

    def refresh_table(self, data):
        self.table.setRowCount(len(data))
        for i, u in enumerate(data):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(u["username"]))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(u["email"] or ""))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(u["role_name"] or "غير محدد"))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(u["created_at"] or ""))

            # زر تعديل
            edit_btn = QtWidgets.QPushButton("✏️")
            edit_btn.clicked.connect(lambda _, r=i: self.edit_user_dialog(data[r]))
            self.table.setCellWidget(i, 4, edit_btn)

            # زر تغيير كلمة المرور
            pass_btn = QtWidgets.QPushButton("🔑")
            pass_btn.clicked.connect(lambda _, r=i: self.change_password_dialog(data[r]["id"]))
            self.table.setCellWidget(i, 5, pass_btn)

            # زر حذف
            del_btn = QtWidgets.QPushButton("🗑️")
            del_btn.clicked.connect(lambda _, r=i: self.delete_user(data[r]["id"]))
            self.table.setCellWidget(i, 6, del_btn)

    def filter_users(self, text):
        filtered = []
        for u in self.users:
            if text.lower() in u["username"].lower() or text.lower() in (u["email"] or "").lower():
                filtered.append(u)
        self.refresh_table(filtered)

    # ============================================================
    # إضافة مستخدم جديد
    # ============================================================
    def add_user_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("➕ إضافة مستخدم جديد")
        dialog.setFixedSize(400, 300)
        form = QtWidgets.QFormLayout()

        name = QtWidgets.QLineEdit()
        email = QtWidgets.QLineEdit()
        password = QtWidgets.QLineEdit()
        password.setEchoMode(QtWidgets.QLineEdit.Password)
        role = QtWidgets.QComboBox()
        for r in self.roles:
            role.addItem(r["name"], r["id"])

        form.addRow("اسم المستخدم:", name)
        form.addRow("البريد الإلكتروني:", email)
        form.addRow("كلمة المرور:", password)
        form.addRow("الدور:", role)
        btn_save = QtWidgets.QPushButton("💾 حفظ")
        form.addWidget(btn_save)

        dialog.setLayout(form)
        btn_save.clicked.connect(lambda: self.save_new_user(dialog, name, email, password, role))
        dialog.exec_()

    def save_new_user(self, dialog, name, email, password, role):
        try:
            n = name.text().strip()
            e = email.text().strip()
            p = password.text().strip()
            r = role.currentData()
            if not n or not p:
                raise ValueError("الاسم وكلمة المرور مطلوبان.")
            self.db.add_user(n, p, r, e)
            QtWidgets.QMessageBox.information(self, "تم", "✅ تمت إضافة المستخدم بنجاح.")
            dialog.close()
            self.load_users()
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self, "خطأ", f"حدث خطأ أثناء الإضافة:\n{ex}")

    # ============================================================
    # تعديل مستخدم
    # ============================================================
    def edit_user_dialog(self, user):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("✏️ تعديل بيانات المستخدم")
        dialog.setFixedSize(400, 300)
        form = QtWidgets.QFormLayout()

        name = QtWidgets.QLineEdit(user["username"])
        email = QtWidgets.QLineEdit(user["email"])
        role = QtWidgets.QComboBox()
        for r in self.roles:
            role.addItem(r["name"], r["id"])
            if r["name"] == user["role_name"]:
                role.setCurrentText(r["name"])

        form.addRow("اسم المستخدم:", name)
        form.addRow("البريد الإلكتروني:", email)
        form.addRow("الدور:", role)
        btn_save = QtWidgets.QPushButton("💾 حفظ التعديل")
        form.addWidget(btn_save)

        dialog.setLayout(form)
        btn_save.clicked.connect(lambda: self.save_user_edit(dialog, user["id"], name, email, role))
        dialog.exec_()

    def save_user_edit(self, dialog, uid, name, email, role):
        try:
            self.db.update_user(uid, name.text().strip(), email.text().strip(), role.currentData())
            QtWidgets.QMessageBox.information(self, "تم", "✅ تم تعديل المستخدم بنجاح.")
            dialog.close()
            self.load_users()
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self, "خطأ", f"تعذر التعديل:\n{ex}")

    # ============================================================
    # تغيير كلمة المرور
    # ============================================================
    def change_password_dialog(self, user_id):
        new_pass, ok = QtWidgets.QInputDialog.getText(self, "تغيير كلمة المرور", "كلمة المرور الجديدة:", QtWidgets.QLineEdit.Password)
        if ok and new_pass.strip():
            self.db.change_password(user_id, new_pass.strip())
            QtWidgets.QMessageBox.information(self, "تم", "🔑 تم تغيير كلمة المرور بنجاح.")

    # ============================================================
    # حذف مستخدم
    # ============================================================
    def delete_user(self, user_id):
        confirm = QtWidgets.QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف هذا المستخدم؟",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            self.db.delete_user(user_id)
            self.load_users()
            QtWidgets.QMessageBox.information(self, "تم", "🗑️ تم حذف المستخدم.")
