from services.pdf_parser import pdf_extraction
from services.chunking import chunk_extracted_text


def main():
    pdf_path = "Consitution of India.pdf"  
    pages = pdf_extraction(pdf_path)
    chunks = chunk_extracted_text(pages)

    for chunk in chunks[:3]: 
        print(f"\n[Page {chunk['page_number']} - Chunk {chunk['chunk_index']}]:")
        print(chunk['content'][:300], "...")

if __name__ == "__main__":
    main()
