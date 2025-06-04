from reportlab.pdfgen import canvas

output_path = "/home/empty.pdf"
c = canvas.Canvas(output_path)
c.showPage()
c.save()

print(f"[INFO] Empty PDF generated at {output_path}")
