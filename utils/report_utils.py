import os
import json
import xlsxwriter
from datetime import datetime

from PyQt5 import QtGui, QtWidgets, QtCore, QtPrintSupport

from utils.settings_manager import SettingsManager


class ReportUtils:
    def __init__(self):
        self.settings = SettingsManager()

    # ========================================================================
    # -------------    PDF EXPORT (TABLES) GOLD VERSION      -----------------
    # ========================================================================
    def export_table_pdf(self, table, filename="report", report_title="Report"):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None, "حفظ PDF", f"{filename}.pdf", "PDF Files (*.pdf)"
        )

        if not save_path:
            return

        # إعدادات الشركة
        company_name = self.settings.get("company_name", "Company Name")
        logo_path = self.settings.get("logo_path", None)

        doc = SimpleDocTemplate(
            save_path, pagesize=A4,
            leftMargin=30, rightMargin=30, topMargin=40, bottomMargin=40
        )

        story = []
        styles = getSampleStyleSheet()

        # -------------------- اللوجو + اسم الشركة --------------------
        if logo_path and os.path.exists(logo_path):
            story.append(Paragraph(
                f"""
                <para alignment='right'>
                    <img src='{logo_path}' width='90' height='90' valign='middle'/>
                </para>
                """,
                styles["Normal"]
            ))

        story.append(Paragraph(
            f"<para alignment='right'><b>{company_name}</b></para>",
            styles["Title"]
        ))

        story.append(Paragraph(
            f"<para alignment='right'><font size=10 color='grey'>Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}</font></para>",
            styles["Normal"]
        ))

        story.append(Paragraph("<br/><br/>", styles["Normal"]))

        # -------------------- عنوان التقرير --------------------
        story.append(Paragraph(
            f"<para alignment='center'><b>{report_title}</b></para>",
            styles["Heading2"]
        ))
        story.append(Paragraph("<br/>", styles["Normal"]))

        # -------------------- جمع البيانات من الجدول --------------------
        headers = []
        data = []

        for c in range(table.columnCount()):
            headers.append(table.horizontalHeaderItem(c).text())

        data.append(headers)

        for r in range(table.rowCount()):
            row = []
            for c in range(table.columnCount()):
                item = table.item(r, c)
                row.append(item.text() if item else "")
            data.append(row)

        # -------------------- إضافة الجدول --------------------
        tbl = Table(data, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A3D91")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("LINEBEFORE", (0, 0), (-1, -1), 0.25, colors.grey),
            ("LINEAFTER", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F4F8")]),
        ]))

        story.append(tbl)
        story.append(Paragraph("<br/><br/>", styles["Normal"]))

        # -------------------- علامة حقوق الملكية --------------------
        story.append(Paragraph(
            "<para alignment='center'><font size=8 color='grey'>"
            "All Rights Reserved © Mahmoud Ali | 01000551634"
            "</font></para>",
            styles["Normal"]
        ))

        doc.build(story)

    # ========================================================================
    # -----------------  EXCEL EXPORT GOLD VERSION  --------------------------
    # ========================================================================
    def export_table_excel(self, table, filename="report", report_title="Report"):

        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None, "حفظ Excel", f"{filename}.xlsx", "Excel Files (*.xlsx)"
        )

        if not save_path:
            return

        workbook = xlsxwriter.Workbook(save_path)
        worksheet = workbook.add_worksheet("Report")

        header_format = workbook.add_format({
            "bold": True,
            "bg_color": "#0A3D91",
            "color": "white",
            "border": 1,
            "align": "center"
        })

        cell_format = workbook.add_format({
            "border": 1,
            "align": "center"
        })

        # -------------------- رأس الصفحة --------------------
        company_name = self.settings.get("company_name", "Company Name")
        worksheet.merge_range("A1:E1", company_name, workbook.add_format({
            "bold": True,
            "font_size": 16,
            "align": "center"
        }))

        worksheet.merge_range("A2:E2", f"Report: {report_title}", workbook.add_format({
            "bold": True,
            "font_size": 12,
            "align": "center"
        }))

        worksheet.merge_range("A3:E3", datetime.now().strftime("%Y-%m-%d %H:%M"), workbook.add_format({
            "color": "gray",
            "align": "center"
        }))

        start_row = 5

        # -------------------- العناوين --------------------
        for col in range(table.columnCount()):
            header = table.horizontalHeaderItem(col).text()
            worksheet.write(start_row, col, header, header_format)

        # -------------------- البيانات --------------------
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                val = item.text() if item else ""
                worksheet.write(row + start_row + 1, col, val, cell_format)

        workbook.close()

        QtWidgets.QMessageBox.information(None, "✔", f"تم حفظ الملف:\n{save_path}")

    # ========================================================================
    # -------------------------  PRINTING  -----------------------------------
    # ========================================================================
    def print_report(self, table):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        dialog = QtPrintSupport.QPrintPreviewDialog(printer)

        dialog.paintRequested.connect(lambda p: self.render_table_for_print(p, table))
        dialog.exec_()

    def render_table_for_print(self, printer, table):
        painter = QtGui.QPainter(printer)
        painter.setFont(QtGui.QFont("Cairo", 10))

        x = 50
        y = 80
        
        # عنوان الشركة
        company_name = self.settings.get("company_name", "Company Name")
        painter.drawText(x, y, company_name)
        y += 40

        # التاريخ
        painter.setPen(QtGui.QColor("gray"))
        painter.drawText(x, y, datetime.now().strftime("%Y-%m-%d %H:%M"))
        painter.setPen(QtGui.QColor("black"))
        y += 60

        # رأس الجدول
        for col in range(table.columnCount()):
            painter.drawText(x + col * 120, y, table.horizontalHeaderItem(col).text())
        y += 30

        # البيانات
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                painter.drawText(x + col * 120, y, item.text() if item else "")
            y += 25

        painter.end()

    # ========================================================================
    # ----------------- DASHBOARD EXPORT - PDF --------------------------------
    # ========================================================================
    def export_dashboard_pdf(self, dashboard_data, filename="dashboard", report_title="Dashboard"):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None, "حفظ Dashboard PDF", f"{filename}.pdf", "PDF Files (*.pdf)"
        )
        if not save_path:
            return

        c = canvas.Canvas(save_path, pagesize=A4)

        company_name = self.settings.get("company_name", "Company Name")
        logo_path = self.settings.get("logo_path", None)

        if logo_path and os.path.exists(logo_path):
            c.drawImage(logo_path, 450, 740, width=90, height=90)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, 800, company_name)

        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(40, 780, f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, 740, report_title)

        y = 700
        c.setFont("Helvetica", 12)

        for d in dashboard_data:
            c.drawString(40, y, f"{d['title']}: {d['value']}")
            y -= 25

        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(200, 40, "All Rights Reserved © Mahmoud Ali | 01000551634")

        c.save()
