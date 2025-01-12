import base64
import streamlit as st
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Configurer le style global de Streamlit
st.set_page_config(layout="wide", page_title="Dashboard Feux de Forêt")

# Convertir l'image en base64
with open("feux_png.jpg", "rb") as image_file:

    encoded_image = base64.b64encode(image_file.read()).decode()

# Ajouter un style de background et un titre principal avec logo
page_style = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpeg;base64,{encoded_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    opacity: 0.9; /* Réduction de l'opacité de l'image */
}}
[data-testid="stHeader"] {{
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
}}
h1.title {{
    font-size: 2em;
    text-align: center;
    color: #ffffff;
    margin-bottom: 1.5em;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}}
h2.section-title {{
    font-size: 1.5em;
    color: #ffffff;
    margin-bottom: 1em;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
}}
h3.chart-title {{
    font-size: 1.2em;
    margin-top: 0.5em;
    color: #ffffff;
}}
.axis-label {{
    font-size: 10px;
    color: #ffffff;
}}
.legend {{
    background-color: rgba(255, 255, 255, 0.8);
    border: 1px solid #dddddd;
    padding: 5px;
}}
.logo-container {{
    text-align: center;
    margin-bottom: 20px;
}}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# Titre principal
st.markdown('<h1 class="title" style="margin-top: 0em;">Analyse Intégrée des Feux de Forêt en Milieu Méditerranéen : Combinaison de SIG et Python pour une Exploration Spatiale, Statistique et Visuelle</h1>', unsafe_allow_html=True)

# Chargement des données
file_path = 'C:/Users/user/Desktop/GMS/Projet_bridier/Incendos.csv'
data = pd.read_csv(file_path, encoding='latin1', sep=';')

# Section 1 : Graphiques de feux par heure et mois
st.markdown('<h2 class="section-title">Analyses des feux par heure et par mois</h2>', unsafe_allow_html=True)

def plot_heatmap_and_3d():
    fires_by_hour_month = data.groupby(['Mois', 'Heure']).size().reset_index(name='Nombre_de_feux')
    pivot_table = fires_by_hour_month.pivot_table(index='Heure', columns='Mois', values='Nombre_de_feux', fill_value=0)

    # Configuration de la figure pour les deux graphiques côte à côte
    fig = plt.figure(figsize=(14, 6))

    # Heatmap
    ax1 = fig.add_subplot(121)
    sns.heatmap(pivot_table, annot=False, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Nombre de Feux'}, ax=ax1)
    ax1.set_title("Feux par Heure et Mois", fontsize=12)
    ax1.set_xlabel("Mois", fontsize=10)
    ax1.set_ylabel("Heure", fontsize=10)

    # Graphique 3D
    ax2 = fig.add_subplot(122, projection='3d')
    x, y = np.meshgrid(pivot_table.columns.values, pivot_table.index.values)
    z = pivot_table.values
    surface = ax2.plot_surface(x, y, z, cmap='viridis', edgecolor='k', alpha=0.8)
    ax2.set_title("Feux en 3D", fontsize=12)
    ax2.set_xlabel("Mois", fontsize=10)
    ax2.set_ylabel("Heure", fontsize=10)
    ax2.set_zlabel("Nombre de Feux", fontsize=10)
    fig.colorbar(surface, ax=ax2, shrink=0.7, aspect=15, label='Nombre de Feux')

    plt.tight_layout()
    return fig

st.pyplot(plot_heatmap_and_3d())

# Section 2 : Surface brûlée par tranche de 5 ans
st.markdown('<h2 class="section-title">Surface brûlée totale par tranche de 5 ans</h2>', unsafe_allow_html=True)

def plot_surface_by_year():
    data['Surface_m2'] = pd.to_numeric(data['Surface_m2'], errors='coerce')
    data['Annee'] = pd.to_numeric(data['Annee'], errors='coerce')
    data['Tranche 5 ans'] = (data['Annee'] // 5) * 5
    somme_surface_5_ans = data.groupby('Tranche 5 ans')['Surface_m2'].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(somme_surface_5_ans.index, somme_surface_5_ans.values, width=4, color='steelblue', edgecolor='black')
    ax.set_xlabel('Tranche de 5 ans', fontsize=10)
    ax.set_ylabel('Surface brûlée totale (m²)', fontsize=10)
    ax.set_title('Surface brûlée par tranche de 5 ans', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' ')))
    plt.tight_layout()
    return fig

st.pyplot(plot_surface_by_year())

# Section 3 : Top communes affectées
st.markdown('<h2 class="section-title">Top des communes affectées</h2>', unsafe_allow_html=True)

def plot_top_bottom_communes():
    data['Surface_m2'] = pd.to_numeric(data['Surface_m2'], errors='coerce')
    data['Nom_commune'] = data['Nom_commune'].fillna('Inconnue')
    somme_surface_commune = data.groupby('Nom_commune')['Surface_m2'].sum()
    somme_surface_commune_sorted = somme_surface_commune.sort_values(ascending=False)
    top_communes = somme_surface_commune_sorted.head(10)
    bottom_communes = somme_surface_commune_sorted.tail(10)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.bar(top_communes.index, top_communes.values, color='darkorange', edgecolor='black')
    ax1.set_title("Top 10 Communes les Plus Affectées", fontsize=12)
    ax1.tick_params(axis='x', rotation=45, labelsize=8)

    ax2.bar(bottom_communes.index, bottom_communes.values, color='darkgreen', edgecolor='black')
    ax2.set_title("Top 10 Communes les Moins Affectées", fontsize=12)
    ax2.tick_params(axis='x', rotation=45, labelsize=8)

    plt.tight_layout()
    return fig

st.pyplot(plot_top_bottom_communes())

# Section 4 : Cartes des feux en juillet et août
st.markdown('<h2 class="section-title">Cartes des feux par mois</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

def plot_fire_map_july():
    shapefile_path = r'C:/Users/user/Desktop/GMS/Projet_bridier/Commune_var.shp'
    july_data_path = r'C:/Users/user/Desktop/GMS/Projet_bridier/Moyenne_des_Feux_en_Juillet_par_Commune_avec_Code_INSEE.csv'
    communes = gpd.read_file(shapefile_path)
    july_data = pd.read_csv(july_data_path, delimiter=',')
    communes = communes.rename(columns={'INSEE_COM': 'Code_INSEE'})
    july_data['Code_INSEE'] = july_data['Code_INSEE'].astype(str)
    merged = communes.merge(july_data, on='Code_INSEE')
    fig, ax = plt.subplots(figsize=(8, 6))
    merged.plot(column='Nombre de feux', ax=ax, legend=True, cmap='YlGnBu', legend_kwds={'shrink': 0.7, 'label': "Nombre de Feux"})
    ax.set_title("Moyenne des Feux - Juillet", fontsize=12)
    plt.tight_layout()
    return fig

col1.pyplot(plot_fire_map_july())

def plot_fire_map_august():
    shapefile_path = r'C:/Users/user/Desktop/GMS/Projet_bridier/Commune_var.shp'
    august_data_path = r'C:/Users/user/Desktop/GMS/Projet_bridier/Moyenne_des_Feux_en_Ao_t_par_Commune_avec_Code_INSEE.csv'
    communes = gpd.read_file(shapefile_path)
    august_data = pd.read_csv(august_data_path, delimiter=',')
    communes = communes.rename(columns={'INSEE_COM': 'Code_INSEE'})
    august_data['Code_INSEE'] = august_data['Code_INSEE'].astype(str)
    merged = communes.merge(august_data, on='Code_INSEE')
    fig, ax = plt.subplots(figsize=(8, 6))
    merged.plot(column='Nombre de feux', ax=ax, legend=True, cmap='YlGnBu', legend_kwds={'shrink': 0.7, 'label': "Nombre de Feux"})
    ax.set_title("Moyenne des Feux - Août", fontsize=12)
    plt.tight_layout()
    return fig

col2.pyplot(plot_fire_map_august())

st.markdown('<h2 class="section-title">Carte des Feux par Commune - Var</h2>', unsafe_allow_html=True)

def plot_fire_map_commune_var():
    feu_par_commune_path = r'C:/Users/user/Desktop/GMS/Projet_bridier/feu_par_commune.csv'
    shapefile_path = r'C:/Users/user/Desktop/GMS/Projet_bridier/Commune_var.shp'
    feu_par_commune = pd.read_csv(feu_par_commune_path, encoding='latin1', sep=';')
    communes = gpd.read_file(shapefile_path)
    communes = communes.rename(columns={'NOM_COM': 'Commune'})
    feu_par_commune = feu_par_commune.rename(columns={'Code INSEE': 'INSEE_COM', 'Nombre feu': 'Nombre de Feux'})
    merged = communes.merge(feu_par_commune, on='INSEE_COM', how='left')
    merged['Nombre de Feux'] = merged['Nombre de Feux'].fillna(0)
    fig, ax = plt.subplots(figsize=(10, 7))
    merged.plot(column='Nombre de Feux', ax=ax, legend=True, cmap='YlOrRd', legend_kwds={'shrink': 0.7, 'label': "Nombre de Feux"})
    ax.set_title("Carte des Feux par Commune - Var", fontsize=12)
    plt.tight_layout()
    return fig

st.pyplot(plot_fire_map_commune_var())


