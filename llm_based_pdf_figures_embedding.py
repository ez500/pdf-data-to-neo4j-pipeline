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
                This task has two parts:\n\n
                1. You must first determine if the attached image is relevant to the content matter and research topic 
                of the PDF by locating the asset on the provided PDF and analyzing surrounding
                context/captions/equations. If the image is deemed irrelevant, respond with 'The attached image is 
                irrelevant' and skip the second part. Do not proceed to the second part and summarize another figure in 
                the PDF if the given image is irrelevant.\n\n
                2. Summarize the attached image using the provided PDF as context. Guidelines are as follows:\n
                1. Format: Start your response with "The attached image...". Output only the description text without
                any additional commentary or formatting.\n
                2. Contextual Relevance: Ensure the summary of the attached image ties back to the main themes and 
                findings of the provided PDF. Connect adjacent/contextual equations to the explanation of the image.\n
                3. Clarity and Conciseness: Provide a clear and concise summary of what the image represents. Take into 
                account the caption that is associated with the figure in the PDF.\n
                4. Key Elements: Highlight significant features, data points, or trends possibly shown in the image.\n
                5. Avoid Redundancy: Do not repeat information that is already clearly stated 
                in the PDF unless it is crucial for understanding the image.\n
                6. Scientific Rigor: Maintain accuracy and scientific integrity in the description.\n
                7. Length: Keep it concise, ideally between 50 and 100 words. Provide the description in a single 
                paragraph.\n
                """
            ]
        )

        if result.text is not None and ('The attached image is irrelevant' in result.text.strip()):
            print(f"Image at {image_path} deemed irrelevant to the PDF content. Skipping description.")
            continue

        with (open(Path(image_path).parent / f'description-{Path(image_path).stem}', 'w', newline='', encoding='utf-8')
              as file):
            file.write(result.text)
            print(f"Description for {image_path} written to {Path(image_path).parent / 'description'}")


# Delete the image/figure directory if it does not contain a description file
def clear_undescribed_folders(output_path):
    for root, dirs, files in os.walk(output_path):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            description_file = dir_path / f'description-{dir_name}'
            if not os.path.isfile(description_file):
                for item in os.listdir(dir_path):
                    item_path = dir_path / item
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    else:
                        os.rmdir(item_path)
                os.rmdir(dir_path)
                print(f"Removed undescribed folder: {dir_path}")


if __name__ == "__main__":
    pdf_files = glob.glob(pdf_directory + '/*.pdf')
    merger = PdfMerger()

    for pdf_file in pdf_files:
        merger.append(pdf_file)

    with open('context/merged/concatenated.pdf', 'wb') as f_out:
        merger.write(f_out)

    convert_pdf_figures_to_contextualized_description(Path('context/merged/concatenated.pdf'))
    # clear_undescribed_folders(Path('out/figures'))
    # print(num_figures(Path('context/Nano-11 _ 2.pdf')))
