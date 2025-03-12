import os
import shutil
from PyPDF2 import PdfWriter, PdfReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pdfplumber  # Import pdfplumber for better text extraction

# Default configuration for text positioning
DEFAULT_TEXT_X_POSITION = 65  # X coordinate for text
DEFAULT_TEXT_Y_POSITION = 680  # Y coordinate for text
DEFAULT_TEXT_SIZE = 12  # Font size
LINE_HEIGHT = 15  # Standard line height for text positioning

# Global variable to enable special Y position detection
CALCULATE_POSITION = True  # Set to True to enable the new strategy

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

def find_quiz_review_y_position(input_file):
    """Find the Y position below all occurrences of 'quiz/review'."""
    with pdfplumber.open(input_file) as pdf:  # Open the PDF file directly
        first_page = pdf.pages[0]
        
        # Extract words with their bounding boxes
        words = first_page.extract_words()
        
        # Sort words by their top position (Y coordinate) in ascending order
        words.sort(key=lambda w: w['top'])
        
        # List to store positions of all occurrences
        positions = []
        
        # Get the actual height of the page
        page_height = first_page.height
        
        # Scan through the sorted words to find "quiz/review"
        for word in words:
            if 'quiz/review' in word['text'].lower():  # Case-insensitive search
                # Get the Y position of the found word
                y_position = page_height - (word['top'] + 10)  # Adjust for padding
                x_position = word['doctop']  # Get the X position from the word's bounding box
                
                # Removed the print statement for found positions
                # print(f"Found 'quiz/review' at X: {x_position}, Y: {y_position}")
                
                # Store the position if needed
                positions.append((x_position, y_position))
        
        return positions  # Return the list of positions if found
        
    return None  # Return None if 'quiz/review' is not found

# Register DejaVu Sans font for Cyrillic support using a relative path (adjust this based on your project directory)
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVu', font_path))

# Create input directory if it doesn't exist
input_dir = "in"
os.makedirs(input_dir, exist_ok=True)

def process_pdf(input_file, output_file, text, x_pos, y_pos):
    # Only create text overlay if y_pos is not None
    if y_pos is not None:
        # Adjust the Y position to place the text one line lower only if dynamic mode is enabled
        if CALCULATE_POSITION:
            y_pos -= LINE_HEIGHT  # Move the text one line lower
        
        # Round the Y position to the nearest integer
        y_pos = round(y_pos)
        
        # Print the Y position and text being added
        print(f"Creating text overlay at X: {x_pos}, Y: {y_pos}, Text: '{text}'")
        
        # Create text overlay
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont('DejaVu', DEFAULT_TEXT_SIZE)
        
        # Set text color (black)
        can.setFillColorRGB(0, 0, 0)  # RGB for black
        
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
    else:
        # If no valid y_pos, just copy the original PDF to output
        shutil.copy(input_file, output_file)

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
        
        # If the special global variable is set, find the Y position
        if CALCULATE_POSITION:
            positions = find_quiz_review_y_position(input_path)  # Pass the input path directly
            if positions:  # Only update if any positions were found
                # Set TEXT_Y_POSITION to the Y position of the first occurrence
                TEXT_Y_POSITION = positions[0][1]
            else:
                # If no positions were found, save the original file in the output directory
                print(f"No occurrences of 'quiz/review' found in {filename}. Saving original file.")
                shutil.copy(input_path, output_path)  # Copy the original PDF to output
                continue  # Skip to the next file
        
        # Only call process_pdf if we have a valid Y position
        process_pdf(input_path, output_path, text, TEXT_X_POSITION, TEXT_Y_POSITION)
