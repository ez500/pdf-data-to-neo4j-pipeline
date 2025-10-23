import os

import spacy
import en_core_web_sm
from llmsherpa.readers import LayoutPDFReader
import pandas as pd
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

def ingest_pdfs_llmsherpa(docs, nlp):

    entities = []
    relations = []

    for doc in docs:
        doc_name_val = os.path.basename(doc[1])

        # TODO INDIVIDUALLY PROCESS TABLES
        for chunk in doc[0].chunks():
            print(chunk.to_text())
            res = nlp(chunk.to_text(include_children=True))

            for ent in res.ents:
                entities.append({"text": ent.text, "label": ent.label_})

            for token in res:
                if token.dep_ == "ROOT" and token.pos_ == "VERB":
                    subject = [child for child in token.children if "subj" in child.dep_]
                    obj = [child for child in token.children if "obj" in child.dep_]
                    if subject and obj:
                        relations.append({
                            "subject": subject[0].text,
                            "relation": token.text,
                            "object": obj[0].text,
                        })


        print(f'\'{doc_name_val}\' Done! Summary: ')
        print('#Sections: ' + str(len(doc[0].sections())))
        print('#Chunks: ' + str(len(doc[0].chunks())))
        print('#Tables: ' + str(len(doc[0].tables())))

    return entities, relations

def main():
    nlp = spacy.load("en_core_web_sm")
    nlp2 = en_core_web_sm.load()

    # docs on how to start the server up: https://github.com/nlmatics/nlm-ingestor#
    pdf_reader = LayoutPDFReader("http://localhost:5010/api/parseDocument?renderFormat=all")

    path = "sample.pdf"
    path_tables = "sample-tables.pdf"

    entities, relations = ingest_pdfs_llmsherpa(
        [(pdf_reader.read_pdf(path), path), (pdf_reader.read_pdf(path_tables), path_tables)], nlp)

    dataframe_entities = pd.DataFrame(entities)
    dataframe_entities.to_csv("out/entities.csv", index=False)

    dataframe_relations = pd.DataFrame(relations)
    dataframe_relations.to_csv("out/relations.csv", index=False)

    # print(extract_text_from_pdf_pypdf2(path))
    # doc = nlp(extract_text_from_pdf_pypdf2(path))
    # print([(w.text, w.pos_) for w in doc])

if __name__ == "__main__":
    main()
