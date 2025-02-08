import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

def scan_and_generate_pdf():
    # Directories
    input_dir = os.path.join(os.getcwd(), 'in')
    output_dir = os.path.join(os.getcwd(), 'out')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Register DejaVu Sans font for Cyrillic support using a relative path (adjust this based on your project directory)
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")
    pdfmetrics.registerFont(TTFont('DejaVu', font_path))

    # Get list of PDF filenames without extensions
    filenames = [os.path.splitext(f)[0] for f in os.listdir(input_dir) if f.endswith('.pdf')]

    # Clear the output directory before starting
    if os.path.exists(output_dir):
        for file_name in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # Create a PDF file
    output_pdf_path = os.path.join(output_dir, 'file_list.pdf')
    c = canvas.Canvas(output_pdf_path, pagesize=A4)

    # Add filenames to the PDF
    c.setFont('DejaVu', 12)

    y_position = 800
    for filename in filenames:
        c.drawString(100, y_position, filename)
        y_position -= 20
        if y_position < 50:  # Check for page overflow
            c.showPage()
            c.setFont('DejaVu', 12)
            y_position = 800

    # Save the PDF
    c.save()

    print(f"PDF file created: {output_pdf_path}")


scan_and_generate_pdf()
