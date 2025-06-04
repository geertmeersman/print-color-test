from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import CMYKColor

filepath = "/home/color_test_page_dated.pdf"
c = canvas.Canvas(filepath, pagesize=A4)
width, height = A4

margin_x = 50
margin_y = 50
usable_height = height - 2 * margin_y
usable_width = width - 2 * margin_x
block_height = usable_height / 4

colors = [
    ("Cyan", CMYKColor(1, 0, 0, 0)),
    ("Magenta", CMYKColor(0, 1, 0, 0)),
    ("Yellow", CMYKColor(0, 0, 1, 0)),
    ("Black", CMYKColor(0, 0, 0, 1)),
]

for i, (name, color) in enumerate(colors):
    y_position = margin_y + i * block_height
    c.setFillColor(color)
    c.rect(margin_x, y_position, usable_width, block_height * 0.8, fill=1)
    c.setFillColorRGB(1, 1, 1 if name != "Yellow" else 0)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x + 10, y_position + block_height * 0.4, name)

c.setFillColorRGB(0, 0, 0)
c.setFont("Helvetica", 12)
current_date = datetime.now().strftime("%Y-%m-%d")
c.drawCentredString(width / 2, margin_y / 2, f"Printed on {current_date}")
c.save()
