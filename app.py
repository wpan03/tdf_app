import streamlit as st
import pandas as pd 
import base64
import webbrowser
from PIL import Image

from search_duplicate import search_duplicate
from transfer_created import ocp_transfer_created
from transfer_amended import transfer_amend
from merge import merge
from logical_check import examine
from find_repeat import find_repeat


selectbox = st.sidebar.selectbox(
    'What do you want to do?',
    ('Home Page','Transfer OCP Created Project', 'Transfer OCP Amended Project', 
    'Search Duplicate','Merge', 'Logical Consistency Check', 'Find Repeat')
)

st.sidebar.info("View [source code](https://github.com/wpan03/tdf_app)")

if selectbox == 'Home Page':
  st.title("Welcome！")
  st.markdown("This website contains some useful techniques for TUFF's work. ")
  st.markdown('**Please choose what you want to do in the side bar.**')
  image = Image.open('sunrise.png')
  st.image(image, use_column_width=True)

elif selectbox == 'Transfer OCP Created Project':
  ocp_transfer_created()
  
elif selectbox == "Transfer OCP Amended Project":
  transfer_amend()

elif selectbox == 'Search Duplicate':
  search_duplicate()

elif selectbox == "Merge":
  merge()

elif selectbox == 'Logical Consistency Check':
    examine()

elif selectbox == 'Find Repeat':
  find_repeat()