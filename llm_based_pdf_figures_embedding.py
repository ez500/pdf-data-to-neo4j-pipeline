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


def convert_pdf_figures_to_contextualized_description(merged_pdf_file, specifiers=None):
    client = genai.Client(api_key="AIzaSyCxNumlNs-xAtdbys5j0a2f9OXa2q8Ayrs")

    image_paths = pdf_figures_extraction.fitz_extract_images_from_pdf(merged_pdf_file)

    for image_path in image_paths:
        try:
            img = Image.open(image_path)
        except FileNotFoundError:
            print("Image file not found:", image_path)
            continue

        # TODO RUN 4: ACCURACY IN PARSING (LARGE-SCALE PDF ANALYSIS VS. VECTOR-BASED ANALYSIS)

        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=merged_pdf_file.read_bytes(),
                    mime_type="application/pdf",
                ),
                img,
                f"""
                This task has four parts:\n\n
                1. Analyze the attached image (independently from all other attachments).\n\n
                2. Analyze the attached PDF (independently from all other attachments).\n\n
                3. Determine if the image is relevant to the strictly scientific topic of the PDF (i.e., no logos). 
                If the image is relevant, silently proceed to the next step. If the image is irrelevant, respond 
                with 'The attached image is irrelevant' and skip the following steps. It is important not to 
                hallucinate the attached image to be a different image that is relevant to the strictly scientific 
                topic of the PDF. To ensure this doesn't happen, independently re-analyze the image (without regard 
                to the content of the PDF), and determine whether the meaning of the image would significantly 
                contribute to the strictly scientific topic of the PDF.\n\n
                4. Summarize the attached image using the provided PDF as context.\n
                Guidelines for 4. are as follows:\n
                a. Format: Start your response with "The attached image...". Output only the description text without 
                any additional commentary or formatting.\n
                b. Contextual Relevance: Ensure the summary of the attached image ties back to the main themes and 
                findings of the provided PDF. Connect adjacent/contextual equations to the explanation of the image.\n
                c. Clarity and Conciseness: Provide a clear and concise summary of what the image represents. Take into 
                account the caption that is associated with the figure in the PDF.\n
                d. Key Elements: Highlight significant features, data points, or trends possibly shown in the image.\n
                e. Avoid Redundancy: Do not repeat information that is already clearly stated 
                in the PDF unless it is crucial for understanding the image.\n
                f. Scientific Rigor: Maintain accuracy and scientific integrity in the description.\n
                g. Length: Keep it concise, ideally between 50 and 100 words. Provide the description in a single 
                paragraph.\n
                5. Start a new paragraph in your response. Using your knowledge of the image and the PDF, determine 
                whether the image can significantly contribute to applications of the following scientific 
                specifier(s): {specifiers if specifiers is not None else "None (skip 5. entirely)"}\n
                If there are no feasible applications to this specifier(s), respond with 'There are no known 
                applications of the attached image to the provided scientific specifier(s)'.\n
                Guidelines for 5. are as follows:\n
                a. Format: Output only the text without any additional commentary or formatting.\n
                b. Contextual Relevance: Ensure the applications you propose tie back to the main findings of the 
                PDF and relevant scientific literature.\n
                c. Scientific Rigor: Propose applications that are scientifically plausible and grounded in the 
                content of the PDF and the image. Consider the novelty of the application.\n
                d. Length: Keep it concise, ideally between 50 and 100 words. Provide the applications in a 
                single paragraph.
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

    specifiers = input("Enter scientific specifier(s) for application "
                       "analysis (comma-separated, or leave blank to skip): ")

    convert_pdf_figures_to_contextualized_description(Path('context/merged/concatenated.pdf'),
                                                      specifiers=specifiers.strip() if specifiers.strip() else None)
    # clear_undescribed_folders(Path('out/figures'))
    # print(num_figures(Path('context/Nano-11 _ 2.pdf')))
