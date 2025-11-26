import csv
import pathlib

from google import genai
from google.genai import types


def main():
    client = genai.Client(api_key="AIzaSyCxNumlNs-xAtdbys5j0a2f9OXa2q8Ayrs")

    pdf_path = pathlib.Path('Test_paper.pdf')

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=pdf_path.read_bytes(),
                mime_type="application/pdf",
            ),
            "Extract relevant triples from the given PDF. In your response, only include lines in the format 'subject "
            "| relation | object', one triple per line."
        ]
    )

    print(response.text)
    with open('out/triples_llm.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for line in response.text.splitlines():
            parts = [part.strip() for part in line.split('|')]
            if len(parts) == 3:
                writer.writerow(parts)


if __name__ == "__main__":
    main()
