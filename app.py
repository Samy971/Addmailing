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

# ZONE DE PARAMÈTRES & PROMPT --------------------------------------------------
def load_prompt_history():
    if os.path.exists(PROMPT_HISTORY_FILE):
        with open(PROMPT_HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_prompt_history(name, text):
    history = load_prompt_history()
    history[name] = text
    with open(PROMPT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

with col_params:
    st.markdown('<div class="section">3. Paramètres du modèle</div>', unsafe_allow_html=True)
    model_choice = st.selectbox("Modèle :", [
        "claude-3-5-sonnet-20240620",
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307"
    ])
    temperature = st.slider("Température", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.selectbox("max_tokens", [500, 1000, 1500, 2000, 3000], index=2)

    st.markdown('<div class="section">4. Prompt personnalisable</div>', unsafe_allow_html=True)
    prompt_history = load_prompt_history()
    prompt_names = list(prompt_history.keys())
    selected_prompt = st.selectbox("📚 Choisir un prompt enregistré :", [""] + prompt_names)

    default_prompt = ""
    if selected_prompt and selected_prompt in prompt_history:
        default_prompt = prompt_history[selected_prompt]

    prompt = st.text_area("✍️ Éditez le prompt (utilise {{PROSPECT_INFO}})", value=default_prompt, height=300)

    col1, col2 = st.columns([3, 1])
    with col1:
        new_prompt_name = st.text_input("💾 Nom du nouveau prompt à enregistrer")
    with col2:
        if st.button("Enregistrer le prompt") and new_prompt_name.strip():
            save_prompt_history(new_prompt_name.strip(), prompt)
            st.success(f"✅ Prompt « {new_prompt_name.strip()} » enregistré.")
            st.experimental_rerun()

# GÉNÉRATION --------------------------------------------------------
placeholder_output = col_output.empty()

with col_params:
    if df is not None and prompt and st.button("🚀 Générer les emails"):
        if result_df is None:
            result_df = df.iloc[:start_idx].copy()

        total = len(df)
        progress_bar = col_output.progress(start_idx / total)
        status_text = col_output.empty()
        req_used = start_idx

        for idx in range(start_idx, total):
            row = df.iloc[idx]
            full_name = row.get("fullName", f"{row.get('firstName', '')} {row.get('lastName', '')}")
            status_text.text(f"Traitement de {full_name} ({idx+1}/{total})")

            try:
content = "\\n".join(f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col]))
                final_prompt = prompt.replace("{{PROSPECT_INFO}}", content)
                response = client.messages.create(
                    model=model_choice.strip(), max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": final_prompt}]
                )
                email_json = json.loads(response.content[0].text.strip())
            except Exception as e:
                email_json = [{"subject": "[ERREUR]", "message": str(e)}] * 4

            new_row = row.to_dict()
            for i in range(4):
                new_row[f"email_{i+1}_subject"] = email_json[i]["subject"]
                new_row[f"email_{i+1}_message"] = email_json[i]["message"].replace("\n", "
")

            new_df = pd.DataFrame([new_row])
            result_df = pd.concat([result_df, new_df], ignore_index=True)
            result_df.to_csv(TEMP_FILE, sep=";", index=False)

            with placeholder_output.container():
                st.markdown("<div class='email-box'>", unsafe_allow_html=True)
                for i in range(4):
                    st.markdown(f"<div class='email-subject'>Objet {i+1}: {email_json[i]['subject']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='email-message'>{email_json[i]['message'].replace('\n','<br>')}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with open(TEMP_FILE, "rb") as f:
                col_params.download_button(
                    "📥 Télécharger les emails en cours",
                    data=f.read(),
                    file_name="emails_en_cours.csv",
                    mime="text/csv",
                    key=f"dl_{idx}"
                )

            progress_bar.progress((idx + 1) / total)
            req_used += 1

            if req_used >= QUOTA_DAILY_REQ:
                col_output.warning("Quota de requêtes atteint. Arrêt automatique.")
                break

        col_output.success("Emails générés avec succès !")
        csv = result_df.to_csv(index=False, sep=";", lineterminator="
", quoting=1).encode("utf-8")
        col_output.download_button("📥 Télécharger le fichier final", data=csv, file_name="emails_silviomotion.csv", mime="text/csv")
        os.remove(TEMP_FILE)
