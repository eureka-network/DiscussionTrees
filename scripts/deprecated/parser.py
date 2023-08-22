import sys, os
from unstructured.partition.auto import partition

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        elements = partition(file=f, include_page_breaks=True, strategy="hi_res", content_type="application/pdf")
    # print("\n\n".join([str(el) for el in elements][:10]))
    save_to_txt(elements, pdf_path)

def save_to_txt(elements, pdf_path):
    # Derive the output filename from the pdf_path
    base_name = os.path.splitext(pdf_path)[0]
    txt_filename = base_name + "-unstr-hires.txt"
    print(f"Saving to {txt_filename}")

    text = "\n\n".join([str(el) for el in elements])

    with open(txt_filename, 'w', encoding='utf-8') as file:
        file.write(text)
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: unstructured.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extract_text_from_pdf(pdf_path)
