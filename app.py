import streamlit as st
import pandas as pd
import anthropic
import json
import os

# ---------- STYLES ----------
st.set_page_config(page_title="Générateur d'emails Silviomotion", layout="centered")
st.markdown("""
    <style>
    .big-title {
        font-size: 36px;
        font-weight: bold;
        color: #4CAF50;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 22px;
        color: #333;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    .small-note {
        font-size: 13px;
        color: #888;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="big-title">🎥 Générateur d’emails Silviomotion</div>', unsafe_allow_html=True)
st.markdown('<p class="small-note">Créez une séquence de 4 emails personnalisés à partir d’un fichier Sales Navigator</p>', unsafe_allow_html=True)

# ---------- 0. CLÉ API ----------
st.markdown('<div class="section-title">🔐 0. Entrez votre clé API Anthropic</div>', unsafe_allow_html=True)
show_key = st.checkbox("Afficher la clé API", value=False)
api_key_input = st.text_input("Clé API", type="default" if show_key else "password")

if not api_key_input:
    st.warning("💡 Veuillez entrer votre clé API pour continuer.")
    st.stop()

# Vérification de la clé API avec modèle actif
try:
    test_client = anthropic.Anthropic(api_key=api_key_input)
    test_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=10,
        messages=[{"role": "user", "content": "Ping"}]
    )
    client = test_client
except Exception as e:
    st.error(f"❌ Clé API invalide ou refusée : {e}")
    st.stop()

# ---------- 1. FICHIER ----------
st.markdown('<div class="section-title">📤 1. Dépose ton fichier CSV Sales Navigator</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Fichier CSV (séparateur `;`)", type="csv")

# ---------- 2. MODÈLE À JOUR ----------
st.markdown('<div class="section-title">🧠 2. Choisis le modèle Claude</div>', unsafe_allow_html=True)
model_choice = st.selectbox("Modèle", [
    "claude-3-sonnet-20240601",
    "claude-3-opus-20240601",
    "claude-3-haiku-20240307"
])

# ---------- 3. PROMPT ----------
st.markdown('<div class="section-title">✍️ 3. Rédige ou recharge ton prompt</div>', unsafe_allow_html=True)
PROMPT_HISTORY_FILE = "prompt_history.json"

def load_prompt_history():
    if os.path.exists(PROMPT_HISTORY_FILE):
        with open(PROMPT_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_prompt_history(name, text):
    history = load_prompt_history()
    history[name] = text
    with open(PROMPT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

history = load_prompt_history()
selected_prompt = st.selectbox("📜 Charger un prompt existant :", [""] + list(history.keys()))
default_prompt = history[selected_prompt] if selected_prompt else ""

prompt = st.text_area("Prompt personnalisé (utilise {{PROSPECT_INFO}})", value=default_prompt, height=500)

col1, col2 = st.columns([3, 1])
with col1:
    new_prompt_name = st.text_input("💾 Nom du prompt à sauvegarder")
with col2:
    if st.button("Sauvegarder le prompt") and new_prompt_name.strip():
        save_prompt_history(new_prompt_name.strip(), prompt)
        st.success(f"✅ Prompt « {new_prompt_name} » sauvegardé.")

# ---------- 4. GENERATE ----------
if uploaded_file and prompt and st.button("🚀 Générer les emails"):

    try:
        df = pd.read_csv(uploaded_file, sep=";")
        result_df = df.copy()

        for i in range(1, 5):
            result_df[f"email_{i}_subject"] = ""
            result_df[f"email_{i}_message"] = ""

        with st.spinner("🔄 Génération en cours..."):
            progress_bar = st.progress(0)
            total = len(df)
            status_text = st.empty()

            for idx, row in df.iterrows():
                full_name = row["fullName"] if "fullName" in row else f"{row.get('firstName', '')} {row.get('lastName', '')}"
                status_text.text(f"👤 Traitement du prospect {idx + 1}/{total} : {full_name}")

                try:
                    prospect_info = "\n".join([f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])])
                    final_prompt = prompt.replace("{{PROSPECT_INFO}}", prospect_info)

                    response = client.messages.create(
                        model=model_choice.strip(),
                        max_tokens=2000,
                        temperature=0.7,
                        messages=[{"role": "user", "content": final_prompt}]
                    )

                    email_json = json.loads(response.content[0].text.strip())

                    for i in range(4):
                        result_df.at[idx, f"email_{i+1}_subject"] = email_json[i]["subject"]
                        result_df.at[idx, f"email_{i+1}_message"] = email_json[i]["message"].replace("\\n", "\n")

                except Exception as e:
                    for i in range(4):
                        result_df.at[idx, f"email_{i+1}_subject"] = "[ERREUR]"
                        result_df.at[idx, f"email_{i+1}_message"] = str(e)

                progress_bar.progress((idx + 1) / total)

        st.success("✅ Emails générés avec succès !")
        st.dataframe(result_df[[f"email_{i}_subject" for i in range(1, 5)] + [f"email_{i}_message" for i in range(1, 5)]])

        csv = result_df.to_csv(index=False, sep=";", lineterminator="\n", quoting=1).encode("utf-8")
        st.download_button("📥 Télécharger le fichier final", data=csv, file_name="emails_silviomotion.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Erreur pendant la génération : {str(e)}")
