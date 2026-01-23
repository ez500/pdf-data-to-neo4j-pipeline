import io
import os

import fitz
from PIL import Image
from PyPDF2 import PdfReader


def fitz_extract_images_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"out/image_page{page_num+1}_{img_index+1}.{image_ext}"

            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)

            print(f"Extracted image saved as: {image_filename}")


def pdf_reader_extract_images_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    image_cnt = 0

    for page_num, page in enumerate(reader.pages, start=1):
        resources = page["/Resources"].get_object()
        if "/XObject" not in resources:
            continue

        xobjects = resources["/XObject"].get_object()

        for name in xobjects:
            obj = xobjects[name].get_object()
            if obj.get("/Subtype") != "/Image":
                continue

            image_cnt += 1
            image_data = obj.get_data()
            width = obj["/Width"]
            height = obj["/Height"]
            color_space = obj.get("/ColorSpace", "/DeviceRGB")

            if color_space == "/DeviceGray":
                mode = "L"
            elif color_space == "/DeviceCMYK":
                mode = "CMYK"
            else:
                mode = "RGB"

            try:
                img = Image.frombytes(mode, (width, height), image_data)
            except Exception as _:
                img = Image.open(io.BytesIO(image_data))

            if img.mode == "CMYK":
                img = img.convert("RGB")

            filename = f"page{page_num}_image{image_cnt}.png"
            img.save(os.path.join("out", filename))

            print(f"Extracted image saved as: out/{filename}")
        print(f"Total images extracted: {image_cnt}")


if __name__ == "__main__":
    pdf_file_path = "context/Nano-11 _ 1.pdf"
    pdf_reader_extract_images_from_pdf(pdf_file_path)
