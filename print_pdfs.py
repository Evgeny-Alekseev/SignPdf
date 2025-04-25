import os
from pathlib import Path
import math
import fitz  # PyMuPDF
import shutil  # Added for file operations

def arrange_pages_two_up(input_pages, output_path):
    """Arrange pages two per page in album layout"""
    # Create a new PDF with landscape orientation
    doc_out = fitz.open()
    
    # Calculate dimensions for A4 landscape
    width = 841.89  # A4 height in points (landscape)
    height = 595.28  # A4 width in points (landscape)
    
    # Process pages two at a time
    for i in range(0, len(input_pages), 2):
        # Create a new landscape page
        page_out = doc_out.new_page(width=width, height=height)
        
        # Calculate scaled dimensions for each input page
        # Use slightly less than half width to create margin
        scale_width = (width * 0.48)
        scale_height = height * 0.95
        
        # Add first page of the pair
        page = input_pages[i]
        rect = page.rect
        scale_factor = min(scale_width/rect.width, scale_height/rect.height)
        scaled_width = rect.width * scale_factor
        scaled_height = rect.height * scale_factor
        
        # Calculate position for first page (left side)
        x1 = (width/4) - (scaled_width/2)
        y1 = (height/2) - (scaled_height/2)
        page_out.show_pdf_page(
            fitz.Rect(x1, y1, x1 + scaled_width, y1 + scaled_height),
            doc_out,
            page.number
        )
        
        # Add second page if available
        if i + 1 < len(input_pages):
            page = input_pages[i + 1]
            rect = page.rect
            scale_factor = min(scale_width/rect.width, scale_height/rect.height)
            scaled_width = rect.width * scale_factor
            scaled_height = rect.height * scale_factor
            
            # Calculate position for second page (right side)
            x2 = (3*width/4) - (scaled_width/2)
            y2 = (height/2) - (scaled_height/2)
            page_out.show_pdf_page(
                fitz.Rect(x2, y2, x2 + scaled_width, y2 + scaled_height),
                doc_out,
                page.number
            )
    
    # Save the output document
    doc_out.save(output_path)
    doc_out.close()

def process_pdf_group(pdf_files, group_number):
    """Process a group of PDFs and create first_pages and last_pages documents"""
    first_pages = []
    last_pages = []
    docs = []  # Keep document references
    
    # Create a blank PDF document for blank pages
    blank_doc = fitz.open()
    blank_page = blank_doc.new_page(width=595.28, height=841.89)  # A4 portrait
    docs.append(blank_doc)  # Add to docs for proper cleanup
    
    # Collect pages from all PDFs in the group
    for pdf_file in pdf_files:
        doc = fitz.open(os.path.join('in', pdf_file))
        docs.append(doc)  # Store document reference
        
        # Get first two pages, add blank if missing
        for i in range(2):  # Always process 2 pages
            if i < len(doc):
                first_pages.append((doc, i, False))  # False = not blank
            else:
                first_pages.append((blank_doc, 0, True))  # True = blank
        
        # Get third and fourth pages, add blank if missing
        for i in range(2, 4):  # Always process pages 3 and 4
            if i < len(doc):
                last_pages.append((doc, i, False))
            else:
                last_pages.append((blank_doc, 0, True))
    
    # Reverse the order of document pairs in last_pages, but keep page order within each document
    last_pages_reversed = []
    for i in range(len(last_pages)-1, -1, -2):
        if i > 0:  # If we have two pages
            last_pages_reversed.extend([last_pages[i-1], last_pages[i]])
        else:  # If we have one page left
            last_pages_reversed.append(last_pages[i])
    last_pages = last_pages_reversed

    # Create output directory if it doesn't exist
    Path('out').mkdir(exist_ok=True)
    
    try:
        # Function to process a set of pages
        def create_output_pdf(pages, output_path):
            doc_out = fitz.open()
            width = 841.89  # A4 height in points (landscape)
            height = 595.28  # A4 width in points (landscape)
            page_width = width * 0.45
            page_height = height * 0.95
            
            for i in range(0, len(pages), 2):
                page_out = doc_out.new_page(width=width, height=height)
                
                # Process first page
                doc, page_num, is_blank = pages[i]
                if not is_blank:
                    source_page = doc[page_num]
                    scale_w = page_width / source_page.rect.width
                    scale_h = page_height / source_page.rect.height
                    scale = min(scale_w, scale_h)
                    actual_width = source_page.rect.width * scale
                    actual_height = source_page.rect.height * scale
                    x1 = (width/4) - (actual_width/2)
                    y1 = (height/2) - (actual_height/2)
                    page_out.show_pdf_page(
                        fitz.Rect(x1, y1, x1 + actual_width, y1 + actual_height),
                        doc,
                        page_num
                    )
                
                # Process second page if available
                if i + 1 < len(pages):
                    doc, page_num, is_blank = pages[i + 1]
                    if not is_blank:
                        source_page = doc[page_num]
                        scale_w = page_width / source_page.rect.width
                        scale_h = page_height / source_page.rect.height
                        scale = min(scale_w, scale_h)
                        actual_width = source_page.rect.width * scale
                        actual_height = source_page.rect.height * scale
                        x2 = (3*width/4) - (actual_width/2)
                        y2 = (height/2) - (actual_height/2)
                        page_out.show_pdf_page(
                            fitz.Rect(x2, y2, x2 + actual_width, y2 + actual_height),
                            doc,
                            page_num
                        )
            
            doc_out.save(output_path)
            doc_out.close()
        
        # Create output PDFs
        if first_pages:
            create_output_pdf(first_pages, f'out/first_pages_group_{group_number}.pdf')
        if last_pages:
            create_output_pdf(last_pages, f'out/last_pages_group_{group_number}.pdf')
            
    finally:
        # Clean up: close all documents
        for doc in docs:
            doc.close()

def main():
    # Create directories if they don't exist
    Path('in').mkdir(exist_ok=True)
    Path('out').mkdir(exist_ok=True)
    
    # First, remove all files in the 'in' directory
    for file in os.listdir('in'):
        file_path = os.path.join('in', file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Removed {file_path}")
    
    # Copy all PDFs from 'out' to 'in'
    out_pdfs = [f for f in os.listdir('out') if f.lower().endswith('.pdf')]
    for pdf in out_pdfs:
        source_path = os.path.join('out', pdf)
        target_path = os.path.join('in', pdf)
        shutil.move(source_path, target_path)
        print(f"Moved {source_path} to {target_path}")
    
    # Get all PDF files from the input directory
    pdf_files = [f for f in os.listdir('in') if f.lower().endswith('.pdf')]
    
    # Process PDFs in groups of 5
    group_size = 5
    num_groups = math.ceil(len(pdf_files) / group_size)
    
    for group_num in range(num_groups):
        start_idx = group_num * group_size
        end_idx = min((group_num + 1) * group_size, len(pdf_files))
        current_group = pdf_files[start_idx:end_idx]
        
        print(f"Processing group {group_num + 1} with {len(current_group)} PDFs")
        process_pdf_group(current_group, group_num + 1)

if __name__ == "__main__":
    main() 