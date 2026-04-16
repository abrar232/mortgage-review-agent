import logging
from pathlib import Path
from dataclasses import dataclass

import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)


@dataclass
class ParsedDocument:
    file_name: str
    file_type: str
    raw_text: str
    page_count: int


def parse_pdf(file_path: str) -> ParsedDocument:
    path = Path(file_path)
    pages = []

    with pdfplumber.open(file_path) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())

    raw_text = "\n\n".join(pages)
    logger.info(f"Parsed PDF: {path.name} | pages={page_count} | chars={len(raw_text)}")

    return ParsedDocument(
        file_name=path.name,
        file_type="pdf",
        raw_text=raw_text,
        page_count=page_count,
    )


def parse_docx(file_path: str) -> ParsedDocument:
    path = Path(file_path)
    doc = Document(file_path)

    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    raw_text = "\n\n".join(paragraphs)
    logger.info(f"Parsed DOCX: {path.name} | paragraphs={len(paragraphs)} | chars={len(raw_text)}")

    return ParsedDocument(
        file_name=path.name,
        file_type="docx",
        raw_text=raw_text,
        page_count=len(paragraphs),
    )


def parse_document(file_path: str) -> ParsedDocument:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        return parse_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Expected .pdf or .docx")