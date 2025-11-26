import csv
import glob
import pathlib

from google import genai
from google.genai import types
from PyPDF2 import PdfMerger


pdf_directory = "context"


def convert_pdf_to_triples(pdf_file):
    client = genai.Client(api_key="AIzaSyCxNumlNs-xAtdbys5j0a2f9OXa2q8Ayrs")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=pdf_file.read_bytes(),
                mime_type="application/pdf",
            ),
            "Extract relevant triples from the given PDF. In your response, the first line has to be 'subject | "
            "relation | object' with succeeding lines in the format 'subject | relation | object', one triple per line."
        ]
    )

    with open('out/triples_llm.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for line in response.text.splitlines():
            parts = [part.strip() for part in line.split('|')]
            if len(parts) == 3:
                writer.writerow(parts)

    print("Triples written to out/triples_llm.csv:")
    print(response.text)


if __name__ == "__main__":
    pdf_files = glob.glob(pdf_directory + '/*.pdf')
    merger = PdfMerger()

    for file in pdf_files:
        merger.append(file)

    merger.write('context/concatenated.pdf')

    convert_pdf_to_triples(pathlib.Path('context/concatenated.pdf'))
