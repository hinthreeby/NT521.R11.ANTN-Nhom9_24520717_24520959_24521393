from reportlab.pdfgen import canvas

output = "corpus_pdf/seed.pdf"

mssv = [
    "24520717",
    "24520959",
    "24521393",
]

c = canvas.Canvas(
    output,
    pagesize=(595, 842),
    pageCompression=0
)

c.setFont("Helvetica", 16)
c.drawString(70, 770, "LAB 3 - FUZZING")

c.setFont("Helvetica", 13)
c.drawString(70, 720, "Danh sach MSSV:")

y = 680
for student in mssv:
    c.drawString(90, y, student)
    y -= 30

c.save()

print(f"Created: {output}")
