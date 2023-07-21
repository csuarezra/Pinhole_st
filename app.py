import os
import streamlit as st
import numpy as np
import pandas as pd
import itertools
import base64
import image_processing as imp

from pathlib import Path
from matplotlib import pyplot as plt
from PIL import Image

image = Image.open('images/vitro_logo.png')
img_path = "img.jpg"

def process_images(images):
    results = []

    for image in images:
        # Saves
        img = Image.open(image)
        img = img.save("img.jpg")

        depth = imp.complete_depth(img_path)
        results.append({'image': os.path.splitext(image.name)[0], 'depth': depth})

    if os.path.exists(img_path):
        os.remove(img_path)

    df = pd.DataFrame(results)
    return df    


col1, col2 = st.columns([0.3, 0.7])
with col1:
    st.image(image, width=200)
with col2:
    #st.title("VitroGPT")
    st.markdown("<h1 style='text-align: center;'>Pinhole Depth Detector</h1>", unsafe_allow_html=True)


#st.markdown("<h1 style='text-align: center;'>Pinhole Depth Detector</h1>", unsafe_allow_html=True)
#st.markdown("<h2 style='text-align: center;'>Pinhole Depth Detector></h2>", unsafe_allow_html=True)
st.markdown("---")

images = st.file_uploader("Drop your images", accept_multiple_files=True, type=["jpg", "png", "jpeg"])

col1, col2, col3 , col4, col5 = st.columns(5)

with col1:
    pass
with col2:
    pass
with col4:
    pass
with col5:
    pass
with col3 :
    proc_btn = col3.button("Process")


st.markdown("---")

block = st.empty()

if proc_btn:
    if not images:
        st.warning("Please, upload some images.")
    else:
        table = process_images(images)
        block.table(table)
        st.download_button(
            label="Download data as CSV",
            data=table.to_csv().encode('utf-8'),
            file_name='depths.csv',
            mime='text/csv'
        )
        