import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

def scan_and_generate_pdf():
    input_dir = os.path.join(os.getcwd(), 'in')
    output_dir = os.path.join(os.getcwd(), 'out')
    os.makedirs(output_dir, exist_ok=True)

    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")
    pdfmetrics.registerFont(TTFont('DejaVu', font_path))

    filenames = [os.path.splitext(f)[0] for f in os.listdir(input_dir) if f.endswith('.pdf')]
    if not filenames:
        print("No PDF files found in the input directory.")
        return

    output_pdf_path = os.path.join(output_dir, 'file_list.pdf')
    c = canvas.Canvas(output_pdf_path, pagesize=A4)

    left_margin, right_margin, top_margin, bottom_margin = 30, 10, 40, 20
    available_width = A4[0] - left_margin - right_margin
    available_height = A4[1] - top_margin - bottom_margin
    max_font_size, min_font_size = 20, 8
    max_columns = 4
    
    column_count = 1
    optimal_font_size = max_font_size

    while column_count <= max_columns:
        column_width = available_width / column_count
        font_size = max_font_size

        for filename in filenames:
            text_width = pdfmetrics.stringWidth(filename, 'DejaVu', font_size)
            while text_width > (column_width - 20) and font_size > min_font_size:
                font_size -= 1
                text_width = pdfmetrics.stringWidth(filename, 'DejaVu', font_size)
        
        line_height = font_size + 4
        max_lines = (available_height // line_height)
        required_columns = -(-len(filenames) // max_lines)
        
        if required_columns <= column_count:
            optimal_font_size = font_size
            break
        
        column_count += 1

    c.setFont('DejaVu', optimal_font_size)
    y_position = A4[1] - top_margin
    line_count, col = 0, 0
    line_height = optimal_font_size + 4

    for filename in filenames:
        if y_position - line_height < bottom_margin:
            col += 1
            line_count = 0
            y_position = A4[1] - top_margin

            if col >= column_count:
                c.showPage()
                c.setFont('DejaVu', optimal_font_size)
                col = 0
                y_position = A4[1] - top_margin

        x_position = left_margin + col * (available_width / column_count)
        c.drawString(x_position, y_position, filename)
        y_position -= line_height
        line_count += 1

    c.save()
    print(f"PDF file created: {output_pdf_path}")

scan_and_generate_pdf()
