import spacy
import en_core_web_sm

def main():
    nlp = spacy.load("en_core_web_sm")
    # nlp = en_core_web_sm.load()

    doc = nlp("This is a test.")
    print([(w.text, w.pos_) for w in doc])

if __name__ == "__main__":
    main()
