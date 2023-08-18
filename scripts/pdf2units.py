import sys
from pdfminer.high_level import extract_text

def extract_text_from_pdf(pdf_path):
    # Extract text using pdfminer
    text = extract_text(pdf_path)
    # print(text[:3000])
    check_arxiv_range = 40

    # Split the text into blocks (assuming empty lines as separators)
    blocks = [block.strip() for block in text.split("\n") if block.strip()]

    blocks = reformat_arxiv_code(blocks[:check_arxiv_range])
    
    # for block in blocks[:20]:
    #     print(block)
    #     print("-" * 40)  # Separator for clarity


def reformat_arxiv_code(first_blocks):
    # Define a reasonable range to check for the arXiv pattern

    
    # Reverse the order of blocks within the check range and merge into a single string
    merged_blocks = ''.join(first_blocks[::-1])
    print(f"merged_blocks: {merged_blocks}")
     
    # Check for the "arXiv:" pattern in the merged blocks (but in reverse order)
    if "arXiv:" not in merged_blocks:
        return None, 0
    
    # Find the start and end indices of the "arXiv" pattern
    start_index = merged_blocks.index("arXiv:")
    end_index = start_index + len("arXiv:")
    
    # Split the merged blocks back into individual blocks
    after_arxiv = merged_blocks[end_index:]
    print(f"after_arxiv: {after_arxiv}")
    print(f"end_index: {end_index}")
    print(f"start_index: {start_index}")

    # Return the reformatted blocks
    return ["arXiv:", after_arxiv], start_index


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pdf2units.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extract_text_from_pdf(pdf_path)
