import glob
import os
from pathlib import Path

from PIL import Image
from PyPDF2 import PdfMerger
from google import genai
from google.genai import types

import pdf_figures_extraction

pdf_directory = "context"


def num_figures(pdf):
    client = genai.Client(api_key="AIzaSyCxNumlNs-xAtdbys5j0a2f9OXa2q8Ayrs")

    result = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=pdf.read_bytes(),
                mime_type="application/pdf",
            ),
            "How many figures are in the given PDF? Provide only the number as an integer."
        ]
    )

    return result.text


# TODO Prompt with PDF for context, iterate prompt for each asset, format with integrated context (paper citation?),
#  output into a subdirectory within figure directory for each figure containing the original exported figure
#  as well as the raw description.

def convert_pdf_figures_to_contextualized_description(merged_pdf_file):
    client = genai.Client(api_key="AIzaSyCxNumlNs-xAtdbys5j0a2f9OXa2q8Ayrs")

    image_paths = pdf_figures_extraction.fitz_extract_images_from_pdf(merged_pdf_file)

    for image_path in image_paths:
        try:
            img = Image.open(image_path)
        except FileNotFoundError:
            print("Image file not found:", image_path)
            continue

        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=merged_pdf_file.read_bytes(),
                    mime_type="application/pdf",
                ),
                img,
                """
                The Big Idea: Summarize the image using the context of the PDF provided. Guidelines are as follows:\n
                1. Contextual Relevance: Ensure the description ties back to the main themes and findings of the PDF.
                2. Clarity and Conciseness: Provide a clear and concise summary of what the image represents. Take into
                account the caption that is associated with the figure in the PDF.
                3. Key Elements: Highlight significant features, data points, or trends possibly shown in the image.
                4. Avoid Redundancy: Do not repeat information that is already clearly stated
                in the PDF unless it is crucial for understanding the image.
                5. Scientific Rigor: Maintain accuracy and scientific integrity in the description.
                Provide the description in a single paragraph.
                6. Format: Output only the description text without any additional commentary or formatting.
                7. Length: Keep it concise, ideally between 50 and 100 words.
                8. IMPORTANT: If the image is not relevant to the content of the PDF, respond with 'irrelevant image'.
                """
            ]
        )

        if result.text is not None and result.text.strip().lower() == 'irrelevant image':
            print(f"Image at {image_path} deemed irrelevant to the PDF content. Skipping description.")
            # Delete the image/figure directory
            os.remove(image_path)
            os.rmdir(Path(image_path).parent)
            continue

        with open(Path(image_path).parent / 'description', 'w', newline='', encoding='utf-8') as file:
            file.write(result.text)
            print(f"Description for {image_path} written to {Path(image_path).parent / 'description'}")


if __name__ == "__main__":
    pdf_files = glob.glob(pdf_directory + '/*.pdf')
    merger = PdfMerger()

    for pdf_file in pdf_files:
        merger.append(pdf_file)

    with open('context/merged/concatenated.pdf', 'wb') as f_out:
        merger.write(f_out)

    # convert_pdf_figures_to_contextualized_description(Path('context/merged/concatenated.pdf'))
    print(num_figures(Path('context/Nano-11 _ 2.pdf')))
