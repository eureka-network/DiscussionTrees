import sys, re, os
from pdfminer.high_level import extract_text


def extract_text_from_pdf(pdf_path):
    # Extract text using pdfminer
    text = extract_text(pdf_path)
    # print(text[:3000])
    check_arxiv_range = 150
    initial_text = text[:check_arxiv_range]

    arxiv_block, end_of_marker = reformat_arxiv(initial_text)
    if arxiv_block is not None:
        text = arxiv_block + text[end_of_marker:]
    
    save_to_txt(text, pdf_path)


def save_to_txt(text, pdf_path):
    # Derive the output filename from the pdf_path
    base_name = os.path.splitext(pdf_path)[0]
    txt_filename = base_name + ".txt"

    with open(txt_filename, 'w', encoding='utf-8') as file:
        file.write(text)


def reformat_arxiv(text):
    # Define the marker sequence
    marker = ":\nv\ni\nX\nr\na"
    
    # Check if the marker sequence is in the text
    if marker not in text:
        return None
    
    # Extract the portion of the text from the start up to the marker sequence
    arxiv_portion = text[:text.index(marker) + len(marker)]
    
    # Reverse the characters
    reversed_arxiv = arxiv_portion[::-1]
    
    # Remove single newlines and convert double newlines to a whitespace
    reformatted_arxiv = reversed_arxiv.replace("\n\n", " ").replace("\n", "")

    # Remove spaces between square brackets
    reformatted_arxiv = re.sub(r'(\[)\s*([^]]*?)\s*(\])',
        lambda m: m.group(1) + m.group(2).replace(' ', '') + m.group(3), reformatted_arxiv)

    # Return the reformatted arXiv portion followed by the rest of the text, 
    # and the index of the end of the marker
    return reformatted_arxiv, text.index(marker) + len(marker)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pdf2units.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extract_text_from_pdf(pdf_path)
