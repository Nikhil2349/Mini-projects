import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile
import os

st.title("Image Background Remover & Resizer")

uploaded_files = st.file_uploader("Choose image files", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

final_images = []

if uploaded_files:
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)

    for uploaded_file in uploaded_files:
        # Open image
        image = Image.open(uploaded_file)
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format='PNG')
        img_byte_array = img_byte_array.getvalue()

        # Remove background
        output = remove(img_byte_array)
        output_image = Image.open(io.BytesIO(output))

        # Add white background
        white_bg = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
        white_bg.paste(output_image, (0, 0), output_image)
        final_image = white_bg.convert("RGB")

        # Resize image to 200x200 pixels
        final_image = final_image.resize((200, 200))

        # Save image
        final_image_path = os.path.join(temp_dir, f"{uploaded_file.name}")
        final_image.save(final_image_path)
        final_images.append(final_image_path)

        # Display images
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image, caption=f"Original Image: {uploaded_file.name}", use_container_width=True)
        with col2:
            st.image(final_image, caption=f"Resized Image (200x200): {uploaded_file.name}", use_container_width=True)

    # Create and provide ZIP download option
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
