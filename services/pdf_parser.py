import fitz

def pdf_extraction(file_path: str) -> list:
    doc = fitz.Document(file_path)
    print(f"Total number of pages: {doc.page_count}")
    page_texts = []
    for i, page in enumerate(doc):
        text = page.get_text()
        page_texts.append({
            "page_number": i + 1,
            "text": text
        })
    doc.close()
    return page_texts

