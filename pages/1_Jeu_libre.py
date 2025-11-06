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

#######################
# Liens et chargement #
#######################
# Utiliser les données en cache
init_google_sheets()
liste_joueurs_complet = st.session_state.liste_joueurs_complet

# Charger les parties en jeu libre tête-à-tête
resultats_simp_rows = st.session_state.sheet_resultats_simp.get_all_records()
resultats_simp_df = pd.DataFrame(resultats_simp_rows)

# Charger les parties en jeu libre tête-à-tête
resultats_doub_rows = st.session_state.sheet_resultats_doub.get_all_records()
resultats_doub_df = pd.DataFrame(resultats_doub_rows)

#############
# Fonctions #
#############

def parse_score(value):
    if value == "" or pd.isna(value):
        return None
    try:
        return int(value)
    except:
        return None

# Fonction pour calculer les stats du jeu libre
###############################################
def calculer_stats():
    stats = {j: {"Victoires": 0, "Défaites": 0, "Sets_gagnés": 0, "Sets_concédés": 0, "Diff_sets": 0, "Points_gagnés": 0, "Points_concédés": 0, "Diff_points": 0, "Bulles_infligées": 0, "Bulles_concédées": 0} for j in liste_joueurs_complet}
    
    if not resultats_simp_df.empty:
        for _, row in resultats_simp_df.iterrows():
            vainq = row["vainqueur"]
            perdant = row["adversaire"]
            # Récupérer les scores des sets
            sets = [parse_score(row["Set_1"]), parse_score(row["Set_2"]), parse_score(row["Set_3"]), parse_score(row["Set_4"]), parse_score(row["Set_5"])]
                
            # Compter les sets remportés par le perdant (ceux avec signe négatif)
            sets_perdant = sum(1 for s in sets if s is not None and (s < 0 or s == -99))  # -99 = perdant gagne 11-0
            sets_vainqueur = 3 

            # Calculer les points totaux
            points_perdant_total = 0
            points_vainqueur_total = 0
            bulles_gagnant = 0
            bulles_perdant = 0

            for score_set in sets:
                if score_set is None: 
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

            if vainq in stats:
                stats[vainq]["Victoires"] += 1
                stats[vainq]["Sets_gagnés"] += sets_vainqueur
                stats[vainq]["Sets_concédés"] += sets_perdant
                stats[vainq]["Points_gagnés"] += points_vainqueur_total
                stats[vainq]["Points_concédés"] += points_perdant_total
                stats[vainq]["Bulles_infligées"] += bulles_gagnant
                stats[vainq]["Bulles_concédées"] += bulles_perdant
                
            if perdant in stats:
                stats[perdant]["Défaites"] += 1
                stats[perdant]["Sets_gagnés"] += sets_perdant
                stats[perdant]["Sets_concédés"] += sets_vainqueur
                stats[perdant]["Points_gagnés"] += points_perdant_total
                stats[perdant]["Points_concédés"] += points_vainqueur_total
                stats[perdant]["Bulles_infligées"] += bulles_perdant
                stats[perdant]["Bulles_concédées"] += bulles_gagnant
    
    for j in stats:
        stats[j]["Diff_sets"] = stats[j]["Sets_gagnés"] - stats[j]["Sets_concédés"]
        stats[j]["Diff_points"] = stats[j]["Points_gagnés"] - stats[j]["Points_concédés"]
    
    return stats

# Tableau complet avec mise en surbrillance du joueur sélectionné
def highlight_joueur(row):
    if row.name == joueur:
        return ['background-color: #90EE90; font-weight: bold'] * len(row)  # vert
    return [''] * len(row)

########################
# Choix du mode de jeu #
########################
st.divider()
mode = st.radio(
    "Mode de jeu",
    ["👤 Simple", "👥 Double"],
    horizontal=True
)
st.divider()

##################
# Mode Jeu libre #
##################
if mode == "👤 Simple": 
    tabs = st.tabs(["➕ Saisie résultat", "📊 Statistiques"])
    
    # --------------------- #
    # --- Onglet Saisie --- # 
    # --------------------- #
    with tabs[0]:
        # Saisie simplifiée sans lien avec le tournoi
        st.header("Saisie d'un résultat libre en simple")

        # Code de saisie adapté
        j1 = st.selectbox("Joueur 1", options=liste_joueurs_complet, key="j1")
        j2 = st.selectbox("Joueur 2", options=[j for j in liste_joueurs_complet if j != j1], key="j2")

        with st.form("saisie_resultat_open"):
            # Vainqueur dépend des joueurs choisis
            vainqueur = st.radio("Qui a gagné ?", [j1, j2])
            if vainqueur == j1:
                perdant = j2 
            else: 
                perdant = j1
            
            # Règles de gestion de la saisie des scores
            col0, col1, col2, col3, col4, col5 = st.columns(6)

            with col0:
                st.write("")
                st.write("")
                st.write(f"**{j1}**")
                st.write("")
                st.write(f"**{j2}**")
                    
            with col1: 
                st.write("**Set 1**")
                score_j1_s1 = st.number_input("", min_value=0, max_value=99, value=0, key="j1_s1", label_visibility="collapsed")
                score_j2_s1 = st.number_input("", min_value=0, max_value=99, value=0, key="j2_s1", label_visibility="collapsed")
                    
            with col2: 
                st.write("**Set 2**")
                score_j1_s2 = st.number_input("", min_value=0, max_value=99, value=0, key="j1_s2", label_visibility="collapsed")
                score_j2_s2 = st.number_input("", min_value=0, max_value=99, value=0, key="j2_s2", label_visibility="collapsed")

            with col3: 
                st.write("**Set 3**")
                score_j1_s3 = st.number_input("", min_value=0, max_value=99, value=0, key="j1_s3", label_visibility="collapsed")
                score_j2_s3 = st.number_input("", min_value=0, max_value=99, value=0, key="j2_s3", label_visibility="collapsed")

            with col4: 
                st.write("**Set 4**")
                score_j1_s4 = st.number_input("", min_value=0, max_value=99, value=0, key="j1_s4", label_visibility="collapsed")
                score_j2_s4 = st.number_input("", min_value=0, max_value=99, value=0, key="j2_s4", label_visibility="collapsed")

            with col5: 
                st.write("**Set 5**")
                score_j1_s5 = st.number_input("", min_value=0, max_value=99, value=0, key="j1_s5", label_visibility="collapsed")
                score_j2_s5 = st.number_input("", min_value=0, max_value=99, value=0, key="j2_s5", label_visibility="collapsed")

                date = pd.to_datetime('now').strftime("%Y-%m-%d %H:%M:%S")

            submitted = st.form_submit_button("✅ Enregistrer", use_container_width=True)

            if submitted:
                # Calculer les sets gagnés par chaque joueur
                sets_j1 = 0
                sets_j2 = 0

                # 1er set
                if (score_j1_s1 >= 11) and (score_j1_s1 >= score_j2_s1 + 2):
                    sets_j1 += 1
                elif (score_j2_s1 >= 11) and (score_j2_s1 >= score_j1_s1 + 2):
                    sets_j2 += 1
                else:
                    st.error("❌ Score du 1er set invalide")
                    st.stop()

                # 2eme set
                if (score_j1_s2 >= 11) and (score_j1_s2 >= score_j2_s2 + 2):
                    sets_j1 += 1
                elif (score_j2_s2 >= 11) and (score_j2_s2 >= score_j1_s2 + 2):
                    sets_j2 += 1
                else:
                    st.error("❌ Score du 2ème set invalide")
                    st.stop()
                # 3eme set
                if (score_j1_s3 >= 11) and (score_j1_s3 >= score_j2_s3 + 2):
                    sets_j1 += 1
                elif (score_j2_s3 >= 11) and (score_j2_s3 >= score_j1_s3 + 2):
                    sets_j2 += 1
                else:
                    st.error("❌ Score du 3ème set invalide")
                    st.stop()

                if sets_j1 != 3 and sets_j2 != 3:
                    # 4eme set
                    if (score_j1_s4 >= 11) and (score_j1_s4 >= score_j2_s4 + 2):
                        sets_j1 += 1
                    elif (score_j2_s4 >= 11) and (score_j2_s4 >= score_j1_s4 + 2):
                        sets_j2 += 1
                    elif sets_j1 < 3 and sets_j2 < 3:
                        st.error("❌ Score du 4ème set invalide")
                        st.stop()

                    if sets_j1 != 3 and sets_j2 != 3:
                        # 5eme set
                        if (score_j1_s5 >= 11) and (score_j1_s5 >= score_j2_s5 + 2):
                            sets_j1 += 1
                        elif (score_j2_s5 >= 11) and (score_j2_s5 >= score_j1_s5 + 2):
                            sets_j2 += 1
                        elif sets_j1 < 3 and sets_j2 < 3:
                            st.error("❌ Score du 5ème set invalide")
                            st.stop()

                score_set_1, score_set_2, score_set_3, score_set_4, score_set_5 = 0, 0, 0, "", ""

                # Déterminer le vainqueur
                if sets_j1 > sets_j2:
                    vainqueur = j1
                    perdant = j2
                    score_vainqueur = sets_j1
                    score_perdant = sets_j2

                    # 1er set
                    if score_j1_s1 > score_j2_s1:
                        score_set_1 = score_j2_s1
                    else:
                        score_set_1 = -score_j1_s1

                    # 2ème set
                    if score_j1_s2 > score_j2_s2:
                        score_set_2 = score_j2_s2
                    else:
                        score_set_2 = -score_j1_s2

                    # 3ème set
                    if score_j1_s3 > score_j2_s3:
                        score_set_3 = score_j2_s3
                    else:
                        score_set_3 = -score_j1_s3

                    if score_perdant > 0:
                        # 4ème set
                        if score_j1_s4 > score_j2_s4:
                            score_set_4 = score_j2_s4
                        else:
                            score_set_4 = -score_j1_s4

                        if score_perdant > 1:
                            # 5ème set
                            if score_j1_s5 > score_j2_s5:
                                score_set_5 = score_j2_s5
                            else:
                                st.error("❌ Impossible que le vainqueur perde le 5ème set. Vérifier les scores saisis.")
                                st.stop()

                elif sets_j2 > sets_j1:
                    vainqueur = j2
                    perdant = j1
                    score_vainqueur = sets_j2
                    score_perdant = sets_j1

                    # 1er set
                    if score_j1_s1 < score_j2_s1:
                        score_set_1 = score_j1_s1
                    else:
                        score_set_1 = -score_j2_s1

                    # 2ème set
                    if score_j1_s2 < score_j2_s2:
                        score_set_2 = score_j1_s2
                    else:
                        score_set_2 = -score_j2_s2

                    # 3ème set
                    if score_j1_s3 < score_j2_s3:
                        score_set_3 = score_j1_s3
                    else:
                        score_set_3 = -score_j2_s3

                    if score_perdant > 0:
                        # 4ème set
                        if score_j1_s4 < score_j2_s4:
                            score_set_4 = score_j1_s4
                        else:
                            score_set_4 = -score_j2_s4

                        if score_perdant > 1:
                            # 5ème set
                            if score_j1_s5 < score_j2_s5:
                                score_set_5 = score_j1_s5
                            else:
                                st.error("❌ Impossible que le vainqueur perde le 5ème set. Vérifier les scores saisis.")
                                st.stop()

                        if score_perdant > 2:
                            st.error("❌ Erreur de score_perdant. Vérifier les scores saisis.")
                            st.stop()
                else:
                    st.error("❌ Erreur : égalité de sets. Vérifier les scores saisis.")
                    st.stop()
                
                # Vérification : au moins 3 sets gagnés (meilleur des 5)
                if score_vainqueur < 3:
                    st.error("❌ Le vainqueur doit avoir gagné au moins 3 sets (meilleur des 5)")
                    st.stop()
                
                # Afficher le résumé
                st.success(f"🏆 **{vainqueur}** remporte le match {score_vainqueur}-{score_perdant}")
                
                # Construire le détail des scores
                detail_scores = f"{score_j1_s1}-{score_j2_s1}, {score_j1_s2}-{score_j2_s2}, {score_j1_s3}-{score_j2_s3}"
                if score_j1_s4 > 0 or score_j2_s4 > 0:
                    detail_scores += f", {score_j1_s4}-{score_j2_s4}"
                if score_j1_s5 > 0 or score_j2_s5 > 0:
                    detail_scores += f", {score_j1_s5}-{score_j2_s5}"
                
                st.info(f"Détail : {detail_scores}")

                # Ajouter aussi dans les résultats généraux
                perdant = j2 if vainqueur == j1 else j1
                st.session_state.sheet_resultats_simp.append_row([vainqueur, perdant, score_set_1, score_set_2, score_set_3, score_set_4, score_set_5, date])
                st.success("✅ Résultat enregistré !")
                st.rerun()

    # -------------------- #
    # --- Onglet stats --- #
    # -------------------- #
    with tabs[1]:
        # Statistiques globales tous joueurs
        st.header("Choisissez un joueur pour afficher ses stats et le mettre en surbrillance dans le tableau")
        # Classement basé sur tous les résultats
        stats = calculer_stats()

        # Sélection d'un joueur à afficher
        joueur = st.selectbox("Choix du joueur", options=liste_joueurs_complet, key="joueur")

        # Mise en forme des stats
        stats_tab = pd.DataFrame(stats).T
        
        # Calcul de stats additionnelles
        stats_tab["Parties jouées"] = stats_tab["Victoires"] + stats_tab["Défaites"]
        stats_tab["%_Victoires"] = ((stats_tab["Victoires"] / stats_tab["Parties jouées"]) * 100).fillna(0).replace([float('inf'), -float('inf')], 0).round(0).astype(int).astype(str) + "%"
        stats_tab = stats_tab.sort_values(by=["Victoires", "Diff_sets", "Diff_points"], ascending=[False, False, False])
        stats_tab = stats_tab[["Parties jouées", "Victoires", "Défaites", "%_Victoires", "Sets_gagnés", "Sets_concédés", "Diff_sets", "Points_gagnés", "Points_concédés", "Diff_points", "Bulles_infligées", "Bulles_concédées"]]
        stats_tab.columns = ["Joués", "Victoires", "Défaites", "% Vict", "Sets Gagnés", "Sets Perdus", "Diff_sets", "Points Gagnés", "Points Perdus", "Diff_points", "Bulles_infligées", "Bulles_concédées"]

        # Afficher sous forme de métriques plutôt qu'un tableau
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Parties jouées", stats_tab.loc[joueur, "Joués"])
        with col2:
            st.metric("Victoires", stats_tab.loc[joueur, "Victoires"])
        with col3:
            st.metric("Défaites", stats_tab.loc[joueur, "Défaites"])
        with col4:
            st.metric("Différence sets", stats_tab.loc[joueur, "Diff_sets"])
        with col5:
            st.metric("Différence points", stats_tab.loc[joueur, "Diff_points"])

        st.divider()

        # Affichage du tableau complet
        stats_tab_styled = stats_tab.style.apply(highlight_joueur, axis=1)
        st.dataframe(stats_tab_styled, use_container_width=True)

else: 
    tabs = st.tabs(["➕ Saisie résultat", "📊 Statistiques"])
    st.image("images/WIP2.jpg", use_container_width=True) 
    st.header("Je finis de peaufiner la partie simple et je ferai ensuite les doubles 😉")

    # --------------------- #
    # --- Onglet Saisie --- # 
    # --------------------- #