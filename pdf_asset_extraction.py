import fitz


def extract_images_from_pdf(pdf_path):
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


if __name__ == "__main__":
    pdf_file_path = "context/Nano-11 _ 1.pdf"
    extract_images_from_pdf(pdf_file_path)
