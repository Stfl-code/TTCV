import streamlit as st
import gspread
import pandas as pd
import sys
sys.path.append('..')  # Pour importer depuis la racine
from utils import init_google_sheets

#############
# Affichage #
#############
st.set_page_config(page_title="Archive", page_icon="🏆")
st.image("images/Archive.jpg", use_container_width=True)
st.write("# Archive des Championnats interne du club de tennis de table de Vaux-sur-Seine")

#######################
# Liens et chargement #
#######################
# Utiliser les données en cache
init_google_sheets()
# liste_joueurs_complet = st.session_state.liste_joueurs_complet

# Charger les matchs archivés
archive_rows = st.session_state.sheet_archive.get_all_records()
archive_df = pd.DataFrame(archive_rows)

# Liste des joueurs et éditions
joueurs_archive = []
liste_editions = []

if not archive_df.empty:
    j1_list = archive_df["joueur_1"].unique().tolist()
    j2_list = archive_df["joueur_2"].unique().tolist()
    liste_editions = archive_df["Edition"].unique().tolist()
    joueurs_archive = list(set(j1_list + j2_list))
    liste_joueurs = joueurs_archive
else:
    liste_joueurs = liste_joueurs_complet


#############
# Fonctions #
#############

# Fonction pour retourner les scores
def parse_score(value):
    if value == "" or pd.isna(value):
        return None
    try:
        return int(value)
    except:
        return None

# Tableau complet avec mise en surbrillance du joueur sélectionné
def highlight_joueur(row):
    if row.name == joueur:
        return ['background-color: #90EE90; font-weight: bold'] * len(row)
    return [''] * len(row)

# Fonction pour colorier les victoires du tableau
def highlight_victoires(val):
    if val == "":
        return ""
    try:
        score_split = val.split("-")
        score_nous = int(score_split[0])
        score_adv = int(score_split[1])
        
        if score_nous > score_adv:
            return 'background-color: #90EE90'  # Vert pour victoire
        elif score_nous < score_adv:
            return 'background-color: #FFB6C6'  # Rouge clair pour défaite
        else:
            return ''
    except:
        return ''

# Fonction pour calculer les stats du championnat actuel
########################################################
def calculer_stats_archive():

    points_victoire = 2     #2 points pour une victoire
    points_défaite = 1      #1 point pour un défaite - récompense la participation 
    stats_archive = {j: {"Points": 0, "Victoires": 0, "Défaites": 0, "Sets_gagnés": 0, "Sets_concédés": 0, "Diff_sets": 0, "Points_gagnés": 0, "Points_concédés": 0, "Diff_points": 0, "Bulles_infligées": 0, "Bulles_concédées": 0} for j in liste_joueurs}
    
    if not archive_df.empty:
        for _, row in archive_df[archive_df["Edition"] == edition].iterrows():
            if row["statut"] == "terminé":
                vainq = row["vainqueur"]
                perdant = row["adversaire"]

                # Récupérer les scores des sets
                sets = [parse_score(row["Set_1"]), parse_score(row["Set_2"]), parse_score(row["Set_3"]), parse_score(row["Set_4"]), parse_score(row["Set_5"])]
                
                # Compter les sets remportés par le perdant (ceux avec signe négatif)
                sets_perdant = sum(1 for s in sets if s is not None and (s < 0 or s == -99))  # -99 = perdant gagne 11-0
                sets_vainqueur = 3  # Toujours 3 pour le vainqueur

                # Calculer les points totaux
                points_perdant_total = 0
                points_vainqueur_total = 0
                bulles_gagnant = 0
                bulles_perdant = 0

                for score_set in sets:
                    if score_set is None:  # Set non joué
                        continue
                    
                    if score_set == -99:
                        # Perdant gagne 11-0
                        points_perdant_total += 11
                        points_vainqueur_total += 0
                        bulles_perdant += 1
                    elif score_set < 0:
                        # Set remporté par le perdant du match (11-X)
                        points_perdant_total += 11
                        points_vainqueur_total += abs(score_set)
                    elif score_set == 0:
                        # Set remporté par le vainqueur du match (11-0)
                        points_vainqueur_total += 11
                        points_perdant_total += score_set
                        bulles_gagnant += 1
                    else: 
                        # Set remporté par le vainqueur du match (11-X)
                        points_vainqueur_total += 11
                        points_perdant_total += score_set

                if vainq in stats_archive:
                    stats_archive[vainq]["Victoires"] += 1
                    stats_archive[vainq]["Sets_gagnés"] += sets_vainqueur
                    stats_archive[vainq]["Sets_concédés"] += sets_perdant
                    stats_archive[vainq]["Points_gagnés"] += points_vainqueur_total
                    stats_archive[vainq]["Points_concédés"] += points_perdant_total
                    stats_archive[vainq]["Bulles_infligées"] += bulles_gagnant
                    stats_archive[vainq]["Bulles_concédées"] += bulles_perdant
                
                if perdant in stats_archive:
                    stats_archive[perdant]["Défaites"] += 1
                    stats_archive[perdant]["Sets_gagnés"] += sets_perdant
                    stats_archive[perdant]["Sets_concédés"] += sets_vainqueur
                    stats_archive[perdant]["Points_gagnés"] += points_perdant_total
                    stats_archive[perdant]["Points_concédés"] += points_vainqueur_total
                    stats_archive[perdant]["Bulles_infligées"] += bulles_perdant
                    stats_archive[perdant]["Bulles_concédées"] += bulles_gagnant
    
    for j in stats_archive:
        stats_archive[j]["Diff_sets"] = stats_archive[j]["Sets_gagnés"] - stats_archive[j]["Sets_concédés"]
        stats_archive[j]["Diff_points"] = stats_archive[j]["Points_gagnés"] - stats_archive[j]["Points_concédés"]
        stats_archive[j]["Points"] = (stats_archive[j]["Victoires"] * points_victoire) + (stats_archive[j]["Défaites"] * points_défaite)
    
    return stats_archive

#################
# Choix du mode #
#################

edition = st.selectbox("Edition", liste_editions)

# Onglets de l'application
tabs = st.tabs(["🎪 Rencontres", "📊 Tableau", "🏆 Classement"])
       

# ------------------------- # 
# --- Onglet Rencontres --- #
# ------------------------- #
with tabs[0]:
    st.header("Rencontres")

    # - Afficher la liste des parties non disputées - #
    parties_en_cours = archive_df[(archive_df["statut"] == "à jouer") & (archive_df["Edition"] == edition)]
    
    if not parties_en_cours.empty:
        st.subheader("⚡ Rencontres non disputées")
        st.write("")
        st.write("")

        # Trier les tours par ordre numérique
        parties_en_cours["tour_num"] = parties_en_cours["tour n°"].str.extract(r'(\d+)').astype(int)
        parties_en_cours = parties_en_cours.sort_values("tour_num")

        for tour_num, groupe in parties_en_cours.groupby("tour_num"):
            st.markdown(f"### 🏁 Tour {tour_num}")
            for _, parties in groupe.iterrows():
                st.info(f"🎯 **{parties['joueur_1']}** vs **{parties['joueur_2']}**")
    
    st.divider()

    # - Afficher la liste des parties terminés - #
    parties_termines = archive_df[(archive_df["statut"] == "terminé") & (archive_df["Edition"] == edition)]

    if not parties_termines.empty:
        st.subheader("✅ Rencontres terminés")

        # Trier les tours par ordre numérique
        parties_termines["tour_num"] = parties_termines["tour n°"].str.extract(r'(\d+)').astype(int)
        parties_termines = parties_termines.sort_values("tour_num")

        for tour_num, groupe in parties_termines.groupby("tour_num"):
            st.markdown(f"### 🏁 Tour {tour_num}")
            for _, parties in groupe.iterrows():
                vainq = parties["vainqueur"]
                adv = parties["adversaire"]
        
                # Récupérer les scores des sets
                sets = [
                    parse_score(parties["Set_1"]),
                    parse_score(parties["Set_2"]),
                    parse_score(parties["Set_3"]),
                    parse_score(parties["Set_4"]),
                    parse_score(parties["Set_5"])
                ]
        
                # Compter les sets remportés par le perdant (ceux avec signe négatif)
                sets_perdant = sum(1 for s in sets if s is not None and (s < 0 or s == -99))
                sets_vainqueur = 3  # Toujours 3 pour le vainqueur (meilleur des 5)

                st.info(f"🎯 **{vainq}** a gagné contre **{adv}** {sets_vainqueur} sets à {sets_perdant}")

# ----------------------------------------- # 
# --- Onglet Tableau des confrontations --- #
# ----------------------------------------- #
with tabs[1]:
    st.header("Tableau des confrontations")
    
    if archive_df.empty:
        st.info("Aucun résultat enregistré pour le moment")
    else:
        recap = pd.DataFrame("", index=liste_joueurs, columns=liste_joueurs)
        
        for _, row in archive_df[archive_df["Edition"] == edition].iterrows():
            if row["statut"] != "terminé":
                continue
                
            vainq = row["vainqueur"]
            adv = row["adversaire"]
            
            # Récupérer les scores des sets
            sets = [
                parse_score(row["Set_1"]),
                parse_score(row["Set_2"]),
                parse_score(row["Set_3"]),
                parse_score(row["Set_4"]),
                parse_score(row["Set_5"])
            ]
            
            # Compter les sets remportés par le perdant (ceux avec signe négatif)
            sets_perdant = sum(1 for s in sets if s is not None and (s < 0 or s == -99))
            sets_vainqueur = 3  # Toujours 3 pour le vainqueur (meilleur des 5)
            
            # Remplir la matrice
            if vainq in liste_joueurs and adv in liste_joueurs:
                recap.loc[vainq, adv] = f"{sets_perdant}-{sets_vainqueur}"
                recap.loc[adv, vainq] = f"{sets_vainqueur}-{sets_perdant}"

        recap_styled = recap.style.applymap(highlight_victoires)
        st.dataframe(recap_styled, use_container_width=True)

    st.divider()

    st.subheader("Détail des confrontations")
    st.text("")

    st.dataframe(archive_df[archive_df["Edition"] == edition], use_container_width=True)

# ------------------------- # 
# --- Onglet Classement --- #
# ------------------------- #
with tabs[2]:

    st.header("Classement du championnat")
    st.subheader("Choisissez un joueur pour afficher ses stats et le mettre en surbrillance dans le tableau")

    # Sélection d'un joueur à afficher
    joueur = st.selectbox("Choix du joueur", options=liste_joueurs, key="joueur")
    
    stats_archive = calculer_stats_archive()
    
    classement = pd.DataFrame(stats_archive).T
    classement["Parties jouées"] = classement["Victoires"] + classement["Défaites"]
    classement["%_Victoires"] = ((classement["Victoires"] / classement["Parties jouées"]) * 100).fillna(0).replace([float('inf'), -float('inf')], 0).round(0).astype(int).astype(str) + "%"
    classement = classement.sort_values(by=["Points", "Victoires", "Diff_sets", "Diff_points"], ascending=[False, False, False, False])
    classement = classement[["Points", "Parties jouées", "Victoires", "Défaites", "%_Victoires", "Sets_gagnés", "Sets_concédés", "Diff_sets", "Points_gagnés", "Points_concédés", "Diff_points", "Bulles_infligées", "Bulles_concédées"]]
    classement.columns = ["Points", "Joués", "Victoires", "Défaites", "% Vict", "Sets Gagnés", "Sets Perdus", "Diff_sets", "Points Gagnés", "Points Perdus", "Diff_points", "Bulles_infligées", "Bulles_concédées"]
        
    # Afficher sous forme de métriques plutôt qu'un tableau
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Points", classement.loc[joueur, "Points"])
    with col2:
        st.metric("% Victoires", classement.loc[joueur, "% Vict"])
    with col3:
        st.metric("Diff_sets", classement.loc[joueur, "Diff_sets"])
    with col4:
        st.metric("Diff_points", classement.loc[joueur, "Diff_points"])
    with col5:
        st.metric("Bulles_infligées", classement.loc[joueur, "Bulles_infligées"])

    st.divider()

    # Affichage du tableau complet
    classement_styled = classement.style.apply(highlight_joueur, axis=1)
    st.dataframe(classement_styled, use_container_width=True)
