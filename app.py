import streamlit as st
from PIL import Image

from search_duplicate import search_duplicate
from transfer_created import ocp_transfer_created
from transfer_amended import transfer_amend
from merge import merge
from logical_check import examine
from find_repeat import find_repeat
from country_profile import get_profile


selectbox = st.sidebar.selectbox(
    'What do you want to do?',
    ('Home Page', 'Transfer OCP Created Project', 'Transfer OCP Amended Project',
     'Search Duplicate', 'Merge', 'Logical Consistency Check', 'Find Repeat','Country Profile')
)

st.sidebar.info("View [source code](https://github.com/wpan03/tdf_app)")

if selectbox == 'Home Page':
    st.title("Welcome！")
    st.markdown("This website contains some useful techniques for TUFF's work. ")
    st.markdown('**Please choose what you want to do in the side bar.**')
    st.markdown('If you are here to **transfer projects** among stages, please see detailed instructions [here](https://docs.google.com/document/d/1Yfj52s-5jL8ActupitHKBFT-8E3qW6wHm5SWotvtla8/edit).')
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

elif selectbox == 'Country Profile':
    get_profile()
