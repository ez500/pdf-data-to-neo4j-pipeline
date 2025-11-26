import os

import PyPDF2
import en_core_web_sm
import pandas as pd
import pdfplumber
import spacy
import textacy
from llmsherpa.readers import LayoutPDFReader


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

def extract_triples(res):
    entities = []
    relations = []
    triples = []

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

    for triple in textacy.extract.subject_verb_object_triples(res):
        subject = " ".join(token.text for token in triple.subject)
        verb = " ".join(token.text for token in triple.verb)
        object_ = " ".join(token.text for token in triple.object)
        triples.append({
            "subject": subject,
            "relation": verb,
            "object": object_
        })

    # BIO_KEYWORDS = ["activate", "increase", "inhibit", "bind", "express", "secrete", "induce"]
    # filtered = [t for t in triples if any(k in t["relation"].lower() for k in BIO_KEYWORDS)]

    return entities, relations, triples


def ingest_pdfs_llmsherpa(docs, nlp):

    entities = []
    relations = []
    triples = []

    for doc in docs:
        doc_name_val = os.path.basename(doc[1])

        # TODO INDIVIDUALLY PROCESS TABLES
        for chunk in [chk for chk in doc[0].chunks() if chk.tag == 'para']:
            if chunk.to_text().startswith("Received"):
                break
            if chunk.to_text().startswith("URLs") or len(chunk.to_text()) < 40:
                continue
            print(chunk.to_text())
            res = nlp(chunk.to_text(include_children=True))

            new_entities, new_relations, new_triples = extract_triples(res)
            entities.extend(new_entities)
            relations.extend(new_relations)
            triples.extend(new_triples)

        for table in doc[0].tables():
            print(table.to_text())
            res = nlp(table.to_text(include_children=True))

            new_entities, new_relations, new_triples = extract_triples(res)
            entities.extend(new_entities)
            relations.extend(new_relations)
            triples.extend(new_triples)


        print(f'\'{doc_name_val}\' Done! Summary: ')
        print('#Sections: ' + str(len(doc[0].sections())))
        print('#Chunks: ' + str(len(doc[0].chunks())))
        print('#Tables: ' + str(len(doc[0].tables())))

    return entities, relations, triples

def main():
    nlp = spacy.load("en_ner_bionlp13cg_md")
    nlp = en_core_web_sm.load()

    for name, proc in nlp.pipeline:
        if name == "parser":
            nlp.add_pipe("merge_noun_chunks")

    # docs on how to start the server up: https://github.com/nlmatics/nlm-ingestor#
    pdf_reader = LayoutPDFReader("http://localhost:5010/api/parseDocument?renderFormat=all")

    path = "context/sample.pdf"
    path_tables = "context/sample-tables.pdf"
    path_test = "context/Test_paper.pdf"

    entities, relations, triples = ingest_pdfs_llmsherpa(
        [(pdf_reader.read_pdf(path_test), path_test)], nlp)

    dataframe_entities = pd.DataFrame(entities)
    dataframe_entities.to_csv("out/entities.csv", index=False)

    dataframe_relations = pd.DataFrame(relations)
    dataframe_relations.to_csv("out/relations.csv", index=False)

    dataframe_triples = pd.DataFrame(triples)
    dataframe_triples.to_csv('out/triples.csv', index=False)

    print(extract_text_from_pdf_pypdf2(path))
    doc = nlp(extract_text_from_pdf_pypdf2(path))
    print([(w.text, w.pos_) for w in doc])

if __name__ == "__main__":
    main()
