import os
import shutil
from PyPDF2 import PdfWriter, PdfReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Default configuration for text positioning
DEFAULT_TEXT_X_POSITION = 65  # X coordinate for text
DEFAULT_TEXT_Y_POSITION = 680  # Y coordinate for text
DEFAULT_TEXT_SIZE = 12  # Font size

# Function to load coordinates from coordinates.txt file
def load_coordinates():
    coordinates = {
        "TEXT_X_POSITION": DEFAULT_TEXT_X_POSITION,
        "TEXT_Y_POSITION": DEFAULT_TEXT_Y_POSITION
    }

    coordinates_file = "coordinates.txt"
    if os.path.exists(coordinates_file):
        try:
            with open(coordinates_file, 'r') as file:
                # Read the content of coordinates.txt
                for line in file:
                    if "TEXT_X_POSITION" in line:
                        coordinates["TEXT_X_POSITION"] = int(line.split('=')[1].strip().split('#')[0].strip())
                    elif "TEXT_Y_POSITION" in line:
                        coordinates["TEXT_Y_POSITION"] = int(line.split('=')[1].strip().split('#')[0].strip())
        except Exception as e:
            print(f"Error reading {coordinates_file}: {e}. Using default coordinates.")

    return coordinates["TEXT_X_POSITION"], coordinates["TEXT_Y_POSITION"]

# Register DejaVu Sans font for Cyrillic support using a relative path (adjust this based on your project directory)
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVu', font_path))

# Create input directory if it doesn't exist
input_dir = "in"
os.makedirs(input_dir, exist_ok=True)

def process_pdf(input_file, output_file, text, x_pos, y_pos):
    # Create text overlay
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('DejaVu', DEFAULT_TEXT_SIZE)
    can.drawString(x_pos, y_pos, text)
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

# Load coordinates from coordinates.txt or use default
TEXT_X_POSITION, TEXT_Y_POSITION = load_coordinates()

# Process all PDFs in input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".pdf"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.replace(".pdf", "-sgn.pdf"))
        text = os.path.splitext(filename)[0]
        text = text.split('_', 1)[0]  # Split by the first underscore and keep the first part
        process_pdf(input_path, output_path, text, TEXT_X_POSITION, TEXT_Y_POSITION)
