import os
import streamlit as st
import numpy as np
import pandas as pd
import image_processing as imp


from matplotlib import pyplot as plt
from PIL import Image

image = Image.open('images/vitro_logo.png')
image2 = Image.open('images/ai_logo.png')
img_path = "img.jpg"


st.set_page_config(page_title="Pinhole Depth",page_icon=':robot_face:')

def move_focus():
    # inspect the html to determine which control to specify to receive focus (e.g. text or textarea).
    st.components.v1.html(
        f"""
            <script>
                var textarea = window.parent.document.querySelectorAll("textarea[type=textarea]");
                for (var i = 0; i < textarea.length; ++i) {{
                    textarea[i].focus();
                }}
            </script>
        """,
    )

def stick_it_good():

    # make header sticky.
    st.markdown(
        """
            <div class='fixed-header'/>
            <style>
                div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                    position: sticky;
                    top: 2.875rem;
                    background-color: #0e1117;
                    z-index: 999;
                }
                .fixed-header {
                    border-bottom: 1px solid white;
                }
            </style>
        """,
        unsafe_allow_html=True
    )


def process_images(images, bandpass=True, sobel=False, edge=False):
    results = []

    for image in images:
        # Saves
        img = Image.open(image)
        img = img.save("img.jpg")

        depth = imp.complete_depth(img_path, bandpass=bandpass, sobel=sobel, edge=edge)
        results.append({'image': os.path.splitext(image.name)[0], 'depth': depth})

    if os.path.exists(img_path):
        os.remove(img_path)

    df = pd.DataFrame(results)
    return df    


def main():
    
    foot = f"""
    <div style="
        position: fixed;
        bottom: 0;
        left: 30%;
        right: 0;
        width: 50%;
        padding: 0px 0px;
        text-align: center;
    ">
        <p>Made by <a href='https://www.vitro.com/es/inicio/'>Vitro</a></p>
    </div>
    """

    st.markdown(foot, unsafe_allow_html=True)
    
    # Add custom CSS
    st.markdown(
        """
        <style>
        
        #MainMenu {visibility: hidden;
        # }
            footer {visibility: hidden;
            }
            .css-card {
                border-radius: 0px;
                padding: 30px 10px 10px 10px;
                background-color: #f8f9fa;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 10px;
                font-family: "IBM Plex Sans", sans-serif;
            }
            
            .card-tag {
                border-radius: 0px;
                padding: 1px 5px 1px 5px;
                margin-bottom: 10px;
                position: absolute;
                left: 0px;
                top: 0px;
                font-size: 0.6rem;
                font-family: "IBM Plex Sans", sans-serif;
                color: white;
                background-color: green;
                }
                
            .css-zt5igj {left:0;
            }
            
            span.css-10trblm {margin-left:0;
            }
            
            div.css-1kyxreq {margin-top: -40px;
            }
            
           
       
            
          

        </style>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.image("images/ai_logo.png")


   

   
    with st.container():
        st.write(
            f"""
            <div style="display: flex; align-items: center; margin-left: 0;">
                <h1 style="display: inline-block;">Pinhole Depth Estimator</h1>
                <sup style="margin-left:5px;font-size:small; color: green;">beta</sup>
            </div>
            """,
            unsafe_allow_html=True,
        )
        stick_it_good()
    
    


    
    
    st.sidebar.title("Menu")
    
    filter_option = st.sidebar.selectbox(
        "Choose Filter", ["Bandpass", "Bandpass + Sobel", "HPF + Blur"])

    
    edge_option = st.sidebar.radio(
        "Detect Edges?", ["No", "Yes"])

    images = st.file_uploader("Drop your images", accept_multiple_files=True, type=["jpg", "png", "jpeg"])

    if images:
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

        if filter_option == "Bandpass":
            bandpass = True
            sobel = False
        elif filter_option == "Bandpass + Sobel":
            bandpass = True
            sobel = True
        else:
            bandpass = False
            sobel = False

        edge = True if edge_option == "Yes" else False

        if proc_btn:
            table = process_images(images, bandpass=bandpass, sobel=sobel, edge=edge)
            block.table(table)
            st.download_button(
                label="Download data as CSV",
                data=table.to_csv().encode('utf-8'),
                file_name='depths.csv',
                mime='text/csv'
            )

        
        

if __name__ == "__main__":
    main()

