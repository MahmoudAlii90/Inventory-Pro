from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

import os


class PDFWriter:

    def __init__(self, company_name="", logo_path="", company_info=""):
        self.company_name = company_name
        self.logo_path = logo_path
        self.company_info = company_info

        # تحميل الخط العربي
        font_path = os.path.join("assets", "fonts", "Cairo-Regular.ttf")
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("Cairo", font_path))
            self.font_name = "Cairo"
        else:
            self.font_name = "Helvetica"

    # =========================================================
    def export_table(self, filename, title, headers, rows):
        """
        إنشاء تقرير PDF بالديزاين الاحترافي
        """

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        y = height - 60

        # ---------------------------------------------------------
        # اللوجو
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                c.drawImage(self.logo_path, 40, height - 120, width=90, preserveAspectRatio=True)
            except:
                pass

        # ---------------------------------------------------------
        # اسم الشركة
        c.setFont(self.font_name, 18)
        c.drawRightString(width - 40, height - 40, self.company_name)

        # ---------------------------------------------------------
        # معلومات الشركة
        c.setFont(self.font_name, 10)
        c.setFillColor(colors.darkgray)
        c.drawRightString(width - 40, height - 60, self.company_info)
        c.setFillColor(colors.black)

        # ---------------------------------------------------------
        # عنوان التقرير
        y -= 60
        c.setFont(self.font_name, 20)
        c.drawCentredString(width / 2, y, title)
        y -= 30

        # التاريخ
        c.setFont(self.font_name, 12)
        c.drawCentredString(width / 2, y, datetime.now().strftime("%Y-%m-%d  %H:%M"))
        y -= 40

        # ---------------------------------------------------------
        # الجدول
        c.setFont(self.font_name, 11)

        row_height = 22
        x_start = 40
        table_width = width - 80

        # رسم الهيدر
        c.setFillColor(colors.HexColor("#0A3D91"))
        c.rect(x_start, y - row_height, table_width, row_height, fill=1)
        c.setFillColor(colors.white)

        x = x_start + 5
        for h in headers:
            c.drawString(x, y - 17, str(h))
            x += (table_width / len(headers))

        c.setFillColor(colors.black)
        y -= (row_height + 5)

        # رسم الصفوف
        for row in rows:
            if y < 80:
                self._add_footer(c, width)
                c.showPage()
                y = height - 80
                c.setFont(self.font_name, 11)

            x = x_start + 5
            for cell in row:
                c.drawString(x, y - 15, str(cell))
                x += (table_width / len(headers))

            y -= row_height

        # ---------------------------------------------------------
        # الفوتر
        self._add_footer(c, width)

        c.save()

    # =========================================================
    def _add_footer(self, c, width):
        """
        فوتر احترافي لكل صفحة
        """
        c.setFont(self.font_name, 9)
        c.setFillColor(colors.HexColor("#0A3D91"))
        c.drawCentredString(width / 2, 30, "All Rights Reserved © Mahmoud Ali — Inventory Pro System")
        c.setFillColor(colors.black)
