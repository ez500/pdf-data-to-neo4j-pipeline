import spacy
import en_core_web_sm
import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = []
    with open(pdf_path, 'r') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text.append(page.extract_text())
    return "\n".join(text)

def main():
    nlp = spacy.load("en_core_web_sm")
    nlp2 = en_core_web_sm.load()

    path = ""
    doc = nlp(extract_text_from_pdf(path))
    print([(w.text, w.pos_) for w in doc])

if __name__ == "__main__":
    main()
