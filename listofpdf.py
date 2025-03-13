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

    # Define margins
    left_margin = 10
    right_margin = 10
    top_margin = 10
    bottom_margin = 20

    # Calculate available width and height
    available_width = A4[0] - left_margin - right_margin
    available_height = A4[1] - top_margin - bottom_margin

    # Add filenames to the PDF
    max_font_size = 12
    min_font_size = 8
    current_font_size = max_font_size
    c.setFont('DejaVu', current_font_size)

    y_position = A4[1] - top_margin  # Start from the top margin
    column_count = 0
    max_columns = 4
    max_lines_per_column = 40  # Maximum lines per column
    line_count = 0  # Initialize line count
    column_width = available_width / max_columns  # Calculate column width based on available width

    for filename in filenames:
        # Calculate the width of the text
        text_width = pdfmetrics.stringWidth(filename, 'DejaVu', current_font_size)

        # Check if the text exceeds the column width
        while text_width > (column_width - 20):  # 20 is a margin
            current_font_size -= 1  # Decrease font size
            if current_font_size < min_font_size:
                break  # Don't go below minimum font size
            c.setFont('DejaVu', current_font_size)
            text_width = pdfmetrics.stringWidth(filename, 'DejaVu', current_font_size)

        # Draw the string only if it fits
        if text_width <= (column_width - 20):  # Ensure it fits within the column width
            c.drawString(left_margin + (column_count * column_width), y_position, filename)
            y_position -= 20
            line_count += 1  # Increment line count

            if line_count >= max_lines_per_column:  # Check for line overflow
                column_count += 1
                if column_count < max_columns:
                    # Move to the next column
                    y_position = A4[1] - top_margin  # Reset y_position to the top margin
                    line_count = 0  # Reset line count for the new column
                    current_font_size = max_font_size  # Reset font size for the new column
                    c.setFont('DejaVu', current_font_size)  # Reset font size
                else:
                    # Reset for a new page
                    c.showPage()
                    c.setFont('DejaVu', 12)
                    column_count = 0
                    y_position = A4[1] - top_margin  # Reset y_position for the new page
                    line_count = 0  # Reset line count for the new page
                    current_font_size = max_font_size  # Reset font size for the new page
                    c.setFont('DejaVu', current_font_size)  # Reset font size
        else:
            print(f"Warning: '{filename}' exceeds the width limit and will not be printed.")

    # Save the PDF
    c.save()

    print(f"PDF file created: {output_pdf_path}")


scan_and_generate_pdf()
