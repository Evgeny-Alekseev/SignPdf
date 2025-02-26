import os
from pathlib import Path
import math
import fitz  # PyMuPDF

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
    
    # Collect pages from all PDFs in the group
    for pdf_file in pdf_files:
        doc = fitz.open(os.path.join('in', pdf_file))
        docs.append(doc)  # Store document reference
        
        # Get first two pages if available
        for i in range(min(2, len(doc))):
            first_pages.append((doc, i))
            
        # Get third and fourth pages if available
        if len(doc) > 2:
            # Add pages in pairs (3rd then 4th) for each document
            temp_pages = []
            if len(doc) > 2:  # Has 3rd page
                temp_pages.append((doc, 2))
            if len(doc) > 3:  # Has 4th page
                temp_pages.append((doc, 3))
            last_pages.extend(temp_pages)
    
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
        # Create the combined PDFs with two pages per sheet
        if first_pages:
            output_path = f'out/first_pages_group_{group_number}.pdf'
            doc_out = fitz.open()
            
            # Calculate dimensions for A4 landscape
            width = 841.89  # A4 height in points (landscape)
            height = 595.28  # A4 width in points (landscape)
            
            # Available space for each page (with margins)
            page_width = width * 0.45  # 45% of page width for each input page
            page_height = height * 0.95  # 95% of page height for each input page
            
            # Process pages two at a time
            for i in range(0, len(first_pages), 2):
                # Create a new landscape page
                page_out = doc_out.new_page(width=width, height=height)
                
                # Add first page of the pair
                doc, page_num = first_pages[i]
                source_page = doc[page_num]
                
                # Calculate scaling factor while maintaining aspect ratio
                scale_w = page_width / source_page.rect.width
                scale_h = page_height / source_page.rect.height
                scale = min(scale_w, scale_h)
                
                # Calculate actual dimensions after scaling
                actual_width = source_page.rect.width * scale
                actual_height = source_page.rect.height * scale
                
                # Center the page in its half
                x1 = (width/4) - (actual_width/2)
                y1 = (height/2) - (actual_height/2)
                
                page_out.show_pdf_page(
                    fitz.Rect(x1, y1, x1 + actual_width, y1 + actual_height),
                    doc,
                    page_num
                )
                
                # Add second page if available
                if i + 1 < len(first_pages):
                    doc, page_num = first_pages[i + 1]
                    source_page = doc[page_num]
                    
                    # Calculate scaling factor while maintaining aspect ratio
                    scale_w = page_width / source_page.rect.width
                    scale_h = page_height / source_page.rect.height
                    scale = min(scale_w, scale_h)
                    
                    # Calculate actual dimensions after scaling
                    actual_width = source_page.rect.width * scale
                    actual_height = source_page.rect.height * scale
                    
                    # Center the page in its half
                    x2 = (3*width/4) - (actual_width/2)
                    y2 = (height/2) - (actual_height/2)
                    
                    page_out.show_pdf_page(
                        fitz.Rect(x2, y2, x2 + actual_width, y2 + actual_height),
                        doc,
                        page_num
                    )
            
            doc_out.save(output_path)
            doc_out.close()
        
        if last_pages:
            output_path = f'out/last_pages_group_{group_number}.pdf'
            doc_out = fitz.open()
            
            # Calculate dimensions for A4 landscape
            width = 841.89  # A4 height in points (landscape)
            height = 595.28  # A4 width in points (landscape)
            
            # Available space for each page (with margins)
            page_width = width * 0.45  # 45% of page width for each input page
            page_height = height * 0.95  # 95% of page height for each input page
            
            # Process pages two at a time
            for i in range(0, len(last_pages), 2):
                # Create a new landscape page
                page_out = doc_out.new_page(width=width, height=height)
                
                # Add first page of the pair
                doc, page_num = last_pages[i]
                source_page = doc[page_num]
                
                # Calculate scaling factor while maintaining aspect ratio
                scale_w = page_width / source_page.rect.width
                scale_h = page_height / source_page.rect.height
                scale = min(scale_w, scale_h)
                
                # Calculate actual dimensions after scaling
                actual_width = source_page.rect.width * scale
                actual_height = source_page.rect.height * scale
                
                # Center the page in its half
                x1 = (width/4) - (actual_width/2)
                y1 = (height/2) - (actual_height/2)
                
                page_out.show_pdf_page(
                    fitz.Rect(x1, y1, x1 + actual_width, y1 + actual_height),
                    doc,
                    page_num
                )
                
                # Add second page if available
                if i + 1 < len(last_pages):
                    doc, page_num = last_pages[i + 1]
                    source_page = doc[page_num]
                    
                    # Calculate scaling factor while maintaining aspect ratio
                    scale_w = page_width / source_page.rect.width
                    scale_h = page_height / source_page.rect.height
                    scale = min(scale_w, scale_h)
                    
                    # Calculate actual dimensions after scaling
                    actual_width = source_page.rect.width * scale
                    actual_height = source_page.rect.height * scale
                    
                    # Center the page in its half
                    x2 = (3*width/4) - (actual_width/2)
                    y2 = (height/2) - (actual_height/2)
                    
                    page_out.show_pdf_page(
                        fitz.Rect(x2, y2, x2 + actual_width, y2 + actual_height),
                        doc,
                        page_num
                    )
            
            doc_out.save(output_path)
            doc_out.close()
            
    finally:
        # Clean up: close all documents
        for doc in docs:
            doc.close()

def main():
    # Create input directory if it doesn't exist
    Path('in').mkdir(exist_ok=True)
    
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