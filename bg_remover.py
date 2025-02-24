import streamlit as st
from rembg import remove
from PIL import Image, ImageFilter
import io
import zipfile
import os

st.set_option("server.maxUploadSize", 300)
st.title("Image Background Remover")

uploaded_files = st.file_uploader("Choose image files", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

final_images = []

if uploaded_files is not None:
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format='PNG')
        img_byte_array = img_byte_array.getvalue()

        output = remove(img_byte_array)
        output_image = Image.open(io.BytesIO(output))

        white_bg = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
        white_bg.paste(output_image, (0, 0), output_image)
        final_image = white_bg.convert("RGB")

        final_image_path = os.path.join(temp_dir, f"{uploaded_file.name}")
        final_image.save(final_image_path)
        final_images.append(final_image_path)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image, caption=f"Original Image: {uploaded_file.name}", use_container_width=True)
        with col2:
            st.image(final_image, caption=f"Image with White Background: {uploaded_file.name}", use_container_width=True)

    if final_images:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for image_path in final_images:
                zip_file.write(image_path, os.path.basename(image_path))
        
        zip_buffer.seek(0)
        st.download_button(
            label="Download All Images",
            data=zip_buffer,
            file_name="final_images.zip",
            mime="application/zip"
        )
