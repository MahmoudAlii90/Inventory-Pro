import os
from reportlab.lib.pagesizes import A4, A5, A6
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from utils.settings_manager import SettingsManager


class ReturnInvoicePrinter:
    def __init__(self):
        self.settings = SettingsManager()

    # =================================================================
    def generate_pdf(self, header, items, filename, size="A4"):
        page_size = self.get_page_size(size)
        c = canvas.Canvas(filename, pagesize=page_size)

        width, height = page_size
        y = height - 30

        # ======================== COMPANY INFO ==========================
        company = self.settings.get_all()

        if company["logo_path"] and os.path.exists(company["logo_path"]):
            c.drawImage(company["logo_path"], width - 120, height - 100, 80, 80)

        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, company["company_name"])
        y -= 18

        c.setFont("Helvetica", 10)
        c.drawString(30, y, f"Phone: {company['company_phone']}")
        y -= 14

        c.drawString(30, y, f"Email: {company['company_email']}")
        y -= 14

        c.drawString(30, y, f"Address: {company['company_address']}")
        y -= 25

        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, y, "Sales Return Receipt")
        y -= 25

        # ======================== HEADER INFO ==========================
        c.setFont("Helvetica", 11)
        c.drawString(30, y, f"Return ID: {header['return_id']}")
        y -= 16

        c.drawString(30, y, f"Invoice ID: {header['invoice_id']}")
        y -= 16

        c.drawString(30, y, f"Date: {header['date']}")
        y -= 25

        # ======================== TABLE HEADERS ==========================
        c.setFont("Helvetica-Bold", 11)
        c.drawString(30, y, "Item")
        c.drawString(width / 2 - 40, y, "Qty")
        c.drawString(width - 120, y, "Price")
        c.drawString(width - 60, y, "Total")
        y -= 12
        c.line(25, y, width - 25, y)
        y -= 10

        # ======================== ITEMS ==========================
        c.setFont("Helvetica", 10)

        total_all = 0

        for item in items:
            c.drawString(30, y, str(item["name"]))
            c.drawString(width / 2 - 30, y, str(item["qty"]))
            c.drawString(width - 120, y, f"{item['price']:.2f}")
            c.drawString(width - 60, y, f"{item['total']:.2f}")

            total_all += item["total"]
            y -= 15

            if y < 60:
                c.showPage()
                y = height - 40

        # ======================== TOTAL ==========================
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y - 20, f"Total Return Amount: {total_all:.2f}")

        # ======================== FOOTER ==========================
        c.setFont("Helvetica", 9)
        c.drawString(30, 40, "All Rights Reserved © Mahmoud Ali — 01000551634")
        c.drawString(30, 28, "Inventory Pro — Professional Stock Management System")

        c.save()

    # =================================================================
    def get_page_size(self, size):
        sizes = {
            "A4": A4,
            "A5": A5,
            "A6": A6,
            "80mm": (80 * mm, 200 * mm),
            "58mm": (58 * mm, 180 * mm),
        }
        return sizes.get(size, A4)
