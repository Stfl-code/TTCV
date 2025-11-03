import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# URL de l'image
url_image = "https://vauxttc.fr/wp-content/uploads/2025/05/telechargement-65x65.webp"
# Afficher l'image depuis l'URL
st.image(url_image, use_container_width=True)

# Titre
st.markdown("<h1 style='text-align: center;'>Menu principal</h1>", unsafe_allow_html=True)
st.markdown("<h2>Veuillez sélectionner une page via le menu déroulant ci-dessous ou le menu latéral.</h2>", unsafe_allow_html=True)

# Liste des pages disponibles (correspond au nom des fichiers sans les préfixes numériques)
pages = {
    "Jeu libre": "Jeu libre",
    "Championnat": "Championnat"
}

# Menu déroulant
st.markdown(f"<p style='font-size:{18}px;'><strong>Sélectionnez une page :</strong></p>", unsafe_allow_html=True)
selected_page = st.selectbox("", options=list(pages.keys()))

# Rediriger vers la page sélectionnée
if st.button("Aller à la page sélectionnée"):
    switch_page(pages[selected_page])