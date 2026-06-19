from pypdf import PdfReader
from docx import Document


def read_txt(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


def read_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def read_docx(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:

        text += paragraph.text + "\n"

    return text


def extract_text(file_path):

    if file_path.endswith(".txt"):
        return read_txt(file_path)

    if file_path.endswith(".pdf"):
        return read_pdf(file_path)

    if file_path.endswith(".docx"):
        return read_docx(file_path)

    return "Unsupported file format."