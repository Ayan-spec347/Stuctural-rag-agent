import os
import json
import time
import google.generativeai as genai
from PIL import Image

# --- PASTE YOUR API KEY HERE ---
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def process_with_cloud_vlm(image_dir, output_json, start_page, end_page):
    print(f"Connecting to Cloud AI for {image_dir}...")
    
    if not os.path.exists(image_dir):
        print(f"Error: Could not find {image_dir}.")
        return
        
    all_images = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg'))]
    
    target_images = []
    for filename in all_images:
        page_number = int(filename.split('_')[1].split('.')[0])
        if start_page <= page_number <= end_page:
            target_images.append(filename)
            
    target_images.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    
    # --- NEW: SMART RESUME LOGIC ---
    document_data = []
    processed_pages = set() # Keep track of what we already finished
    
    if os.path.exists(output_json):
        print(f"Loading existing progress from {output_json}...")
        try:
            with open(output_json, "r", encoding="utf-8") as f:
                document_data = json.load(f)
                # Mark these pages as done so we don't waste API tokens on them
                for item in document_data:
                    processed_pages.add(item["page_number"])
            print(f"Successfully loaded {len(processed_pages)} previously extracted pages.")
        except json.JSONDecodeError:
            print("Existing JSON is empty or corrupted. Starting fresh.")

    system_prompt = """You are an advanced Document AI and OCR extraction engine. 
    Read the provided engineering document page. 
    1. Output all text visible exactly as written.
    2. Format any tabular data into standard markdown tables.
    3. Describe any structural schematics in extreme technical detail.
    If the page is completely blank, reply with "SKIP_PAGE".
    Output only the raw extracted data without conversational filler."""

    print(f"Scanning {len(target_images)} pages. Starting extraction pipeline...\n")

    for filename in target_images:
        page_number = int(filename.split('_')[1].split('.')[0])
        
        # --- NEW: SKIP IF ALREADY DONE ---
        if page_number in processed_pages:
            print(f"⏭️ Skipping Page {page_number} (Already extracted)")
            continue
            
        image_path = os.path.join(image_dir, filename)
        print(f"Uploading and processing Page {page_number}...")
        start_time = time.time()
        
        # Token Starvation Logic (Shrink image to save API quota)
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((768, 768), Image.Resampling.LANCZOS)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content([system_prompt, img])
                page_content = response.text.strip()
                elapsed_time = round(time.time() - start_time, 2)
                
                document_data.append({
                    "page_number": page_number,
                    "content": page_content
                })
                
                print(f" -> Success! {len(page_content.split())} words extracted in {elapsed_time}s.")
                
                # Checkpoint Save: Now it safely overwrites the file WITH all the old data included!
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(document_data, f, indent=4)
                
                time.sleep(15) # Safe speed limit
                break 
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    wait_time = 60 * (attempt + 1) 
                    print(f" -> 🚦 Rate limit hit! Sleeping for {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f" -> ❌ ERROR on Page {page_number}: {e}")
                    document_data.append({"page_number": page_number, "content": f"Error: {e}"})
                    break 

if __name__ == "__main__":
    PAGE_DIRECTORY = "data/processed/document_pages"
    OUTPUT_JSON = "data/processed/vlm_extracted_data.json"
    
    # You can now leave this as 1 to 5000 forever. The script will figure out where to resume!
    START_PAGE = 58
    END_PAGE = 59
    
    process_with_cloud_vlm(PAGE_DIRECTORY, OUTPUT_JSON, START_PAGE, END_PAGE)