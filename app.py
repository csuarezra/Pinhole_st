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

col1, col2 = st.columns(2)



st.markdown("<h1 style='text-align: center;'>Pinhole Depth Detector</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Pinhole Depth Detector></h2>", unsafe_allow_html=True)

images = st.file_uploader("Drop your images", accept_multiple_files=True)
img_path = "img.jpg"

for image in images:
    # Saves
    img = Image.open(image)
    img = img.save("img.jpg")

    depth = imp.complete_depth(img_path)
    print(depth)

if os.path.exists(img_path):
    os.remove(img_path)