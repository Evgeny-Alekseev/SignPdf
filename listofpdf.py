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

    # Define margins for the PDF layout
    left_margin, right_margin, top_margin, bottom_margin = 30, 10, 40, 20
    available_width = A4[0] - left_margin - right_margin  # Calculate available width
    available_height = A4[1] - top_margin - bottom_margin  # Calculate available height
    max_font_size, min_font_size = 20, 8  # Set font size limits
    max_columns = 4  # Maximum number of columns to display

    column_count = 1  
    optimal_font_size = max_font_size  

    # Determine the optimal font size and number of columns
    while column_count <= max_columns:
        column_width = available_width / column_count  # Calculate width for each column
        font_size = max_font_size  # Start with the maximum font size

        # Check each filename to see if it fits within the column width
        for filename in filenames:
            text_width = pdfmetrics.stringWidth(filename, 'DejaVu', font_size)
            # Decrease font size until the text fits or reaches the minimum size
            while text_width > (column_width - 20) and font_size > min_font_size:
                font_size -= 1
                text_width = pdfmetrics.stringWidth(filename, 'DejaVu', font_size)
        
        # Calculate how many lines can fit in the available height
        line_height = font_size + 4  # Add some padding
        max_lines = (available_height // line_height)  # Maximum lines per column
        required_columns = -(-len(filenames) // max_lines)  # Ceiling division for required columns
        
        # If the required columns fit within the current column count, set the optimal font size
        if required_columns <= column_count:
            optimal_font_size = font_size
            break
        
        column_count += 1

    c.setFont('DejaVu', optimal_font_size)
    y_position = A4[1] - top_margin  # Start drawing from the top margin
    line_count, col = 0, 0  # Initialize line count and column index
    line_height = optimal_font_size + 4  # Calculate line height for spacing

    for filename in filenames:
        # Check if the next line will exceed the bottom margin
        if y_position - line_height < bottom_margin:
            col += 1
            line_count = 0
            y_position = A4[1] - top_margin

            # If the column exceeds the maximum, start a new page
            if col >= column_count:
                c.showPage()  # Create a new page
                c.setFont('DejaVu', optimal_font_size)  # Reset font size for the new page
                col = 0  # Reset column index
                y_position = A4[1] - top_margin  # Reset y_position for the new page

        # Calculate the x position based on the current column
        x_position = left_margin + col * (available_width / column_count)
        c.drawString(x_position, y_position, filename)
        y_position -= line_height
        line_count += 1

    c.save()
    print(f"PDF file created: {output_pdf_path}")

scan_and_generate_pdf()
