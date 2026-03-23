import fitz  # PyMuPDF
import os

def convert_pdf_to_images(pdf_path, output_dir):
    print(f"Starting Vision-First conversion for: {pdf_path}")
    
    # Create a new folder specifically for full pages
    page_dir = os.path.join(output_dir, "document_pages")
    os.makedirs(page_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    
    # We use a matrix to scale the resolution up to 300 DPI 
    # This ensures the VLM can read small technical subscripts and dimensions
    zoom_x = 2.0  # horizontal zoom
    zoom_y = 2.0  # vertical zoom
    mat = fitz.Matrix(zoom_x, zoom_y)

    print(f"Converting {len(doc)} pages into high-res images...")

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Take a high-resolution screenshot of the entire page
        pix = page.get_pixmap(matrix=mat)
        
        image_name = f"page_{page_num + 1}.png"
        image_path = os.path.join(page_dir, image_name)
        
        pix.save(image_path)
        
        # Print progress every 10 pages so we know it hasn't frozen
        if (page_num + 1) % 10 == 0:
            print(f" -> Processed {page_num + 1}/{len(doc)} pages...")
            
    print(f"\nSuccess! All pages converted and saved to {page_dir}")

if __name__ == "__main__":
    TARGET_PDF = "data/raw/ISI_CODE.pdf" 
    OUTPUT_DIRECTORY = "data/processed/"
    
    convert_pdf_to_images(TARGET_PDF, OUTPUT_DIRECTORY)
