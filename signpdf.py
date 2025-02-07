import os
import shutil
from PyPDF2 import PdfWriter, PdfReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Global configuration for text positioning
TEXT_X_POSITION = 65  # X coordinate for text
TEXT_Y_POSITION = 680  # Y coordinate for text
TEXT_SIZE = 12  # Font size

# Register DejaVu Sans font for Cyrillic support using a relative path (adjust this based on your project directory)
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVu', font_path))

# Create input directory if it doesn't exist
input_dir = "in"
os.makedirs(input_dir, exist_ok=True)

def process_pdf(input_file, output_file, text):
    # Create text overlay
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('DejaVu', TEXT_SIZE)
    can.drawString(TEXT_X_POSITION, TEXT_Y_POSITION, text)
    can.save()
    packet.seek(0)
    
    # Create new PDF with text
    new_pdf = PdfReader(packet)
    
    with open(input_file, "rb") as file:
        existing_pdf = PdfReader(file)
        output = PdfWriter()
        
        # Merge pages
        for page in existing_pdf.pages:
            if page == existing_pdf.pages[0]:  # Add text only to first page
                page.merge_page(new_pdf.pages[0])
            output.add_page(page)
        
        # Save output
        with open(output_file, "wb") as output_stream:
            output.write(output_stream)

# Clear the output directory before starting
output_dir = "out"
if os.path.exists(output_dir):
    # Remove all files in the output directory
    for file_name in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process all PDFs in input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".pdf"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.replace(".pdf", "-sgn.pdf"))
        text = os.path.splitext(filename)[0]
        text = text.split('_', 1)[0]  # Split by the first underscore and keep the first part
        process_pdf(input_path, output_path, text)
