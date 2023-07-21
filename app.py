import streamlit as st
import cv2
import numpy as np
import math
from scipy import fftpack
from scipy.signal import find_peaks
import pandas as pd
import itertools
import base64

from pathlib import Path
from matplotlib import pyplot as plt

col1, col2 = st.columns(2):



st.markdown("<h1 style='text-align: center;'>Pinhole Depth Detector</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Pinhole Depth Detector></h2>")

images = st.file_uploader("Drop your images", accept_multiple_files=True)

for image in images:
    pass