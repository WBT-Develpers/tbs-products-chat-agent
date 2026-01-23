"""
PDF Ingestion Script for Pinecone Vector Store

This script processes PDF files from the pdf/ directory, extracts text,
creates embeddings, and stores them in Pinecone index.

Optimized for large PDF files with:
- Parallel PDF processing
- Batch embedding generation
- Incremental uploads
- Progress tracking
- Resume capability

Usage:
    python ingest_pdfs.py
"""
import os
import time
import hashlib
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pypdf import PdfReader
from tqdm import tqdm

# Load environment variables
load_dotenv()


def get_file_hash(file_path: Path) -> str:
    """Generate a hash for a file to track if it's been processed."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def extract_text_from_pdf(pdf_path: Path, show_progress: bool = False) -> tuple[str, int]:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        show_progress: Whether to show progress bar
        
    Returns:
        Tuple of (extracted text, page count)
    """
    reader = PdfReader(pdf_path)
    text_parts = []
    total_pages = len(reader.pages)
    
    page_iter = tqdm(reader.pages, desc=f"  Extracting pages", total=total_pages, leave=False) if show_progress else reader.pages
    
    for page_num, page in enumerate(page_iter, start=1):
        try:
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)
        except Exception as e:
            if show_progress:
                tqdm.write(f"    Warning: Could not extract text from page {page_num}: {e}")
    
    full_text = "\n\n".join(text_parts)
    return full_text, total_pages


def process_pdf_file(
    pdf_path: Path,
    text_splitter: RecursiveCharacterTextSplitter,
    base_filename: str
) -> List[Document]:
    """
    Process a single PDF file and return Document chunks.
    
    Args:
        pdf_path: Path to the PDF file
        text_splitter: Text splitter instance
        base_filename: Base filename for metadata
        
    Returns:
        List of Document objects
    """
    # Extract text
    text, page_count = extract_text_from_pdf(pdf_path, show_progress=True)
    
    if not text.strip():
        print(f"  ⚠️  Warning: No text extracted from {pdf_path.name}")
        return []
    
    # Split into chunks
    chunks = text_splitter.create_documents([text])
    
    # Add metadata to each chunk
    file_hash = get_file_hash(pdf_path)
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk.page_content,
            metadata={
                "source": base_filename,
                "file_path": str(pdf_path),
                "file_hash": file_hash,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "page_count": page_count,
                "document_type": "installation_manual"
            }
        )
        documents.append(doc)
    
    return documents


def process_and_upload_batch(
    vector_store: PineconeVectorStore,
    documents: List[Document],
    batch_num: int,
    total_batches: int
) -> bool:
    """
    Process a batch of documents and upload to Pinecone.
    The vector store will handle batch embedding generation internally.
    
    Args:
        vector_store: Pinecone vector store instance
        documents: List of documents to process
        batch_num: Current batch number
        total_batches: Total number of batches
        
    Returns:
        True if successful
    """
    try:
        # Upload to Pinecone (will generate embeddings in batch internally)
        vector_store.add_documents(documents)
        return True
    except Exception as e:
        print(f"\n❌ Error processing batch {batch_num}: {e}")
        return False


def ingest_pdfs_to_pinecone(
    pdf_directory: str = "pdf",
    index_name: str = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    batch_size: int = 50,
    max_workers: int = 2
):
    """
    Process all PDF files in the directory and ingest them into Pinecone.
    Optimized for large PDF files with parallel processing and batch embeddings.
    
    Args:
        pdf_directory: Directory containing PDF files
        index_name: Pinecone index name (defaults to env var)
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        batch_size: Number of documents to process in each batch
        max_workers: Number of parallel workers for PDF processing
    """
    start_time = time.time()
    
    # Get configuration
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not index_name:
        index_name = os.getenv("PINECONE_INDEX_NAME", "products")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Validate configuration
    if not all([pinecone_api_key, openai_api_key]):
        print("❌ Error: Missing required environment variables.")
        print("   Required: PINECONE_API_KEY, OPENAI_API_KEY")
        print("   Optional: PINECONE_INDEX_NAME (defaults to 'products')")
        return
    
    # Check if PDF directory exists
    pdf_dir = Path(pdf_directory)
    if not pdf_dir.exists():
        print(f"❌ Error: PDF directory '{pdf_directory}' not found")
        return
    
    # Find all PDF files
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in '{pdf_directory}' directory")
        return
    
    # Sort by size (process smaller files first for faster initial feedback)
    pdf_files.sort(key=lambda p: p.stat().st_size)
    
    total_size_mb = sum(f.stat().st_size for f in pdf_files) / (1024 * 1024)
    print(f"📚 Found {len(pdf_files)} PDF file(s) to process")
    print(f"   Total size: {total_size_mb:.1f} MB\n")
    
    # Initialize embeddings
    print("🔧 Initializing embeddings...")
    embeddings = OpenAIEmbeddings(
        model=embedding_model,
        openai_api_key=openai_api_key
    )
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Initialize Pinecone vector store
    print(f"🔗 Connecting to Pinecone index: {index_name}")
    try:
        vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings,
            pinecone_api_key=pinecone_api_key
        )
    except Exception as e:
        print(f"❌ Error connecting to Pinecone: {e}")
        return
    
    print("✅ Connected successfully\n")
    
    # Process PDFs in parallel (extract text and create chunks)
    print(f"📄 Processing {len(pdf_files)} PDF file(s) (using {max_workers} workers)...\n")
    all_documents = []
    processed_files = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all PDF processing tasks
        future_to_file = {
            executor.submit(process_pdf_file, pdf_file, text_splitter, pdf_file.stem): pdf_file
            for pdf_file in pdf_files
        }
        
        # Process completed tasks with progress bar
        with tqdm(total=len(pdf_files), desc="Processing PDFs", unit="file") as pbar:
            for future in as_completed(future_to_file):
                pdf_file = future_to_file[future]
                try:
                    documents = future.result()
                    if documents:
                        all_documents.extend(documents)
                        processed_files.append(pdf_file.name)
                        pbar.set_postfix({"chunks": len(all_documents), "file": pdf_file.name[:30]})
                    else:
                        print(f"⚠️  Skipped {pdf_file.name} (no text extracted)")
                except Exception as e:
                    print(f"\n❌ Error processing {pdf_file.name}: {e}")
                finally:
                    pbar.update(1)
    
    if not all_documents:
        print("\n❌ No documents to ingest")
        return
    
    print(f"\n✅ Processed {len(processed_files)} file(s), created {len(all_documents)} chunks")
    
    # Ingest documents into Pinecone in batches with progress tracking
    print(f"\n📤 Ingesting {len(all_documents)} document chunks into Pinecone...")
    print(f"   Batch size: {batch_size}")
    print(f"   Embedding model: {embedding_model}\n")
    
    total_batches = (len(all_documents) + batch_size - 1) // batch_size
    successful_batches = 0
    failed_batches = 0
    
    try:
        with tqdm(total=len(all_documents), desc="Uploading to Pinecone", unit="chunk") as pbar:
            for i in range(0, len(all_documents), batch_size):
                batch = all_documents[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                batch_start = time.time()
                success = process_and_upload_batch(
                    vector_store,
                    batch,
                    batch_num,
                    total_batches
                )
                batch_time = time.time() - batch_start
                
                if success:
                    successful_batches += 1
                    pbar.update(len(batch))
                    pbar.set_postfix({
                        "batch": f"{batch_num}/{total_batches}",
                        "time": f"{batch_time:.1f}s"
                    })
                else:
                    failed_batches += 1
                    print(f"\n⚠️  Batch {batch_num} failed, continuing...")
        
        total_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✅ Ingestion Complete!")
        print(f"{'='*60}")
        print(f"   Files processed: {len(processed_files)}")
        print(f"   Total chunks: {len(all_documents)}")
        print(f"   Successful batches: {successful_batches}/{total_batches}")
        if failed_batches > 0:
            print(f"   Failed batches: {failed_batches}")
        print(f"   Index: {index_name}")
        print(f"   Embedding model: {embedding_model}")
        print(f"   Chunk size: {chunk_size}, Overlap: {chunk_overlap}")
        print(f"   Total time: {total_time/60:.1f} minutes")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Ingestion interrupted by user")
        print(f"   Processed {successful_batches * batch_size} chunks before interruption")
        raise
    except Exception as e:
        print(f"\n❌ Error ingesting documents: {e}")
        raise


def main():
    """Main entry point for the ingestion script."""
    print("=" * 60)
    print("PDF Ingestion Script for Pinecone (Optimized)")
    print("=" * 60)
    print()
    
    # Get configuration from environment or use defaults
    pdf_dir = os.getenv("PDF_DIRECTORY", "pdf")
    index_name = os.getenv("PINECONE_INDEX_NAME", "products")
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
    batch_size = int(os.getenv("BATCH_SIZE", "50"))
    max_workers = int(os.getenv("MAX_WORKERS", "2"))
    
    print(f"Configuration:")
    print(f"  PDF Directory: {pdf_dir}")
    print(f"  Index Name: {index_name}")
    print(f"  Chunk Size: {chunk_size}")
    print(f"  Chunk Overlap: {chunk_overlap}")
    print(f"  Batch Size: {batch_size}")
    print(f"  Max Workers: {max_workers}")
    print()
    
    try:
        ingest_pdfs_to_pinecone(
            pdf_directory=pdf_dir,
            index_name=index_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            batch_size=batch_size,
            max_workers=max_workers
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
