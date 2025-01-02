import streamlit as st
from PIL import Image
import easyocr
import numpy as np

def extract_text_from_image(image):
    """Extract text from the given image using EasyOCR."""
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader
    image_np = np.array(image)  # Convert PIL image to NumPy array
    results = reader.readtext(image_np)
    
    # Combine text from all detected regions
    extracted_text = "\n".join([result[1] for result in results])
    return extracted_text

def main():
    st.title("Image Text Extraction App")
    st.write("Upload an image, and the app will extract any text it contains.")

    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Open the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        st.write("Processing the image...")
        
        # Extract text from the image
        extracted_text = extract_text_from_image(image)

        if extracted_text.strip():
            st.subheader("Extracted Text:")
            st.text_area("", extracted_text, height=300)
        else:
            st.write("No text found in the image.")

if __name__ == "__main__":
    main()
