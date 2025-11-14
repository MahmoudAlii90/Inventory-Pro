from PyQt5 import QtWidgets, QtCore, QtGui

# صفحات البرنامج
from ui.dashboard_page import DashboardPage
from ui.items_page import ItemsPage
from ui.warehouses_page import WarehousesPage
from ui.partners_page import PartnersPage
from ui.transactions_page import TransactionsPage
from ui.users_page import UsersPage
from ui.roles_manager_window import RolesManagerWindow
from ui.activity_log_page import ActivityLogPage
from ui.reports_page import ReportsPage
from ui.backup_page import BackupPage
from ui.price_list_page import PriceListPage
from ui.sales_page import SalesPage
from ui.purchases_page import PurchasesPage
from ui.sales_viewer import SalesViewer
from ui.purchases_viewer import PurchasesViewer
from ui.profit_analytics_page import ProfitAnalyticsPage

from utils.global_signals import global_signals


class MainWindow(QtWidgets.QMainWindow):
    logout_requested = QtCore.pyqtSignal()

    def __init__(self, username, role, permissions):
        super().__init__()

        self.username = username
        self.role = role
        self.permissions = permissions

        self.setWindowTitle("Inventory Pro — by Mahmoud Ali")
        self.setMinimumSize(1500, 900)

        self.build_ui()
        self.showMaximized()

    # ============================================================
    def build_ui(self):
        main = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(main)
        layout.setContentsMargins(0, 0, 0, 0)

        # ----------- Side Menu -----------
        self.menu = self.build_menu()
        layout.addWidget(self.menu)

        # ----------- Main Pages -----------
        self.pages = QtWidgets.QStackedWidget()
        layout.addWidget(self.pages, stretch=1)

        self.setCentralWidget(main)
        self.load_pages()

    # ============================================================
    def build_menu(self):
        menu = QtWidgets.QFrame()
        menu.setFixedWidth(270)

        menu.setStyleSheet("""
            QFrame {
                background-color: #0A3D91;
            }
            QPushButton {
                padding: 14px;
                font-size: 17px;
                border: none;
                color: white;
                text-align: right;
                border-radius: 6px;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: #0D4FB1;
            }
            QPushButton:checked {
                background-color: #08407A;
                font-weight: bold;
                border-left: 4px solid #21d4fd;
            }
            QLabel {
                color: white;
            }
        """)

        v = QtWidgets.QVBoxLayout(menu)
        v.setAlignment(QtCore.Qt.AlignTop)

        # ----------- User Info -----------
        user_box = QtWidgets.QVBoxLayout()
        lbl_user = QtWidgets.QLabel(f"👤 {self.username}")
        lbl_user.setStyleSheet("font-size: 20px; font-weight: bold; margin-top:20px; margin-left:10px;")

        lbl_role = QtWidgets.QLabel(f"🎖 {self.role}")
        lbl_role.setStyleSheet("font-size: 14px; margin-left:10px; margin-bottom: 20px;")

        user_box.addWidget(lbl_user)
        user_box.addWidget(lbl_role)
        v.addLayout(user_box)

        self.btns = {}

        # ----------- Helper function -----------
        def add_btn(text, icon, page_index, perm):
            if perm.get("view", 0):
                btn = QtWidgets.QPushButton(f"{icon}   {text}")
                btn.setCheckable(True)
                btn.clicked.connect(lambda: self.switch_page(btn, page_index))
                v.addWidget(btn)
                self.btns[text] = btn

        # ----------- Menu Buttons -----------
        add_btn("الرئيسية", "🏠", 0, self.permissions["dashboard"])
        add_btn("الأصناف", "📦", 1, self.permissions["items"])
        add_btn("المخازن", "🏭", 2, self.permissions["warehouses"])
        add_btn("الموردين والعملاء", "👥", 3, self.permissions["partners"])
        add_btn("الأذونات", "📑", 4, self.permissions["transactions"])
        add_btn("قائمة الأسعار", "💲", 5, self.permissions["price_list"])
        add_btn("المبيعات", "🛒 فاتورة بيع", 6, self.permissions["sales"])
        add_btn("مشاهد المبيعات", "📘", 7, self.permissions["sales"])
        add_btn("المشتريات", "📥 فاتورة شراء", 8, self.permissions["purchases"])
        add_btn("مشاهد المشتريات", "📗", 9, self.permissions["purchases"])
        add_btn("تحليل الأرباح", "📊", 10, self.permissions["profit"])
        add_btn("التقارير", "📘", 11, self.permissions["reports"])
        add_btn("سجل النشاط", "📝", 12, self.permissions["activity"])
        add_btn("النسخ الاحتياطي", "🛡", 13, self.permissions["backup"])
        add_btn("إدارة المستخدمين", "👤", 14, self.permissions["users"])
        add_btn("الصلاحيات", "🔐", 15, self.permissions["roles"])

        # ----------- Logout -----------
        btn_logout = QtWidgets.QPushButton("🚪 تسجيل خروج")
        btn_logout.clicked.connect(self.logout)
        btn_logout.setStyleSheet("margin-top: 40px; background:#DC3545;")
        v.addWidget(btn_logout)

        v.addStretch()
        return menu

    # ============================================================
    def switch_page(self, btn, index):
        for b in self.btns.values():
            b.setChecked(False)

        btn.setChecked(True)
        self.pages.setCurrentIndex(index)

    # ============================================================
    def load_pages(self):
        self.pages.addWidget(DashboardPage(self.permissions["dashboard"]))      # 0
        self.pages.addWidget(ItemsPage(self.permissions["items"]))              # 1
        self.pages.addWidget(WarehousesPage(self.permissions["warehouses"]))    # 2
        self.pages.addWidget(PartnersPage(self.permissions["partners"]))        # 3
        self.pages.addWidget(TransactionsPage(self.username,
                               self.permissions["transactions"]))              # 4
        self.pages.addWidget(PriceListPage(self.permissions["price_list"]))     # 5
        self.pages.addWidget(SalesPage(self.username, 
                               self.permissions["sales"]))                     # 6
        self.pages.addWidget(SalesViewer(self.permissions["sales"]))            # 7
        self.pages.addWidget(PurchasesPage(self.username,
                               self.permissions["purchases"]))                 # 8
        self.pages.addWidget(PurchasesViewer(self.permissions["purchases"]))    # 9
        self.pages.addWidget(ProfitAnalyticsPage(self.permissions["profit"]))   # 10
        self.pages.addWidget(ReportsPage(self.permissions["reports"]))          # 11
        self.pages.addWidget(ActivityLogPage(self.permissions["activity"]))     # 12
        self.pages.addWidget(BackupPage(self.permissions["backup"]))            # 13
        self.pages.addWidget(UsersPage(self.permissions["users"]))              # 14
        self.pages.addWidget(QtWidgets.QLabel("إدارة الصلاحيات من القائمة"))  # 15

    # ============================================================
    def logout(self):
        self.logout_requested.emit()
