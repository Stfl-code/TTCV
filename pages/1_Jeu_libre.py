import streamlit as st
import gspread
import pandas as pd
import random
import itertools
import sys
sys.path.append('..')  # Pour importer depuis la racine
from utils import init_google_sheets

#############
# Affichage #
#############
st.set_page_config(page_title="Jeu libre", page_icon="🏆")
st.image("images/WIP2.jpg", use_container_width=True) 

st.header("Je finis de peaufiner la partie championnat et je ferai ensuite le jeu libre 😉")