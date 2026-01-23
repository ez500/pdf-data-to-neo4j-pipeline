import csv
import glob
import pathlib

from google import genai
from google.genai import types
from PyPDF2 import PdfMerger


pdf_directory = "context"


def convert_pdf_figures_to_embeddings(merged_pdf_file):
    client = genai.Client(api_key="AIzaSyCxNumlNs-xAtdbys5j0a2f9OXa2q8Ayrs")

    result = client.models.embed_content(
        model="gemini-embedding-001",
        # contents=[
        #     types.Part.from_bytes(
        #         data=merged_pdf_file.read_bytes(),
        #         mime_type="application/pdf",
        #     ),
        #     "Extract relevant relationships from the given PDF in the context of optimizing food formulations. "
        #     "That is, relationships must explicitly define the state of one loosely-biological object relating to "
        #     "another loosely-biological object in a loosely-biological relationship (words like 'inhibit', 'boosts', "
        #     "'creates', etc.). In your response, the first line has to be 'subject | relation | object' with "
        #     "succeeding lines in the format 'subject | relation | object', one triple per line."
        # ]
        contents="This is a test sentence."
    )

    # with open('out/triples_llm.csv', 'w', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     for line in response.text.splitlines():
    #         parts = [part.strip() for part in line.split('|')]
    #         if len(parts) == 3:
    #             writer.writerow(parts)

    print(result.embeddings)


if __name__ == "__main__":
    pdf_files = glob.glob(pdf_directory + '/*.pdf')
    merger = PdfMerger()

    for pdf_file in pdf_files:
        merger.append(pdf_file)

    with open('context/merged/concatenated.pdf', 'wb') as f_out:
        merger.write(f_out)

    convert_pdf_figures_to_embeddings(pathlib.Path('context/merged/concatenated.pdf'))
