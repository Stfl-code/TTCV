import streamlit as st
import gspread
import pandas as pd
import random
import string
import math
import itertools
import sys
sys.path.append('..')  # Pour importer depuis la racine
from utils import init_google_sheets

#############
# Affichage #
#############
st.set_page_config(page_title="tournoi", page_icon="🏓")
st.image("images/img_tournoi.png", use_container_width=True)
st.write("# tournoi interne du club de tennis de table de Vaux-sur-Seine")

#######################
# Liens et chargement #
#######################
# Utiliser les données en cache
init_google_sheets()
liste_joueurs_complet = st.session_state.liste_joueurs_complet

# Charger les matchs du championnat tête-à-tête
tournoi_rows = st.session_state.sheet_tournoi.get_all_records()
tournoi_df = pd.DataFrame(tournoi_rows)

joueurs_tournoi = []
if not tournoi_df.empty:
    j1_list = tournoi_df["joueur_1"].unique().tolist()
    j2_list = tournoi_df["joueur_2"].unique().tolist()
    joueurs_tournoi = list(set(j1_list + j2_list))
    liste_joueurs = joueurs_tournoi
else:
    liste_joueurs = liste_joueurs_complet

# Initialiser l'onglet actif dans session_state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0  # Index de l'onglet par défaut

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

def afficher_bracket_phase_finale():
    """Affiche le bracket de la phase finale de manière visuelle"""
    
    # Filtrer les matchs de la phase finale
    matchs_finale = tournoi_df[
        (tournoi_df['phase'].str.contains('Finale', na=False)) & 
        (~tournoi_df['phase'].str.contains('Consolante', na=False))
    ]
    
    matchs_consolante = tournoi_df[tournoi_df['phase'].str.contains('Consolante', na=False)]
    
    if matchs_finale.empty and matchs_consolante.empty:
        st.info("ℹ️ La phase finale n'a pas encore été lancée")
        return
    
    # ===========================
    # BRACKET PHASE FINALE
    # ===========================
    if not matchs_finale.empty:
        st.subheader("🏆 Bracket - Phase Finale")
        
        # Organiser par étape
        etapes_ordre = {
            "1/16ème de finale": 1,
            "1/8ème de finale": 2,
            "Quart de finale": 3,
            "Demi-finale": 4,
            "Finale": 5
        }
        
        # Extraire les étapes présentes
        etapes_presentes = {}
        for _, match in matchs_finale.iterrows():
            phase = match['phase']
            etape = phase.replace('Finale_', '')
            
            if etape not in etapes_presentes:
                etapes_presentes[etape] = []
            etapes_presentes[etape].append(match)
        
        # Trier les étapes
        etapes_triees = sorted(
            etapes_presentes.items(),
            key=lambda x: etapes_ordre.get(x[0], 0)
        )
        
        # Afficher le bracket
        nb_etapes = len(etapes_triees)
        cols = st.columns(nb_etapes)
        
        for idx, (etape, matchs) in enumerate(etapes_triees):
            with cols[idx]:
                st.markdown(f"**{etape}**")
                st.markdown("---")
                
                for match in matchs:
                    j1 = match['joueur_1']
                    j2 = match['joueur_2']
                    statut = match['statut']
                    
                    # Créer un container pour le match
                    with st.container():
                        if statut == 'terminé':
                            vainqueur = match['vainqueur']
                            
                            # Récupérer le score
                            sets = [
                                parse_score(match["Set_1"]),
                                parse_score(match["Set_2"]),
                                parse_score(match["Set_3"]),
                                parse_score(match["Set_4"]),
                                parse_score(match["Set_5"])
                            ]
                            
                            sets_perdant = sum(1 for s in sets if s is not None and (s < 0 or s == -99))
                            sets_vainqueur = 3
                            
                            # Afficher avec le vainqueur en gras
                            if vainqueur == j1:
                                st.markdown(f"**✅ {j1}** `{sets_vainqueur}`")
                                st.markdown(f"{j2} `{sets_perdant}`")
                            else:
                                st.markdown(f"{j1} `{sets_perdant}`")
                                st.markdown(f"**✅ {j2}** `{sets_vainqueur}`")
                        else:
                            # Match à jouer
                            st.markdown(f"🔵 {j1}")
                            st.markdown(f"🔵 {j2}")
                        
                        st.markdown("")  # Espacement
        
        st.divider()
    
    # ===========================
    # BRACKET CONSOLANTE
    # ===========================
    if not matchs_consolante.empty:
        st.subheader("🎯 Bracket - Consolante")
        
        # Même logique pour la consolante
        etapes_presentes_consolante = {}
        for _, match in matchs_consolante.iterrows():
            phase = match['phase']
            etape = phase.replace('Consolante_', '')
            
            if etape not in etapes_presentes_consolante:
                etapes_presentes_consolante[etape] = []
            etapes_presentes_consolante[etape].append(match)
        
        etapes_triees_consolante = sorted(
            etapes_presentes_consolante.items(),
            key=lambda x: etapes_ordre.get(x[0], 0)
        )
        
        nb_etapes_consolante = len(etapes_triees_consolante)
        cols_consolante = st.columns(nb_etapes_consolante)
        
        for idx, (etape, matchs) in enumerate(etapes_triees_consolante):
            with cols_consolante[idx]:
                st.markdown(f"**{etape}**")
                st.markdown("---")
                
                for match in matchs:
                    j1 = match['joueur_1']
                    j2 = match['joueur_2']
                    statut = match['statut']
                    
                    with st.container():
                        if statut == 'terminé':
                            vainqueur = match['vainqueur']
                            
                            sets = [
                                parse_score(match["Set_1"]),
                                parse_score(match["Set_2"]),
                                parse_score(match["Set_3"]),
                                parse_score(match["Set_4"]),
                                parse_score(match["Set_5"])
                            ]
                            
                            sets_perdant = sum(1 for s in sets if s is not None and (s < 0 or s == -99))
                            sets_vainqueur = 3
                            
                            if vainqueur == j1:
                                st.markdown(f"**✅ {j1}** `{sets_vainqueur}`")
                                st.markdown(f"{j2} `{sets_perdant}`")
                            else:
                                st.markdown(f"{j1} `{sets_perdant}`")
                                st.markdown(f"**✅ {j2}** `{sets_vainqueur}`")
                        else:
                            st.markdown(f"🟡 {j1}")
                            st.markdown(f"🟡 {j2}")
                        
                        st.markdown("")

def generer_appariements_round_robin(joueurs):
    """
    Génère les appariements round-robin avec l'algorithme des tours
    Pour paralléliser : tous les matchs d'un tour peuvent être joués simultanément
    """
    n = len(joueurs)
    if n < 2:
        return []
    
    # Si nombre impair, ajouter un "bye" fictif
    if n % 2 != 0:
        joueurs = joueurs + [None]
        n += 1
    
    matchs_par_tour = []
    joueurs_rotation = joueurs[1:]  # Joueurs qui tournent
    joueur_fixe = joueurs[0]  # Premier joueur reste fixe
    
    # Générer n-1 tours
    for tour in range(n - 1):
        matchs_tour = []
        
        # Match avec le joueur fixe
        adversaire = joueurs_rotation[0]
        if adversaire is not None:  # Pas de match si adversaire = bye
            matchs_tour.append([joueur_fixe, adversaire])
        
        # Matchs entre les autres joueurs (face à face)
        for i in range(1, n // 2):
            j1 = joueurs_rotation[i]
            j2 = joueurs_rotation[n - 1 - i]
            if j1 is not None and j2 is not None:
                matchs_tour.append([j1, j2])
        
        matchs_par_tour.append(matchs_tour)
        
        # Rotation : dernier élément passe en premier
        joueurs_rotation = [joueurs_rotation[-1]] + joueurs_rotation[:-1]
    
    return matchs_par_tour

def generer_phase_poules(joueurs_selectionnes, nb_poules, tournoi_sheet):
    """
    Génère les matchs de la phase de poules en format round-robin
    """
    # Mélanger les joueurs aléatoirement
    joueurs_melange = joueurs_selectionnes.copy()
    random.shuffle(joueurs_melange)
    
    # Répartir dans les poules
    poules = {}
    lettres_poules = string.ascii_uppercase[:nb_poules]  # A, B, C, D...
    
    joueurs_par_poule = len(joueurs_melange) // nb_poules
    reste = len(joueurs_melange) % nb_poules
    
    idx = 0
    for i, lettre in enumerate(lettres_poules):
        # Les premières poules ont un joueur de plus si répartition inégale
        taille_poule = joueurs_par_poule + (1 if i < reste else 0)
        poules[lettre] = joueurs_melange[idx:idx + taille_poule]
        idx += taille_poule
    
    # Générer les matchs pour chaque poule avec algorithme round-robin
    appariements_par_poule = {}
    for lettre, joueurs_poule in poules.items():
        appariements_par_poule[lettre] = generer_appariements_round_robin(joueurs_poule)
    
    # Déterminer le nombre maximum de tours (certaines poules peuvent avoir plus de tours)
    nb_tours_max = max(len(tours) for tours in appariements_par_poule.values())
    
    # Organiser les matchs en parallélisant : Tour 1 de toutes les poules, puis Tour 2, etc.
    tous_matchs = []
    
    for num_tour in range(nb_tours_max):
        for lettre in lettres_poules:
            tours_poule = appariements_par_poule[lettre]
            
            # Vérifier que cette poule a un tour à ce niveau
            if num_tour < len(tours_poule):
                matchs_tour = tours_poule[num_tour]
                
                for j1, j2 in matchs_tour:
                    match = [
                        j1,
                        j2,
                        f"Poule_{lettre}",  # Phase
                        f"Tour_{num_tour + 1}",  # Tour
                        "à jouer"  # Statut
                    ]
                    tous_matchs.append(match)
    
    # Écrire dans le spreadsheet
    for match in tous_matchs:
        tournoi_sheet.append_row(match)
    
    # Sauvegarder la composition des poules dans session_state
    st.session_state.composition_poules = poules
    st.session_state.nb_tours_poules = nb_tours_max
    
    return len(tous_matchs), poules, nb_tours_max

# Calculer les stats pour chaque poule
def calculer_classement_poule(lettre_poule, joueurs_poule):
    """Calcule le classement d'une poule"""
    # Filtrer les matchs de cette poule qui sont terminés
    matchs_poule = tournoi_df[
        (tournoi_df['phase'] == f'Poule_{lettre_poule}') & 
        (tournoi_df['statut'] == 'terminé')
    ]
    
    # Initialiser les stats
    stats = {j: {
        "Victoires": 0,
        "Défaites": 0,
        "Sets_gagnes": 0,
        "Sets_perdus": 0,
        "Points_marques": 0,
        "Points_encaisses": 0,
        "Diff_sets": 0,
        "Diff_points": 0,
        "Points": 0  # Système de points : 2 pts victoire, 1 pt défaite
    } for j in joueurs_poule}
    
    for _, row in matchs_poule.iterrows():
        vainq = row["vainqueur"]
        perdant = row["adversaire"]
        
        # Récupérer les scores des sets
        sets = [
            parse_score(row["Set_1"]),
            parse_score(row["Set_2"]),
            parse_score(row["Set_3"]),
            parse_score(row["Set_4"]),
            parse_score(row["Set_5"])
        ]
        
        # Compter les sets
        sets_perdant = sum(1 for s in sets if s is not None and (s < 0 or s == -99))
        sets_vainqueur = 3  # Toujours 3 dans un meilleur des 5
        
        # Calculer les points
        points_perdant_total = 0
        points_vainqueur_total = 0
        
        for score_set in sets:
            if score_set is None:
                continue
            
            if score_set == -99:
                points_perdant_total += 11
                points_vainqueur_total += 0
            elif score_set < 0:
                points_perdant_total += 11
                points_vainqueur_total += abs(score_set)
            elif score_set == 0:
                points_vainqueur_total += 11
                points_perdant_total += 0
            else:
                points_vainqueur_total += 11
                points_perdant_total += score_set
        
        # Mettre à jour les stats
        if vainq in stats:
            stats[vainq]["Victoires"] += 1
            stats[vainq]["Sets_gagnes"] += sets_vainqueur
            stats[vainq]["Sets_perdus"] += sets_perdant
            stats[vainq]["Points_marques"] += points_vainqueur_total
            stats[vainq]["Points_encaisses"] += points_perdant_total
            stats[vainq]["Points"] += 2  # 2 points pour une victoire
        
        if perdant in stats:
            stats[perdant]["Défaites"] += 1
            stats[perdant]["Sets_gagnes"] += sets_perdant
            stats[perdant]["Sets_perdus"] += sets_vainqueur
            stats[perdant]["Points_marques"] += points_perdant_total
            stats[perdant]["Points_encaisses"] += points_vainqueur_total
            stats[perdant]["Points"] += 1  # 1 point pour une défaite
    
    # Calculer les différences
    for j in stats:
        stats[j]["Diff_sets"] = stats[j]["Sets_gagnes"] - stats[j]["Sets_perdus"]
        stats[j]["Diff_points"] = stats[j]["Points_marques"] - stats[j]["Points_encaisses"]
    
    # Convertir en DataFrame et trier
    df_classement = pd.DataFrame(stats).T
    
    # Tri : Points > Diff_sets > Diff_points
    df_classement = df_classement.sort_values(
        by=["Points", "Diff_sets", "Diff_points"],
        ascending=[False, False, False]
    )
    
    # Ajouter le rang
    df_classement.insert(0, "Rang", range(1, len(df_classement) + 1))
    
    return df_classement

def verifier_poules_terminees():
    """Vérifie si tous les matchs de poules sont terminés"""
    matchs_poules = tournoi_df[tournoi_df['phase'].str.contains('Poule', na=False)]
    if matchs_poules.empty:
        return False, 0, 0
    
    total = len(matchs_poules)
    termines = len(matchs_poules[matchs_poules['statut'] == 'terminé'])
    
    return termines == total, termines, total


def obtenir_classements_poules():
    """Retourne les classements de toutes les poules"""
    poules = st.session_state.composition_poules
    classements = {}
    
    for lettre, joueurs_poule in poules.items():
        # Filtrer les matchs de cette poule qui sont terminés
        matchs_poule = tournoi_df[
            (tournoi_df['phase'] == f'Poule_{lettre}') & 
            (tournoi_df['statut'] == 'terminé')
        ]
        
        # Initialiser les stats
        stats = {j: {
            "Victoires": 0,
            "Défaites": 0,
            "Sets_gagnes": 0,
            "Sets_perdus": 0,
            "Points_marques": 0,
            "Points_encaisses": 0,
            "Diff_sets": 0,
            "Diff_points": 0,
            "Points": 0
        } for j in joueurs_poule}
        
        for _, row in matchs_poule.iterrows():
            vainq = row["vainqueur"]
            perdant = row["adversaire"]
            
            # Récupérer les scores des sets
            sets = [
                parse_score(row["Set_1"]),
                parse_score(row["Set_2"]),
                parse_score(row["Set_3"]),
                parse_score(row["Set_4"]),
                parse_score(row["Set_5"])
            ]
            
            # Compter les sets
            sets_perdant = sum(1 for s in sets if s is not None and (s < 0 or s == -99))
            sets_vainqueur = 3
            
            # Calculer les points
            points_perdant_total = 0
            points_vainqueur_total = 0
            
            for score_set in sets:
                if score_set is None:
                    continue
                
                if score_set == -99:
                    points_perdant_total += 11
                    points_vainqueur_total += 0
                elif score_set < 0:
                    points_perdant_total += 11
                    points_vainqueur_total += abs(score_set)
                elif score_set == 0:
                    points_vainqueur_total += 11
                    points_perdant_total += 0
                else:
                    points_vainqueur_total += 11
                    points_perdant_total += score_set
            
            # Mettre à jour les stats
            if vainq in stats:
                stats[vainq]["Victoires"] += 1
                stats[vainq]["Sets_gagnes"] += sets_vainqueur
                stats[vainq]["Sets_perdus"] += sets_perdant
                stats[vainq]["Points_marques"] += points_vainqueur_total
                stats[vainq]["Points_encaisses"] += points_perdant_total
                stats[vainq]["Points"] += 2
            
            if perdant in stats:
                stats[perdant]["Défaites"] += 1
                stats[perdant]["Sets_gagnes"] += sets_perdant
                stats[perdant]["Sets_perdus"] += sets_vainqueur
                stats[perdant]["Points_marques"] += points_perdant_total
                stats[perdant]["Points_encaisses"] += points_vainqueur_total
                stats[perdant]["Points"] += 1
        
        # Calculer les différences
        for j in stats:
            stats[j]["Diff_sets"] = stats[j]["Sets_gagnes"] - stats[j]["Sets_perdus"]
            stats[j]["Diff_points"] = stats[j]["Points_marques"] - stats[j]["Points_encaisses"]
        
        # Convertir en liste triée
        classement_liste = sorted(
            stats.items(),
            key=lambda x: (x[1]["Points"], x[1]["Diff_sets"], x[1]["Diff_points"]),
            reverse=True
        )
        
        # Extraire juste les noms des joueurs dans l'ordre
        classements[lettre] = [joueur for joueur, _ in classement_liste]
    
    return classements


def generer_bracket_phase_finale(qualifies, phase_depart, type_bracket="Finale"):
    """
    Génère les matchs de la phase finale en bracket
    qualifies : liste ordonnée des joueurs qualifiés
    phase_depart : "Quart de finale", "Demi-finale", etc.
    type_bracket : "Finale" ou "Consolante"
    """
    nb_joueurs = len(qualifies)
    
    # Vérifier que c'est une puissance de 2
    if nb_joueurs & (nb_joueurs - 1) != 0:
        st.error(f"❌ Erreur : {nb_joueurs} joueurs n'est pas une puissance de 2")
        return []
    
    matchs = []
    
    # Mapping des étapes
    etapes_map = {
        2: "Finale",
        4: "Demi-finale",
        8: "Quart de finale",
        16: "1/8ème de finale",
        32: "1/16ème de finale"
    }
    
    etape_actuelle = etapes_map.get(nb_joueurs, f"Tour_{int(math.log2(nb_joueurs))}")
    
    # Appariements classiques : 1 vs dernier, 2 vs avant-dernier, etc.
    for i in range(nb_joueurs // 2):
        j1 = qualifies[i]
        j2 = qualifies[nb_joueurs - 1 - i]
        
        match = [
            j1,
            j2,
            f"{type_bracket}_{etape_actuelle}",
            f"Match_{i + 1}",
            "à jouer"
        ]
        matchs.append(match)
    
    return matchs


def lancer_phase_finale():
    """Lance la phase finale du tournoi"""
    params = st.session_state.tournoi_params
    
    # Obtenir les classements de toutes les poules
    classements = obtenir_classements_poules()
    
    # Déterminer le nombre de qualifiés par poule
    nb_joueurs_phase_finale_map = {
        "Demi-finale": 4,
        "Quart de finale": 8,
        "1/8ème de finale": 16,
        "1/16ème de finale": 32
    }
    
    cutoff = params["cutoff_phase_finale"]
    nb_total_qualifies = nb_joueurs_phase_finale_map[cutoff]
    nb_poules = params["nb_poules"]
    nb_qualifies_par_poule = nb_total_qualifies // nb_poules
    
    # Extraire les qualifiés pour la phase finale
    qualifies_finale = []
    
    # Ordre d'extraction : 1er de chaque poule, puis 2ème de chaque poule, etc.
    for rang in range(nb_qualifies_par_poule):
        for lettre in sorted(classements.keys()):
            if rang < len(classements[lettre]):
                qualifies_finale.append(classements[lettre][rang])
    
    # Générer les matchs de la phase finale
    matchs_finale = generer_bracket_phase_finale(
        qualifies_finale,
        cutoff,
        "Finale"
    )
    
    # Écrire dans le spreadsheet
    for match in matchs_finale:
        st.session_state.sheet_tournoi.append_row(match)
    
    nb_matchs_finale = len(matchs_finale)
    
    # Gérer la consolante si activée
    nb_matchs_consolante = 0
    if params.get("consolante"):
        cutoff_consolante = params.get("cutoff_consolante")
        nb_total_consolante = nb_joueurs_phase_finale_map[cutoff_consolante]
        nb_consolante_par_poule = nb_total_consolante // nb_poules
        
        # Extraire les joueurs pour la consolante (rangs suivants)
        qualifies_consolante = []
        
        for rang in range(nb_qualifies_par_poule, nb_qualifies_par_poule + nb_consolante_par_poule):
            for lettre in sorted(classements.keys()):
                if rang < len(classements[lettre]):
                    qualifies_consolante.append(classements[lettre][rang])
        
        # Générer les matchs de la consolante
        matchs_consolante = generer_bracket_phase_finale(
            qualifies_consolante,
            cutoff_consolante,
            "Consolante"
        )
        
        # Écrire dans le spreadsheet
        for match in matchs_consolante:
            st.session_state.sheet_tournoi.append_row(match)
        
        nb_matchs_consolante = len(matchs_consolante)
    
    # Sauvegarder que la phase finale est lancée
    st.session_state.phase_finale_lancee = True
    
    return nb_matchs_finale, nb_matchs_consolante, qualifies_finale

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

###########
# Tournoi #
###########
# Onglets de l'application
tabs = st.tabs(["👥 Participants", "⚙️ Paramètres", "➕ Saisie résultat", "📊 Poules", "🏆 Tableau final"])

# --------------------------- # 
# --- Onglet Participants --- #
# --------------------------- #
with tabs[0]:
    st.header("Sélection des participants")
    
    if not tournoi_df.empty:
        st.info(f"✅ Le tournoi est déjà lancé avec {len(joueurs_tournoi)} participants")
        st.write("**Participants :**")
        for j in sorted(joueurs_tournoi):
            st.write(f"• {j}")
        
        st.divider()

        st.warning("⚠️ Pour modifier les participants, il faut réinitialiser le tournoi (Contacter Stef-la-pétanque)")
    
    else:
        st.write("Sélectionner les joueurs qui participeront au tournoi :")
        
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
            st.info("Une fois la liste des participants validés, allez dans l'onglet ⚙️ Paramètres")
            
# ------------------------- # 
# --- Onglet Paramètres --- #
# ------------------------- #
with tabs[1]:

    if not tournoi_df.empty:
        st.info(f"✅ Le tournoi est déjà lancé avec {len(joueurs_tournoi)} participants")
        st.write("**Participants :**")
        for j in sorted(joueurs_tournoi):
            st.write(f"• {j}")
        
        st.divider()
        
        # Afficher les paramètres du tournoi actuel
        if 'tournoi_params' in st.session_state:
            params = st.session_state.tournoi_params
            st.subheader("⚙️ Paramètres du tournoi actuel")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Phase de poules", "Oui" if params.get("phase_poule") else "Non")
                st.metric("Nombre de poules", params.get("nb_poules", "N/A"))
                st.metric("Sets gagnants", params.get("nb_sets_gagnants", "N/A"))
            with col2:
                st.metric("Consolante", "Oui" if params.get("consolante") else "Non")
                st.metric("Phase finale", params.get("cutoff_phase_finale", "N/A"))
                if params.get("consolante"):
                    st.metric("Consolante", params.get("cutoff_consolante", "N/A"))
        
        st.divider()

        st.warning("⚠️ Pour modifier les paramètres, il faut réinitialiser le tournoi (Contacter Stef-la-pétanque)")
    
    else:
        st.header("Paramètres du tournoi")
        
        st.info(f"Il y a {len(joueurs_selectionnes)} joueurs sélectionnés pour ce tournoi.")
        phase_poule = st.radio("Le tournoi possède-t-il une phase de poules ?", options=["Oui", "Non"])
        consolante = st.radio("Le tournoi possède-t-il une consolante ?", options=["Oui", "Non"])
        nb_sets = st.radio("Combien de sets faut-il gagner pour remporter un match ?", options=[1, 2, 3, 4])
        
        if phase_poule == "Oui":
            nb_poules = st.selectbox("Dans combien de poules les joueurs sont-ils répartis ?", options=[2, 3, 4, 5, 6, 7, 8])
            nb_j_poules_max = len(joueurs_selectionnes) // nb_poules
            nb_j_poules_supplement = len(joueurs_selectionnes) % nb_poules
            
            if nb_j_poules_supplement != 0:
                st.info(f"La configuration actuelle donne **{nb_j_poules_supplement} poule(s)** de **{nb_j_poules_max + 1} joueurs** et **{nb_poules - nb_j_poules_supplement} poule(s)** de **{nb_j_poules_max} joueurs**")
            else: 
                st.info(f"La configuration actuelle donne **{nb_poules} poules** de **{nb_j_poules_max} joueurs** chacune.")
            
            st.divider()
            
            cutoff_phase_finale = st.selectbox("À quelle étape la phase finale démarre-t-elle ?", options=["Demi-finale", "Quart de finale", "1/8ème de finale", "1/16ème de finale"])
            
            if consolante == "Oui":
                cutoff_consolante = st.selectbox("À quelle étape la phase finale de la consolante démarre-t-elle ?", options=["Demi-finale", "Quart de finale", "1/8ème de finale", "1/16ème de finale"])
            else:
                cutoff_consolante = None
            
            st.divider()
            
            # Aperçu du tournoi
            with st.expander("📊 Aperçu du tournoi"):
                nb_matchs_total = 0
                for i in range(nb_poules):
                    taille = nb_j_poules_max + (1 if i < nb_j_poules_supplement else 0)
                    nb_matchs_poule = taille * (taille - 1) // 2
                    nb_matchs_total += nb_matchs_poule
                
                st.write(f"**Phase de poules** : {nb_poules} poules")
                st.write(f"**Total matchs phase de poules** : {nb_matchs_total} matchs")
                
                nb_joueurs_phase_finale = {
                    "Demi-finale": 4,
                    "Quart de finale": 8,
                    "1/8ème de finale": 16,
                    "1/16ème de finale": 32
                }
                
                qualifies = nb_joueurs_phase_finale[cutoff_phase_finale]
                qualifies_par_poule = qualifies // nb_poules
                
                st.write(f"**Qualifiés pour la phase finale** : {qualifies} joueurs ({qualifies_par_poule} par poule)")
                st.write(f"**Phase finale** : À partir des {cutoff_phase_finale}")
                
                if consolante == "Oui":
                    st.write(f"**Consolante** : À partir des {cutoff_consolante}")
            
            st.divider()
            
            if st.button("🎲 Création du tournoi", use_container_width=True, key="btn_creation"):
                # Générer la phase de poules
                nb_matchs, poules, nb_tours = generer_phase_poules(
                    joueurs_selectionnes,
                    nb_poules,
                    st.session_state.sheet_tournoi 
                )
                    
                # Sauvegarder les paramètres du tournoi
                st.session_state.tournoi_params = {
                    "phase_poule": True,
                    "consolante": consolante == "Oui",
                    "nb_sets_gagnants": nb_sets,
                    "nb_poules": nb_poules,
                    "cutoff_phase_finale": cutoff_phase_finale,
                    "cutoff_consolante": cutoff_consolante
                }
                
                # Sauvegarder la composition des poules (déjà fait dans generer_phase_poules)
                # st.session_state.composition_poules = poules (déjà sauvegardé)
                # st.session_state.nb_tours_poules = nb_tours (déjà sauvegardé)
                    
                st.success(f"✅ Tournoi créé avec succès !")
                st.success(f"📊 {nb_matchs} matchs de poules générés sur {nb_tours} tours")
                    
                # Afficher la composition des poules
                st.subheader("📋 Composition des poules")
                    
                cols = st.columns(min(nb_poules, 4))  # Max 4 colonnes pour l'affichage
                    
                for idx, (lettre, joueurs_poule) in enumerate(poules.items()):
                    with cols[idx % len(cols)]:
                        st.markdown(f"**Poule {lettre}** ({len(joueurs_poule)} joueurs)")
                        for joueur in joueurs_poule:
                            st.write(f"• {joueur}")
                    
                st.balloons()
                    
                # Recharger les données
                tournoi_rows = st.session_state.sheet_tournoi.get_all_records()
                st.session_state.tournoi_df = pd.DataFrame(tournoi_rows)
                    
                st.rerun()
        else:
            # Pas de phase de poules
            st.info("ℹ️ Tournoi sans phase de poules - Génération du tableau final directement")
            # TODO : Implémenter la génération d'un bracket direct


# --------------------- # 
# --- Onglet Saisie --- #
# --------------------- #
with tabs[2]:
    st.header("Saisie des résultats")
    # Récupérer les matchs à jouer
    matchs_disponibles = []
    if not tournoi_df.empty:
        matchs_a_jouer = tournoi_df[tournoi_df["statut"] == "à jouer"]
        for _, match in matchs_a_jouer.iterrows():
            matchs_disponibles.append(f"{match['joueur_1']} vs {match['joueur_2']}")
    
    if not matchs_disponibles:
        st.warning("⚠️ Aucun match en attente.")
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
            
            with st.form("saisie_resultat_tournoi"):
                
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
                all_data = st.session_state.sheet_tournoi.get_all_values()
                row_idx = None
                
                for i, row in enumerate(all_data[1:], start=2):
                    if (row[0] == j1 and row[1] == j2) or (row[0] == j2 and row[1] == j1):
                        if row[4] == "à jouer": 
                            row_idx = i
                            break
                
                if row_idx:
                    # Mettre à jour le tournoi
                    st.session_state.sheet_tournoi.update(f"E{row_idx}:M{row_idx}", [["terminé", vainqueur, perdant, score_set_1, score_set_2, score_set_3, score_set_4, score_set_5, date]])
                    
                    # Recharger les données du championnat
                    tournoi_tat_rows = st.session_state.sheet_tournoi.get_all_records()
                    st.session_state.tournoi_df = pd.DataFrame(tournoi_tat_rows)
                    
                    st.success("✅ Résultat enregistré !")
                    st.rerun()
                else:
                    st.error("❌ Erreur : impossible de trouver le match")

# --------------------- # 
# --- Onglet Poules --- #
# --------------------- #
with tabs[3]:
    st.header("Phase de poules")
    
    # Vérifier que le tournoi a des poules
    if 'composition_poules' in st.session_state and st.session_state.composition_poules:
        poules = st.session_state.composition_poules
        nb_poules_actuel = len(poules)

        # ===========================
        # STATISTIQUES GLOBALES
        # ===========================
        total_matchs = len(tournoi_df[tournoi_df['phase'].str.contains('Poule', na=False)])
        matchs_joues = len(tournoi_df[(tournoi_df['phase'].str.contains('Poule', na=False)) & (tournoi_df['statut'] == 'terminé')])
            
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Matchs totaux", total_matchs)
        with col_stat2:
            st.metric("Matchs joués", matchs_joues)
        with col_stat3:
            progression = (matchs_joues / total_matchs * 100) if total_matchs > 0 else 0
            st.metric("Progression", f"{progression:.0f}%")
            
        st.progress(progression / 100)
        st.divider()

        # ===========================
        # COMPOSITION DES POULES
        # ===========================
        st.subheader("📋 Composition des poules")
        
        cols = st.columns(min(nb_poules_actuel, 4))  # Max 4 colonnes
        
        for idx, (lettre, joueurs_poule) in enumerate(poules.items()):
            with cols[idx % len(cols)]:
                st.markdown(f"**Poule {lettre}**")
                st.caption(f"{len(joueurs_poule)} joueurs")
                for joueur in joueurs_poule:
                    st.write(f"• {joueur}")
        
        st.divider()
        
        # ===========================
        # CLASSEMENT DES POULES
        # ===========================
        st.subheader("🏆 Classements des poules")
        
        # Afficher le classement de chaque poule
        cols_classement = st.columns(min(nb_poules_actuel, 1)) 
        
        for idx, (lettre, joueurs_poule) in enumerate(poules.items()):
            with cols_classement[idx % len(cols_classement)]:
                st.markdown(f"#### Poule {lettre}")
                
                classement_poule = calculer_classement_poule(lettre, joueurs_poule)
                
                # Réorganiser les colonnes pour l'affichage
                colonnes_affichage = ["Points", "Victoires", "Défaites", "Diff_sets", "Diff_points"]
                colonnes_renommees = ["Pts", "V", "D", "Δ Sets", "Δ Pts"]
                
                df_affichage = classement_poule[colonnes_affichage].copy()
                df_affichage.columns = colonnes_renommees
                
                st.dataframe(df_affichage, use_container_width=True, hide_index=False)
                with st.expander(f"Tableau des confrontations de la poule {lettre}"):
                    recap = pd.DataFrame("", index=joueurs_poule, columns=joueurs_poule)
                    
                    for _, row in tournoi_df.iterrows():
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
                        if vainq in joueurs_poule and adv in joueurs_poule:
                            recap.loc[vainq, adv] = f"{sets_perdant}-{sets_vainqueur}"
                            recap.loc[adv, vainq] = f"{sets_vainqueur}-{sets_perdant}"
            
                    recap_styled = recap.style.applymap(highlight_victoires)
                    st.dataframe(recap_styled, use_container_width=True)
        
    else:
        st.warning("⚠️ Aucune poule n'a été créée. Va dans l'onglet **Paramètres** pour créer le tournoi.")


# --------------------------- # 
# --- Onglet Phase finale --- #
# --------------------------- #
with tabs[4]:
    st.header("Phase finale")
    # ===========================
    # LANCEMENT PHASE FINALE
    # ===========================
    st.subheader("🚀 Lancement de la phase finale")
    
    # Vérifier si tous les matchs de poules sont terminés
    poules_terminees, matchs_joues, matchs_total = verifier_poules_terminees()
    
    if not poules_terminees:
        st.warning(f"⚠️ Phase de poules en cours : {matchs_joues}/{matchs_total} matchs terminés")
        st.info("La phase finale pourra être lancée une fois tous les matchs de poules terminés")
    else:
        # Vérifier si la phase finale est déjà lancée
        phase_finale_existe = not tournoi_df[
            (tournoi_df['phase'].str.contains('Finale', na=False)) |
            (tournoi_df['phase'].str.contains('Consolante', na=False))
        ].empty
        
        if phase_finale_existe:
            st.success("✅ La phase finale a déjà été lancée")
            
            # Afficher les qualifiés
            if 'tournoi_params' in st.session_state:
                params = st.session_state.tournoi_params
                
                with st.expander("👥 Joueurs qualifiés"):
                    classements = obtenir_classements_poules()
                    
                    nb_joueurs_phase_finale_map = {
                        "Demi-finale": 4,
                        "Quart de finale": 8,
                        "1/8ème de finale": 16,
                        "1/16ème de finale": 32
                    }
                    
                    cutoff = params["cutoff_phase_finale"]
                    nb_total_qualifies = nb_joueurs_phase_finale_map[cutoff]
                    nb_poules_total = params["nb_poules"]
                    nb_qualifies_par_poule = nb_total_qualifies // nb_poules_total
                    
                    st.write(f"**Phase finale ({cutoff})** : {nb_qualifies_par_poule} premiers de chaque poule")
                    
                    for lettre, classement in sorted(classements.items()):
                        st.write(f"**Poule {lettre}** :")
                        for i in range(min(nb_qualifies_par_poule, len(classement))):
                            st.write(f"  {i+1}. {classement[i]} ✅")
                    
                    if params.get("consolante"):
                        st.divider()
                        cutoff_consolante = params.get("cutoff_consolante")
                        nb_total_consolante = nb_joueurs_phase_finale_map[cutoff_consolante]
                        nb_consolante_par_poule = nb_total_consolante // nb_poules_total
                        
                        st.write(f"**Consolante ({cutoff_consolante})** : du {nb_qualifies_par_poule + 1}ème au {nb_qualifies_par_poule + nb_consolante_par_poule}ème de chaque poule")
                        
                        for lettre, classement in sorted(classements.items()):
                            st.write(f"**Poule {lettre}** :")
                            for i in range(nb_qualifies_par_poule, nb_qualifies_par_poule + nb_consolante_par_poule):
                                if i < len(classement):
                                    st.write(f"  {i+1}. {classement[i]} 🎯")
        else:
            st.success("✅ Tous les matchs de poules sont terminés !")
            
            # Aperçu des qualifiés
            if 'tournoi_params' in st.session_state:
                params = st.session_state.tournoi_params
                classements = obtenir_classements_poules()
                
                nb_joueurs_phase_finale_map = {
                    "Demi-finale": 4,
                    "Quart de finale": 8,
                    "1/8ème de finale": 16,
                    "1/16ème de finale": 32
                }
                
                cutoff = params["cutoff_phase_finale"]
                nb_total_qualifies = nb_joueurs_phase_finale_map[cutoff]
                nb_poules_total = params["nb_poules"]
                nb_qualifies_par_poule = nb_total_qualifies // nb_poules_total
                
                with st.expander("👀 Aperçu des qualifiés"):
                    st.write(f"**Phase finale** : Top {nb_qualifies_par_poule} de chaque poule")
                    
                    for lettre, classement in sorted(classements.items()):
                        st.write(f"**Poule {lettre}** :")
                        for i in range(min(nb_qualifies_par_poule, len(classement))):
                            st.write(f"  {i+1}. {classement[i]}")
                    
                    if params.get("consolante"):
                        st.divider()
                        cutoff_consolante = params.get("cutoff_consolante")
                        nb_total_consolante = nb_joueurs_phase_finale_map[cutoff_consolante]
                        nb_consolante_par_poule = nb_total_consolante // nb_poules_total
                        
                        st.write(f"**Consolante** : Rangs {nb_qualifies_par_poule + 1} à {nb_qualifies_par_poule + nb_consolante_par_poule}")
                        
                        for lettre, classement in sorted(classements.items()):
                            st.write(f"**Poule {lettre}** :")
                            for i in range(nb_qualifies_par_poule, nb_qualifies_par_poule + nb_consolante_par_poule):
                                if i < len(classement):
                                    st.write(f"  {i+1}. {classement[i]}")
                
                st.divider()
                
                # Bouton pour lancer
                if st.button("🎬 Lancer la phase finale", type="primary", use_container_width=True):
                    nb_finale, nb_consolante, qualifies = lancer_phase_finale()
                    
                    st.success(f"✅ Phase finale lancée avec succès !")
                    st.success(f"🏆 {nb_finale} matchs de phase finale générés")
                    
                    if nb_consolante > 0:
                        st.success(f"🎯 {nb_consolante} matchs de consolante générés")
                    
                    st.balloons()
                    
                    # Recharger les données
                    tournoi_rows = st.session_state.sheet_tournoi.get_all_records()
                    st.session_state.tournoi_df = pd.DataFrame(tournoi_rows)
                    
                    st.rerun()

    # Vérifier si la phase finale existe
    phase_finale_existe = not tournoi_df[
        (tournoi_df['phase'].str.contains('Finale', na=False)) |
        (tournoi_df['phase'].str.contains('Consolante', na=False))
    ].empty
    
    if not phase_finale_existe:
        st.warning("⚠️ La phase finale n'a pas encore été lancée")
        st.info("Va dans l'onglet **📋 Poules** pour lancer la phase finale une fois tous les matchs de poules terminés")
    else:
        # Statistiques de la phase finale
        matchs_finale = tournoi_df[
            (tournoi_df['phase'].str.contains('Finale', na=False)) & 
            (~tournoi_df['phase'].str.contains('Consolante', na=False))
        ]
        matchs_consolante = tournoi_df[tournoi_df['phase'].str.contains('Consolante', na=False)]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_finale = len(matchs_finale)
            termines_finale = len(matchs_finale[matchs_finale['statut'] == 'terminé'])
            st.metric("Phase Finale", f"{termines_finale}/{total_finale}")
        
        with col2:
            if not matchs_consolante.empty:
                total_consolante = len(matchs_consolante)
                termines_consolante = len(matchs_consolante[matchs_consolante['statut'] == 'terminé'])
                st.metric("Consolante", f"{termines_consolante}/{total_consolante}")
            else:
                st.metric("Consolante", "Non activée")
        
        with col3:
            total_general = total_finale + (len(matchs_consolante) if not matchs_consolante.empty else 0)
            termines_general = termines_finale + (termines_consolante if not matchs_consolante.empty else 0)
            progression = (termines_general / total_general * 100) if total_general > 0 else 0
            st.metric("Progression", f"{progression:.0f}%")
        
        st.progress(progression / 100)
        
        st.divider()
        
        # Afficher le bracket
        afficher_bracket_phase_finale()
        
        st.divider()
        
        # Tableau détaillé des matchs
        with st.expander("📋 Détail de tous les matchs"):
            tous_matchs_finale = pd.concat([matchs_finale, matchs_consolante])
            
            # Colonnes à afficher
            colonnes_affichage = ['phase', 'tour', 'joueur_1', 'joueur_2', 'statut', 'vainqueur']
            
            if not tous_matchs_finale.empty:
                st.dataframe(
                    tous_matchs_finale[colonnes_affichage],
                    use_container_width=True,
                    hide_index=True
                )