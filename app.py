# email_generator_ui.py
# Version avec interface modernisée, multicolore, à deux colonnes, progression visible et export à tout moment

import streamlit as st
import pandas as pd
import anthropic
import json
import os
import time
from datetime import date

# CONFIG
QUOTA_DAILY_REQ = 200
TEMP_FILE = "generation_temp.csv"
PROMPT_HISTORY_FILE = "prompt_history.json"

# STYLES -------------------------------------------------------------
st.set_page_config(page_title="Générateur d'emails Silviomotion", layout="wide")
st.markdown("""
    <style>
    body {background-color: #f7f9fc;}
    .title {font-size: 40px; font-weight: bold; color: #2e7d32;}
    .section {font-size: 22px; color: #1b1b1b; margin-top: 30px;}
    .sub {color: #888; font-size: 14px; margin-bottom: 10px;}
    .email-box {background-color: #fff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px;}
    .email-subject {font-weight: bold; color: #1565c0;}
    .email-message {white-space: pre-line; color: #333;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class=\"title\">🎥 Silviomotion - Générateur d'emails personnalisés</div>", unsafe_allow_html=True)

# COLONNES PRINCIPALES
col_params, col_output = st.columns([1, 2])

# API KEY ------------------------------------------------------------
with col_params:
    st.markdown('<div class="section">1. Entrez votre clé API Anthropic</div>', unsafe_allow_html=True)
    show_key = st.checkbox("Afficher la clé API", value=False)
    api_key_input = st.text_input("Clé API", type="default" if show_key else "password")
    if not api_key_input:
        st.stop()

    try:
        client = anthropic.Anthropic(api_key=api_key_input)
        client.messages.create(model="claude-3-haiku-20240307", max_tokens=10, messages=[{"role": "user", "content": "Test"}])
    except Exception as e:
        st.error(f"Clé API invalide ou erreur : {e}")
        st.stop()

# UPLOAD & REPRISE --------------------------------------------------
start_idx = 0
result_df = None
with col_params:
    st.markdown('<div class="section">2. Déposez le fichier CSV Sales Navigator</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Fichier CSV", type="csv")

df = None
if uploaded_file:
    if uploaded_file.size == 0:
        st.error("❌ Le fichier est vide. Veuillez uploader un CSV valide avec des données.")
        st.stop()
    try:
        df = pd.read_csv(uploaded_file, sep=";")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        st.stop()

    if os.path.exists(TEMP_FILE):
        with col_params:
            if st.button("🔁 Reprendre depuis dernière session"):
                try:
                    result_df = pd.read_csv(TEMP_FILE, sep=";")
                    start_idx = len(result_df)
                    df = pd.read_csv(uploaded_file, sep=";")

                    if start_idx > 0:
                        last_row = result_df.iloc[-1]
                        prospect_name = last_row.get("fullName") or f"{last_row.get('firstName', '')} {last_row.get('lastName', '')}"
                        st.info(f"🔁 Dernier prospect traité : **{prospect_name}** (ligne {start_idx})")

                    st.success(f"Reprise à la ligne {start_idx+1}")
                except Exception as e:
                    st.error(f"Erreur pendant la reprise : {e}")
                    st.stop()
            elif st.button("❌ Supprimer sauvegarde et recommencer"):
                os.remove(TEMP_FILE)
                result_df = None
                start_idx = 0

# ... (reste du code inchangé)
