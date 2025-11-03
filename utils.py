# utils.py
import streamlit as st
import gspread

def init_google_sheets():
    """Initialise la connexion Google Sheets si nécessaire"""
    if 'sheets_loaded' not in st.session_state:
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        sh = gc.open_by_key(st.secrets["sheet"]["id"])
        
        # Charger tous les worksheets
        st.session_state.sheet_joueurs = sh.worksheet("joueurs")
        st.session_state.sheet_resultats_simp = sh.worksheet("resultats_simple")
        st.session_state.sheet_resultats_doub = sh.worksheet("resultats_double")
        st.session_state.sheet_tournoi = sh.worksheet("tournoi")
        st.session_state.sheet_championnat = sh.worksheet("championnat")
        
        # Charger les joueurs
        prenoms = st.session_state.sheet_joueurs.col_values(1)[1:]
        noms = st.session_state.sheet_joueurs.col_values(2)[1:]
        st.session_state.liste_joueurs_complet = [f"{p} {n}" for p, n in zip(prenoms, noms)]
        
        st.session_state.sheets_loaded = True