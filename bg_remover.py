import streamlit as st
from rembg import remove
from PIL import Image, ImageFilter
import io
import zipfile
import os

st.title("High-Quality Image Background Remover & Resizer")

uploaded_files = st.file_uploader("Choose image files", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

final_images = []

if uploaded_files:
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)

    for uploaded_file in uploaded_files:
        # Open image and ensure correct format
        image = Image.open(uploaded_file).convert("RGBA")
        
        # Convert to bytes for rembg processing
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format='PNG')
        img_byte_array = img_byte_array.getvalue()

        # Remove background
        output = remove(img_byte_array)
        output_image = Image.open(io.BytesIO(output)).convert("RGBA")

        # Edge Smoothing: Apply slight Gaussian Blur to smooth edges
        output_image = output_image.filter(ImageFilter.GaussianBlur(0.5))

        # Create a white background (for non-transparent output)
        white_bg = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
        white_bg.paste(output_image, (0, 0), output_image)
        final_image = white_bg.convert("RGB")

        # High-Quality Resizing to 200x200 pixels
        final_image = final_image.resize((200, 200), Image.LANCZOS)

        # Convert to high-quality JPG
        jpg_filename = os.path.splitext(uploaded_file.name)[0] + ".jpg"
        final_image_path = os.path.join(temp_dir, jpg_filename)

        # Save JPG with minimal quality loss
        final_image.save(final_image_path, format="JPEG", quality=100, optimize=True, subsampling=0)

        final_images.append(final_image_path)

        # Display before and after images
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image, caption=f"Original Image: {uploaded_file.name}", use_container_width=True)
        with col2:
            st.image(final_image, caption=f"Resized & High-Quality JPG: {jpg_filename}", use_container_width=True)

    # Create and provide ZIP download option
    if final_images:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for image_path in final_images:
                zip_file.write(image_path, os.path.basename(image_path))

        zip_buffer.seek(0)
        st.download_button(
            label="Download All Images (JPG)",
            data=zip_buffer,
            file_name="final_images.zip",
            mime="application/zip"
        )
