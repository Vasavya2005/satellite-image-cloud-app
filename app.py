
from io import BytesIO
import os

import boto3
import streamlit as st
from PIL import Image, ImageEnhance

st.set_page_config(
    page_title="Satellite Image Cloud Application",
    page_icon="🛰️",
    layout="wide"
)

st.title("Satellite Image Processing Using AWS Cloud")
st.write("Upload, process, and store satellite images.")

uploaded_file = st.file_uploader(
    "Upload a satellite image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    try:
        original = Image.open(uploaded_file)
        original.load()
        original = original.convert("RGB")

        col1, col2, col3 = st.columns(3)
        col1.metric("Width", f"{original.width} pixels")
        col2.metric("Height", f"{original.height} pixels")
        col3.metric(
            "File size",
            f"{uploaded_file.size / 1024:.2f} KB"
        )

        operation = st.selectbox(
            "Select processing method",
            ["Original", "Grayscale", "Enhance Contrast"]
        )

        if operation == "Grayscale":
            processed = original.convert("L").convert("RGB")
        elif operation == "Enhance Contrast":
            processed = ImageEnhance.Contrast(original).enhance(1.8)
        else:
            processed = original.copy()

        left, right = st.columns(2)

        with left:
            st.subheader("Original")
            st.image(original, width="stretch")

        with right:
            st.subheader("Processed")
            st.image(processed, width="stretch")

        buffer = BytesIO()
        processed.save(buffer, format="PNG")
        processed_bytes = buffer.getvalue()

        st.download_button(
            "Download processed image",
            data=processed_bytes,
            file_name="processed_satellite.png",
            mime="image/png"
        )

        bucket_name = os.getenv("S3_BUCKET")

        if bucket_name:
            if st.button("Save images to AWS S3"):
                try:
                    # On EC2, boto3 uses the attached IAM role.
                    s3 = boto3.client("s3")

                    original_buffer = BytesIO()
                    original.save(original_buffer, format="PNG")

                    s3.put_object(
                        Bucket=bucket_name,
                        Key="uploads/original_satellite.png",
                        Body=original_buffer.getvalue(),
                        ContentType="image/png"
                    )

                    s3.put_object(
                        Bucket=bucket_name,
                        Key="processed/processed_satellite.png",
                        Body=processed_bytes,
                        ContentType="image/png"
                    )

                    st.success(
                        f"Images saved to S3 bucket: {bucket_name}"
                    )

                except Exception as error:
                    st.error(
                        "S3 upload failed. Check the EC2 role, "
                        "bucket name, and AWS Region."
                    )
                    st.exception(error)
        else:
            st.info(
                "S3 upload will be available after the application "
                "is configured on AWS."
            )

    except Exception:
        st.error("Unable to process this image. Try another JPG or PNG.")

else:
    st.info("Upload an image to get started.")

st.caption("Academic project demonstration")
