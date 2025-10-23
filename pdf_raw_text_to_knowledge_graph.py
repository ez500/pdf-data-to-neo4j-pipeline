import spacy
import en_core_web_sm
import PyPDF2
import pdfplumber

def extract_text_from_pdf_pypdf2(pdf_path):
    text = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text.append(page.extract_text())
    return "\n".join(text)

def extract_text_from_pdf_plumber(pdf_path):
    text = []
    with pdfplumber.open(pdf_path) as file:
        for page in file.pages:
            text.append(page.extract_text())
    return "\n".join(text)

def main():
    nlp = spacy.load("en_core_web_sm")
    nlp2 = en_core_web_sm.load()

    path = "sample.pdf"
    print(extract_text_from_pdf_pypdf2(path))
    doc = nlp(extract_text_from_pdf_pypdf2(path))
    print([(w.text, w.pos_) for w in doc])

if __name__ == "__main__":
    main()
