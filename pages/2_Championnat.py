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
st.set_page_config(page_title="Championnat du Lundi", page_icon="🏆")
#st.image("images/img_tournoi.png", use_container_width=True) # A modifier ##############################
st.write("# Championnat interne du club de tennis de table de Vaux-sur-Seine")

#######################
# Liens et chargement #
#######################
# Utiliser les données en cache
init_google_sheets()
liste_joueurs_complet = st.session_state.liste_joueurs_complet

# Charger les matchs du championnat tête-à-tête
championnat_rows = st.session_state.sheet_championnat.get_all_records()
championnat_df = pd.DataFrame(championnat_rows)

joueurs_championnat = []
if not championnat_df.empty:
    j1_list = championnat_df["joueur_1"].unique().tolist()
    j2_list = championnat_df["joueur_2"].unique().tolist()
    joueurs_championnat = list(set(j1_list + j2_list))
    liste_joueurs = joueurs_championnat
else:
    liste_joueurs = liste_joueurs_complet

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

# Fonction pour calculer les stats du championnat actuel
########################################################
def calculer_stats_championnat():

    points_victoire = 2     #2 points pour une victoire
    points_défaite = 1      #1 point pour un défaite - récompense la participation 
    stats_championnat = {j: {"Points": 0, "Victoires": 0, "Défaites": 0, "Sets_gagnés": 0, "Sets_concédés": 0, "Diff_sets": 0, "Points_gagnés": 0, "Points_concédés": 0, "Diff_points": 0, "Bulles_infligées": 0, "Bulles_concédées": 0} for j in liste_joueurs}
    
    if not championnat_df.empty:
        for _, row in championnat_df.iterrows():
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

                if vainq in stats_championnat:
                    stats_championnat[vainq]["Victoires"] += 1
                    stats_championnat[vainq]["Sets_gagnés"] += sets_vainqueur
                    stats_championnat[vainq]["Sets_concédés"] += sets_perdant
                    stats_championnat[vainq]["Points_gagnés"] += points_vainqueur_total
                    stats_championnat[vainq]["Points_concédés"] += points_perdant_total
                    stats_championnat[vainq]["Bulles_infligées"] += bulles_gagnant
                    stats_championnat[vainq]["Bulles_concédées"] += bulles_perdant
                
                if perdant in stats_championnat:
                    stats_championnat[perdant]["Défaites"] += 1
                    stats_championnat[perdant]["Sets_gagnés"] += sets_perdant
                    stats_championnat[perdant]["Sets_concédés"] += sets_vainqueur
                    stats_championnat[perdant]["Points_gagnés"] += points_perdant_total
                    stats_championnat[perdant]["Points_concédés"] += points_vainqueur_total
                    stats_championnat[perdant]["Bulles_infligées"] += bulles_perdant
                    stats_championnat[perdant]["Bulles_concédées"] += bulles_gagnant
    
    for j in stats_championnat:
        stats_championnat[j]["Diff_sets"] = stats_championnat[j]["Sets_gagnés"] - stats_championnat[j]["Sets_concédés"]
        stats_championnat[j]["Diff_points"] = stats_championnat[j]["Points_gagnés"] - stats_championnat[j]["Points_concédés"]
        stats_championnat[j]["Points"] = (stats_championnat[j]["Victoires"] * points_victoire) + (stats_championnat[j]["Défaites"] * points_défaite)
    
    return stats_championnat

# Fonction pour générer les appariements complet du championnat
###############################################################
def generer_appariements_aleatoires(joueurs, seed=None):
    """
    Retourne une liste de rounds; chaque round est une liste de paires (j1, j2).
    Pour n impair, on ajoute 'BYE' (match contre BYE = repos).
    """
    if seed is not None:
        random.seed(seed)
    joueurs = list(joueurs)
    random.shuffle(joueurs)  # randomiser l'ordre initial
    n = len(joueurs)
    bye = None
    if n % 2 == 1:
        bye = "BYE"
        joueurs.append(bye)
        n += 1

    rounds = []
    # méthode du cercle : on fixe joueurs[0], on fait tourner le reste
    for r in range(n - 1):
        paires = []
        for i in range(n // 2):
            a = joueurs[i]
            b = joueurs[n - 1 - i]
            if a != bye and b != bye:
                paires.append((a, b, f"Tour {r+1}", "à jouer"))
        rounds.append(paires)
        # rotation (fixer joueurs[0])
        joueurs = [joueurs[0]] + [joueurs[-1]] + joueurs[1:-1]
    return rounds

# Tableau complet avec mise en surbrillance du joueur sélectionné
def highlight_joueur(row):
    if row.name == joueur:
        return ['background-color: #90EE90; font-weight: bold'] * len(row)  # vert
    return [''] * len(row)

########################
# Choix du mode de jeu #
########################

# Onglets de l'application
tabs = st.tabs(["👥 Participants", "🎪 Championnat", "➕ Saisie résultat", "📊 Confrontations", "🏆 Classement"])

# --------------------------- # 
# --- Onglet Participants --- #
# --------------------------- #
with tabs[0]:
    st.header("👥 Sélection des participants")
    
    if not championnat_df.empty:
        st.info(f"✅ Le championnat est déjà lancé avec {len(joueurs_championnat)} participants")
        st.write("**Participants :**")
        for j in sorted(joueurs_championnat):
            st.write(f"• {j}")
        
        st.divider()

        st.warning("⚠️ Pour modifier les participants, il faut réinitialiser le championnat (Contacter Stef-la-pétanque)")
    
    else:
        st.write("Sélectionner les joueurs qui participeront au championnat :")
        
        # Initialiser la sélection dans session_state
        if 'joueurs_selectionnes' not in st.session_state:
            st.session_state.joueurs_selectionnes = liste_joueurs_complet.copy()
        
        # Créer des checkboxes pour chaque joueur
        col1, col2 = st.columns(2)
        mid = len(liste_joueurs_complet) // 2
        
        with col1:
            for j in liste_joueurs_complet[:mid]:
                checked = st.checkbox(j, value=j in st.session_state.joueurs_selectionnes, key=f"cb_{j}")
                if checked and j not in st.session_state.joueurs_selectionnes:
                    st.session_state.joueurs_selectionnes.append(j)
                elif not checked and j in st.session_state.joueurs_selectionnes:
                    st.session_state.joueurs_selectionnes.remove(j)
        
        with col2:
            for j in liste_joueurs_complet[mid:]:
                checked = st.checkbox(j, value=j in st.session_state.joueurs_selectionnes, key=f"cb_{j}")
                if checked and j not in st.session_state.joueurs_selectionnes:
                    st.session_state.joueurs_selectionnes.append(j)
                elif not checked and j in st.session_state.joueurs_selectionnes:
                    st.session_state.joueurs_selectionnes.remove(j)
        
        st.divider()
        
        joueurs_selectionnes = st.session_state.joueurs_selectionnes
        
        if len(joueurs_selectionnes) < 2:
            st.error("⚠️ Sélectionne au moins 2 joueurs pour lancer le tournoi")
        else:
            st.success(f"✅ {len(joueurs_selectionnes)} joueurs sélectionnés")
            nb_parties_tour = round(len(joueurs_selectionnes) // 2)
            nb_parties_total = len(joueurs_selectionnes) * (len(joueurs_selectionnes) - 1) // 2
            st.info(f"📊 Ce tournoi nécessitera **{nb_parties_total} parties** au total ({len(joueurs_selectionnes) - 1} par joueur)")
            
            st.divider()
            
            if st.button("🎲 Création du championnat", use_container_width=True, key="btn_aleatoire"):
                nouveaux_matchs = generer_appariements_aleatoires(joueurs_selectionnes, seed=42)
                for match in nouveaux_matchs:
                    st.session_state.sheet_championnat.append_rows(match)
                    
                # Recharger les données du championnat
                st.session_state.championnat_df = pd.DataFrame(championnat_rows)
                    
                st.success(f"✅ {len(nouveaux_matchs)} matchs générés !")
                st.rerun()

# -------------------------- # 
# --- Onglet championnat --- #
# -------------------------- # 
with tabs[1]:
    st.header("🎪 Gestion du championnat")
    
    if championnat_df.empty:
        st.warning("⚠️ Voir dans l'onglet **👥 Participants** pour lancer le championnat")
    
    else:
        # Calculs nécéssaires
        nb_total = len(joueurs_championnat) * (len(joueurs_championnat) - 1) // 2
        nb_parties_tour = round(len(liste_joueurs) // 2)
        nb_joues = len(championnat_df[championnat_df["statut"] == "terminé"]) if not championnat_df.empty else 0
        nb_en_cours = len(championnat_df[championnat_df["statut"] == "à jouer"]) if not championnat_df.empty else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Parties terminées", f"{nb_joues}/{nb_total}")
        with col2:
            st.metric("En cours", nb_en_cours)
        with col3:
            progression = (nb_joues / nb_total * 100) if nb_total > 0 else 0
            st.metric("Progression", f"{progression:.0f}%")
        
        st.progress(progression / 100)
        
        st.divider()
        
        # - Afficher la liste des parties en cours - #
        parties_en_cours = championnat_df[championnat_df["statut"] == "à jouer"]
        
        if not parties_en_cours.empty:
            st.subheader("⚡ Parties à jouer")
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
        parties_termines = championnat_df[championnat_df["statut"] == "terminé"]

        if not parties_termines.empty:
            st.subheader("✅ Parties terminés")

            # Trier les tours par ordre numérique
            parties_termines["tour_num"] = parties_termines["tour n°"].str.extract(r'(\d+)').astype(int)
            parties_termines = parties_termines.sort_values("tour_num")

            for tour_num, groupe in parties_termines.groupby("tour_num"):
                st.markdown(f"### 🏁 Tour {tour_num}")
                for _, parties in groupe.iterrows():
                    st.info(f"🎯 **{parties['joueur_1']}** vs **{parties['joueur_2']}**")

        st.divider()
        
        # Historique complet
        with st.expander("📋 Voir tous les matchs du championnat"):
            st.dataframe(championnat_df, use_container_width=True)

# --------------------- #
# --- Onglet Saisie --- #
# --------------------- #
with tabs[2]:
    st.header("Saisie d'un résultat de championnat")
    
    # Récupérer les matchs à jouer
    matchs_disponibles = []
    if not championnat_df.empty:
        matchs_a_jouer = championnat_df[championnat_df["statut"] == "à jouer"]
        for _, match in matchs_a_jouer.iterrows():
            matchs_disponibles.append(f"{match['joueur_1']} vs {match['joueur_2']}")
    
    if not matchs_disponibles:
        st.warning("⚠️ Aucun match en attente. Va dans l'onglet 🎪 Championnat pour en générer !")
    else:
        match_selectionne = st.selectbox("Sélectionne le match", matchs_disponibles)
        
        if match_selectionne:
            j1, j2 = match_selectionne.replace(" vs ", "|").split("|")
            
            st.divider()

            vainqueur = st.radio("Qui a gagné ?", [j1, j2])
            if vainqueur == j1:
                perdant = j2 
            else: 
                perdant = j1
            
            with st.form("saisie_resultat_championnat"):
                
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
                
                submitted = st.form_submit_button("✅ Enregistrer le résultat du match", use_container_width=True)
            
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
            
            if submitted:
                # Trouver la ligne du match dans le sheet
                all_data = st.session_state.sheet_championnat.get_all_values()
                row_idx = None
                
                for i, row in enumerate(all_data[1:], start=2):
                    if (row[0] == j1 and row[1] == j2) or (row[0] == j2 and row[1] == j1):
                        if row[3] == "à jouer": 
                            row_idx = i
                            break
                
                if row_idx:
                    # Mettre à jour le championnat
                    st.session_state.sheet_championnat.update(f"D{row_idx}:L{row_idx}", [["terminé", vainqueur, perdant, score_set_1, score_set_2, score_set_3, score_set_4, score_set_5, date]])
                    
                    # Recharger les données du championnat
                    championnat_tat_rows = st.session_state.sheet_championnat.get_all_records()
                    st.session_state.championnat_df = pd.DataFrame(championnat_tat_rows)
                    
                    st.success("✅ Résultat enregistré !")
                    st.rerun()
                else:
                    st.error("❌ Erreur : impossible de trouver le match")

# ----------------------------- #
# --- Onglet Confrontations --- #
# ----------------------------- #
with tabs[3]:
    st.header("Tableau des confrontations")
    
    if championnat_df.empty:
        st.info("Aucun résultat enregistré pour le moment")
    else:
        recap = pd.DataFrame("", index=liste_joueurs, columns=liste_joueurs)
        
        for _, row in championnat_df.iterrows():
            vainq = row["vainqueur"]
            adv = row["adversaire"]
            score_v = row.get("score_vainqueur", 1)
            score_a = row.get("score_adversaire", row.get("score_adv", 0))
            
            if vainq in liste_joueurs and adv in liste_joueurs:
                recap.loc[vainq, adv] = f"{score_v}-{score_a}"
                recap.loc[adv, vainq] = f"{score_a}-{score_v}"
        
        st.dataframe(recap, use_container_width=True)

    st.divider()

    st.subheader("Liste des confrontations")
    st.text("")

    st.dataframe(championnat_df, use_container_width=True)

# ------------------------- #
# --- Onglet Classement --- #
# ------------------------- #
with tabs[4]:
    st.header("Classement du championnat")

    st.subheader("Choisissez un joueur pour afficher ses stats et le mettre en surbrillance dans le tableau")
    # Sélection d'un joueur à afficher
    joueur = st.selectbox("Choix du joueur", options=liste_joueurs, key="joueur")
    
    stats_championnat = calculer_stats_championnat()
    
    if all(s["Victoires"] == 0 and s["Défaites"] == 0 for s in stats_championnat.values()):
        st.info("Aucune partie terminée pour le moment")
    else:
        classement = pd.DataFrame(stats_championnat).T
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
