from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QPieSeries, QLineSeries, QBarCategoryAxis, QValueAxis
from utils.db_manager import DatabaseManager
from utils.export_utils import Exporter
from utils.global_signals import global_signals


class ProfitAnalyticsPage(QtWidgets.QWidget):
    def __init__(self, permissions):
        super().__init__()

        self.permissions = permissions
        self.db = DatabaseManager()

        self.sales = []
        self.purchases = []

        self.build_ui()
        self.load_data()

        # تحديث تلقائي عند تغيير أي بيانات
        global_signals.data_changed.connect(self.load_data)

    # ============================================================
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("📊 تحليل الأرباح")
        title.setStyleSheet("font-size:24px; font-weight:bold; color:#0A3D91; margin:10px;")
        layout.addWidget(title)

        # -------------------- فلترة التاريخ --------------------
        filter_box = QtWidgets.QHBoxLayout()

        self.from_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate().addMonths(-1))
        self.to_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.from_date.setCalendarPopup(True)
        self.to_date.setCalendarPopup(True)

        btn_filter = QtWidgets.QPushButton("🔍 تطبيق الفلتر")
        btn_filter.clicked.connect(self.apply_filter)

        filter_box.addWidget(QtWidgets.QLabel("من:"))
        filter_box.addWidget(self.from_date)
        filter_box.addWidget(QtWidgets.QLabel("إلى:"))
        filter_box.addWidget(self.to_date)
        filter_box.addWidget(btn_filter)

        layout.addLayout(filter_box)

        # ============================================================
        # كروت الأرقام الأساسية
        # ============================================================
        cards = QtWidgets.QHBoxLayout()

        self.lbl_total_sales = self.make_card("إجمالي المبيعات", "#198754")
        self.lbl_total_purchases = self.make_card("إجمالي المشتريات", "#dc3545")
        self.lbl_profit = self.make_card("صافي الربح", "#0d6efd")

        cards.addWidget(self.lbl_total_sales)
        cards.addWidget(self.lbl_total_purchases)
        cards.addWidget(self.lbl_profit)

        layout.addLayout(cards)

        # ============================================================
        # الرسوم البيانية
        # ============================================================
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        layout.addWidget(self.chart_view, stretch=1)

        # ============================================================
        # الأزرار
        # ============================================================
        btns = QtWidgets.QHBoxLayout()

        btn_export_pdf = QtWidgets.QPushButton("📄 تصدير PDF")
        btn_export_pdf.clicked.connect(self.export_pdf)

        btn_export_excel = QtWidgets.QPushButton("🟩 تصدير Excel")
        btn_export_excel.clicked.connect(self.export_excel)

        btns.addWidget(btn_export_pdf)
        btns.addWidget(btn_export_excel)
        btns.addStretch()

        layout.addLayout(btns)

    # ============================================================
    def make_card(self, title, color):
        frame = QtWidgets.QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 2px solid {color};
                padding: 10px;
            }}
        """)

        v = QtWidgets.QVBoxLayout(frame)
        lbl_title = QtWidgets.QLabel(title)
        lbl_title.setAlignment(QtCore.Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size:14px; font-weight:600;")

        lbl_value = QtWidgets.QLabel("0")
        lbl_value.setAlignment(QtCore.Qt.AlignCenter)
        lbl_value.setStyleSheet(f"font-size:24px; font-weight:bold; color:{color};")

        v.addWidget(lbl_title)
        v.addWidget(lbl_value)

        return frame

    # ============================================================
    def load_data(self):
        self.sales = self.db.get_sales_profit_data()
        self.purchases = self.db.get_purchase_cost_data()

        self.update_ui()

    # ============================================================
    def apply_filter(self):
        date_from = self.from_date.date().toString("yyyy-MM-dd")
        date_to = self.to_date.date().toString("yyyy-MM-dd")

        self.sales = self.db.get_sales_profit_data(date_from, date_to)
        self.purchases = self.db.get_purchase_cost_data(date_from, date_to)

        self.update_ui()

    # ============================================================
    def update_ui(self):
        # ---------- تجميع الأرقام ----------
        total_sales = sum(s["net_total"] for s in self.sales)
        total_purchases = sum(p["net_total"] for p in self.purchases)
        profit = total_sales - total_purchases

        # تحديث الكروت
        self.lbl_total_sales.findChildren(QtWidgets.QLabel)[1].setText(str(total_sales))
        self.lbl_total_purchases.findChildren(QtWidgets.QLabel)[1].setText(str(total_purchases))
        self.lbl_profit.findChildren(QtWidgets.QLabel)[1].setText(str(profit))

        # ---------- رسم الشارت ----------
        chart = QChart()
        chart.setTitle("📈 مقارنة الأرباح — المبيعات مقابل المشتريات")

        series = QBarSeries()

        set_sales = QBarSet("المبيعات")
        set_purchases = QBarSet("المشتريات")

        set_sales.append(total_sales)
        set_purchases.append(total_purchases)

        series.append(set_sales)
        series.append(set_purchases)

        chart.addSeries(series)
        chart.createDefaultAxes()

        chart.legend().setVisible(True)
        chart.legend().setAlignment(QtCore.Qt.AlignBottom)

        self.chart_view.setChart(chart)

    # ============================================================
    def export_pdf(self):
        Exporter.export_profit_pdf(self.sales, self.purchases)
        QtWidgets.QMessageBox.information(self, "✔", "تم تصدير PDF بنجاح.")

    # ============================================================
    def export_excel(self):
        Exporter.export_profit_excel(self.sales, self.purchases)
        QtWidgets.QMessageBox.information(self, "✔", "تم تصدير Excel بنجاح.")
