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
    column_count = 0
    max_columns = 3
    x_position = 100  # Starting x position for the first column

    for filename in filenames:
        c.drawString(x_position, y_position, filename)
        y_position -= 20
        if y_position < 50:  # Check for column overflow
            column_count += 1
            if column_count < max_columns:
                # Move to the next column
                y_position = 800
                x_position += 200  # Adjust this value based on your layout
            else:
                # Reset for a new page
                c.showPage()
                c.setFont('DejaVu', 12)
                column_count = 0
                x_position = 100  # Reset x position for the new page
                y_position = 800

    # Save the PDF
    c.save()

    print(f"PDF file created: {output_pdf_path}")


scan_and_generate_pdf()
