from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_extracted_text(pages:list, chunk_size = 750, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = []
    for page in pages:
        texts = splitter.split_text(page["text"])
        for i, chunk in enumerate(texts):
            chunks.append({
                "page_number": page["page_number"],
                "chunk_index": i,
                "content": chunk
            })

    return chunks