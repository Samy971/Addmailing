# email_generator_ui.py
# Version style  - Interface élégante et moderne

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
STATS_FILE = "usage_stats.json"

# STYLES INSPIRÉS DE CLAUDE
st.set_page_config(page_title="Silviomotion Mail", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* RESET ET BASE */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: #fafafa;
        color: #2d3748;
        line-height: 1.6;
    }
    
    /* VARIABLES CSS - PALETTE CLAUDE */
    :root {
        --primary-orange: #e97749;
        --primary-orange-light: #f4a688;
        --primary-orange-dark: #d65d33;
        --accent-orange: #ff8c42;
        --bg-primary: #fafafa;
        --bg-secondary: #ffffff;
        --bg-tertiary: #f7fafc;
        --text-primary: #2d3748;
        --text-secondary: #4a5568;
        --text-muted: #718096;
        --border-light: #e2e8f0;
        --border-medium: #cbd5e0;
        --success: #48bb78;
        --warning: #ed8936;
        --error: #f56565;
        --info: #4299e1;
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        --transition: all 0.2s ease;
    }
    
    /* CONTENEUR PRINCIPAL */
    .main {
        background: var(--bg-primary);
        min-height: 100vh;
        padding: 0;
    }
    
    .block-container {
        padding: var(--spacing-xl) var(--spacing-lg);
        max-width: 1200px;
    }
    
    /* HEADER ÉLÉGANT */
    .elegant-header {
        text-align: center;
        padding: var(--spacing-xl) 0;
        margin-bottom: var(--spacing-xl);
        border-bottom: 1px solid var(--border-light);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-sm);
        letter-spacing: -0.025em;
    }
    
    .header-accent {
        color: var(--primary-orange);
    }
    
    .header-subtitle {
        font-size: 1.125rem;
        color: var(--text-secondary);
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* CARTES ÉLÉGANTES */
    .elegant-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: var(--spacing-xl);
        margin-bottom: var(--spacing-lg);
        transition: var(--transition);
    }
    
    .elegant-card:hover {
        border-color: var(--border-medium);
    }
    
    /* SECTIONS */
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-lg);
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }
    
    .section-title .emoji {
        font-size: 1.1rem;
    }
    
    /* MÉTRIQUES STYLE CLAUDE */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: var(--spacing-md);
        margin-bottom: var(--spacing-lg);
    }
    
    .metric-item {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        text-align: center;
        transition: var(--transition);
    }
    
    .metric-item:hover {
        background: var(--bg-secondary);
        border-color: var(--primary-orange-light);
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--primary-orange);
        margin-bottom: var(--spacing-xs);
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-muted);
        font-weight: 500;
    }
    
    /* INPUTS STYLE CLAUDE */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
        transition: var(--transition) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-orange) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* BOUTONS STYLE CLAUDE */
    .stButton > button {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 10px 16px !important;
        transition: var(--transition) !important;
        font-size: 14px !important;
    }
    
    .stButton > button:hover {
        background: var(--bg-tertiary) !important;
        border-color: var(--primary-orange-light) !important;
    }
    
    /* BOUTON PRINCIPAL */
    .stButton > button[kind="primary"] {
        background: var(--primary-orange) !important;
        border: 1px solid var(--primary-orange) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 20px !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--primary-orange-dark) !important;
        border-color: var(--primary-orange-dark) !important;
    }
    
    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: var(--primary-orange) !important;
        border-radius: var(--radius-sm) !important;
    }
    
    .stProgress > div > div > div {
        background: var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
    }
    
    /* SIDEBAR STYLE CLAUDE */
    .css-1d391kg {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-light) !important;
    }
    
    /* EXPANDER STYLE CLAUDE */
    .streamlit-expanderHeader {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-secondary) !important;
        border-color: var(--primary-orange-light) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-light) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
        padding: var(--spacing-lg) !important;
    }
    
    /* EMAIL CARDS ÉLÉGANTES */
    .email-card {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        margin-bottom: var(--spacing-md);
        transition: var(--transition);
    }
    
    .email-card:hover {
        background: var(--bg-secondary);
        border-color: var(--primary-orange-light);
    }
    
    .email-subject {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-md);
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }
    
    .email-subject .emoji {
        color: var(--primary-orange);
    }
    
    .email-body {
        color: var(--text-secondary);
        line-height: 1.6;
        background: var(--bg-secondary);
        padding: var(--spacing-md);
        border-radius: var(--radius-sm);
        border-left: 3px solid var(--primary-orange);
        font-size: 14px;
    }
    
    /* NOTIFICATIONS STYLE CLAUDE */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: var(--radius-md) !important;
        border: 1px solid !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
    }
    
    .stSuccess {
        background: #f0fff4 !important;
        border-color: var(--success) !important;
        color: #22543d !important;
    }
    
    .stError {
        background: #fed7d7 !important;
        border-color: var(--error) !important;
        color: #742a2a !important;
    }
    
    .stWarning {
        background: #fefcbf !important;
        border-color: var(--warning) !important;
        color: #744210 !important;
    }
    
    .stInfo {
        background: #bee3f8 !important;
        border-color: var(--info) !important;
        color: #2c5282 !important;
    }
    
    /* UPLOAD ZONE */
    .stFileUploader > div {
        background: var(--bg-secondary) !important;
        border: 2px dashed var(--border-medium) !important;
        border-radius: var(--radius-lg) !important;
        transition: var(--transition) !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--primary-orange-light) !important;
        background: var(--bg-tertiary) !important;
    }
    
    /* CHECKBOX STYLE CLAUDE */
    .stCheckbox > label {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
    }
    
    /* SLIDER STYLE CLAUDE */
    .stSlider > div > div > div > div {
        background: var(--primary-orange) !important;
    }
    
    .stSlider > div > div > div {
        background: var(--border-light) !important;
    }
    
    /* SELECTBOX STYLE CLAUDE */
    .stSelectbox > div > div {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
    }
    
    /* HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* SCROLLBAR STYLE CLAUDE */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-medium);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* BADGES ET LABELS */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 8px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-secondary);
    }
    
    .status-badge.success {
        background: #f0fff4;
        border-color: var(--success);
        color: #22543d;
    }
    
    .status-badge.warning {
        background: #fefcbf;
        border-color: var(--warning);
        color: #744210;
    }
    
    /* DIVIDERS */
    .divider {
        height: 1px;
        background: var(--border-light);
        margin: var(--spacing-lg) 0;
    }
    
    /* RESPONSIVE */
    @media (max-width: 768px) {
        .block-container {
            padding: var(--spacing-md);
        }
        
        .elegant-card {
            padding: var(--spacing-lg);
        }
        
        .header-title {
            font-size: 2rem;
        }
        
        .metrics-container {
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        }
    }
    
    /* ANIMATIONS SUBTILES */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* FOCUS STATES */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-orange) !important;
        outline: none !important;
    }
    
    /* LOADING STATES */
    .loading-text {
        color: var(--text-muted);
        font-style: italic;
    }
    
    /* TABLES */
    .dataframe {
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
    }
    
    .dataframe th {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    .dataframe td {
        border-color: var(--border-light) !important;
    }
    </style>
""", unsafe_allow_html=True)

# HEADER ÉLÉGANT STYLE CLAUDE
st.markdown("""
    <div class="elegant-header fade-in">
        <h1 class="header-title">
            <span class="header-accent">Silviomotion</span> AI
        </h1>
        <p class="header-subtitle">
            Génération intelligente d'emails personnalisés avec Claude AI
        </p>
    </div>
""", unsafe_allow_html=True)

col_params, col_output = st.columns([1, 2], gap="large")

# Initialisation des variables de session
if 'api_validated' not in st.session_state:
    st.session_state.api_validated = False
if 'client' not in st.session_state:
    st.session_state.client = None
if 'preview_data' not in st.session_state:
    st.session_state.preview_data = None
if 'generating' not in st.session_state:
    st.session_state.generating = False

def load_prompt_history():
    """Charge l'historique des prompts depuis le fichier JSON"""
    if os.path.exists(PROMPT_HISTORY_FILE):
        try:
            with open(PROMPT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_prompt_history(name, text):
    """Sauvegarde un prompt dans l'historique"""
    history = load_prompt_history()
    history[name] = text
    try:
        with open(PROMPT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")
        return False

def load_stats():
    """Charge les statistiques d'utilisation"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"total_requests": 0, "successful_requests": 0, "failed_requests": 0, "sessions": [], "daily_usage": {}}
    return {"total_requests": 0, "successful_requests": 0, "failed_requests": 0, "sessions": [], "daily_usage": {}}

def save_stats(stats):
    """Sauvegarde les statistiques"""
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Erreur sauvegarde stats : {e}")

def update_stats(success=True, cost_estimate=0):
    """Met à jour les statistiques"""
    stats = load_stats()
    today = date.today().isoformat()
    
    stats["total_requests"] += 1
    if success:
        stats["successful_requests"] += 1
    else:
        stats["failed_requests"] += 1
    
    # Statistiques quotidiennes
    if today not in stats["daily_usage"]:
        stats["daily_usage"][today] = {"requests": 0, "cost": 0}
    
    stats["daily_usage"][today]["requests"] += 1
    stats["daily_usage"][today]["cost"] += cost_estimate
    
    save_stats(stats)
    return stats

def get_display_name(df, index):
    """Fonction pour obtenir le nom d'affichage d'un prospect"""
    row = df.iloc[index]
    full_name = row.get('fullName', '')
    if full_name and str(full_name).strip():
        return str(full_name).strip()
    else:
        first_name = str(row.get('firstName', '')).strip()
        last_name = str(row.get('lastName', '')).strip()
        return f"{first_name} {last_name}".strip() or f"Prospect {index + 1}"

with col_params:
    st.markdown('<div class="elegant-card fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="emoji">🔑</span> Configuration API</div>', unsafe_allow_html=True)
    
    show_key = st.checkbox("Afficher la clé API", value=False)
    api_key_input = st.text_input(
        "Clé API Anthropic", 
        type="default" if show_key else "password", 
        placeholder="sk-ant-api03-..."
    )
    
    if api_key_input and not st.session_state.api_validated:
        with st.spinner("Validation de la clé API..."):
            try:
                client = anthropic.Anthropic(api_key=api_key_input)
                test_response = client.messages.create(
                    model="claude-3-haiku-20240307", 
                    max_tokens=10, 
                    messages=[{"role": "user", "content": "Test"}]
                )
                st.session_state.client = client
                st.session_state.api_validated = True
                st.success("✅ Clé API validée avec succès")
            except Exception as e:
                st.error(f"❌ Clé API invalide : {str(e)[:50]}...")
                st.session_state.api_validated = False
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not api_key_input:
        st.warning("⚠️ Veuillez entrer votre clé API Anthropic pour continuer")
        st.stop()
    
    if not st.session_state.api_validated:
        st.stop()

# Variables pour la reprise de session
start_idx = 0
result_df = None

with col_params:
    st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="emoji">📊</span> Analytics</div>', unsafe_allow_html=True)
    
    stats = load_stats()
    
    # Métriques style Claude
    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.markdown(f"""
            <div class="metric-item">
                <div class="metric-value">{stats["total_requests"]}</div>
                <div class="metric-label">Requêtes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_stat2:
        success_rate = (stats["successful_requests"] / max(stats["total_requests"], 1)) * 100
        st.markdown(f"""
            <div class="metric-item">
                <div class="metric-value">{success_rate:.1f}%</div>
                <div class="metric-label">Succès</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_stat3:
        today_usage = stats["daily_usage"].get(date.today().isoformat(), {"requests": 0})
        st.markdown(f"""
            <div class="metric-item">
                <div class="metric-value">{today_usage['requests']}</div>
                <div class="metric-label">Aujourd'hui</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Graphique simple
    if len(stats["daily_usage"]) > 0:
        last_7_days = sorted(stats["daily_usage"].items())[-7:]
        if last_7_days:
            dates = [item[0] for item in last_7_days]
            requests = [item[1]["requests"] for item in last_7_days]
            
            chart_data = pd.DataFrame({"Date": dates, "Requêtes": requests})
            st.bar_chart(chart_data.set_index("Date"), use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_params:
    st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="emoji">📁</span> Import de données</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Fichier CSV Sales Navigator", 
        type="csv",
        help="Formats supportés : CSV avec séparateur ; ou ,"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

df = None
if uploaded_file:
    if uploaded_file.size == 0:
        st.error("Le fichier est vide. Veuillez uploader un CSV valide.")
        st.stop()
    
    try:
        # Essayer différents séparateurs
        try:
            df = pd.read_csv(uploaded_file, sep=";")
        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=",")
        
        st.success(f"✅ Fichier chargé avec succès - **{len(df)}** prospects trouvés")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
        st.stop()

    # Gestion de la reprise de session
    if os.path.exists(TEMP_FILE):
        with col_params:
            st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span class="emoji">🔄</span> Reprise de session</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔁 Reprendre", use_container_width=True):
                    try:
                        result_df = pd.read_csv(TEMP_FILE, sep=";")
                        start_idx = len(result_df)
                        
                        if start_idx > 0:
                            last_row = result_df.iloc[-1]
                            prospect_name = last_row.get("fullName", f"{last_row.get('firstName', '')} {last_row.get('lastName', '')}")
                            st.info(f"🔁 Dernier prospect traité : **{prospect_name}** (ligne {start_idx})")
                        st.success(f"✅ Reprise à la ligne {start_idx+1}")
                    except Exception as e:
                        st.error(f"❌ Erreur pendant la reprise : {e}")
                        
            with col2:
                if st.button("🆕 Nouveau", use_container_width=True):
                    try:
                        os.remove(TEMP_FILE)
                        result_df = None
                        start_idx = 0
                        st.success("✅ Nouvelle session démarrée")
                        st.rerun()
                    except Exception as e:
                        st.warning(f"Attention : {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)

with col_params:
    st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="emoji">⚙️</span> Configuration du modèle</div>', unsafe_allow_html=True)
    
    model_choice = st.selectbox("Modèle Claude", [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-haiku-20240307"
    ])
    
    col_temp, col_tokens = st.columns(2)
    with col_temp:
        temperature = st.slider("Créativité", 0.0, 1.0, 0.7, 0.1)
    with col_tokens:
        max_tokens = st.selectbox("Longueur maximale", [500, 1000, 1500, 2000, 3000], index=2)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_params:
    st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="emoji">✍️</span> Prompt personnalisé</div>', unsafe_allow_html=True)
    
    prompt_history = load_prompt_history()
    prompt_names = list(prompt_history.keys())
    selected_prompt = st.selectbox("Templates sauvegardés", ["Nouveau prompt"] + prompt_names)

    default_prompt = """Tu es un expert en prospection commerciale pour Silviomotion, une agence de production vidéo.

Informations du prospect :
{{PROSPECT_INFO}}

Génère exactement 4 emails de prospection personnalisés en utilisant ces informations.

RÈGLES STRICTES :
1. Réponds SEULEMENT en JSON valide
2. Aucun texte explicatif avant ou après
3. Pas de balises XML ou HTML
4. Exactement 4 emails dans le format demandé

JSON attendu :
[
{"subject": "Objet 1", "message": "Message 1"},
{"subject": "Objet 2", "message": "Message 2"},
{"subject": "Objet 3", "message": "Message 3"},
{"subject": "Objet 4", "message": "Message 4"}
]

Commence ta réponse directement par [ et termine par ]"""

    if selected_prompt != "Nouveau prompt" and selected_prompt in prompt_history:
        default_prompt = prompt_history[selected_prompt]

    prompt = st.text_area(
        "Instructions pour Claude", 
        value=default_prompt, 
        height=200,
        help="Utilisez {{PROSPECT_INFO}} pour insérer les données du prospect",
        placeholder="Décrivez comment Claude doit générer les emails..."
    )

    # Sauvegarde de prompt
    col1, col2 = st.columns([3, 1])
    with col1:
        new_prompt_name = st.text_input("Nom du template", placeholder="Ex: Emails vidéo B2B")
    with col2:
        if st.button("💾 Sauvegarder", use_container_width=True) and new_prompt_name.strip():
            if save_prompt_history(new_prompt_name.strip(), prompt):
                st.success(f"✅ Template « {new_prompt_name.strip()} » sauvegardé")
                time.sleep(1)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_params:
    st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="emoji">👁️</span> Prévisualisation</div>', unsafe_allow_html=True)
    
    if df is not None and prompt:
        preview_idx = st.selectbox(
            "Prospect pour l'aperçu",
            range(len(df)),
            format_func=lambda x: get_display_name(df, x)
        )
        
        if st.button("Générer un aperçu", use_container_width=True):
            with st.spinner("Génération de l'aperçu..."):
                try:
                    row = df.iloc[preview_idx]
                    content_parts = []
                    for col in df.columns:
                        if pd.notna(row[col]) and str(row[col]).strip():
                            content_parts.append(f"{col}: {row[col]}")
                    
                    content = "\n".join(content_parts)
                    final_prompt = prompt.replace("{{PROSPECT_INFO}}", content)
                    
                    # Prompt modifié pour un seul email
                    single_email_prompt = final_prompt.replace(
                        "4 emails", "1 email"
                    ).replace(
                        '[\n{"subject": "Objet 1", "message": "Message 1"},\n{"subject": "Objet 2", "message": "Message 2"},\n{"subject": "Objet 3", "message": "Message 3"},\n{"subject": "Objet 4", "message": "Message 4"}\n]',
                        '[{"subject": "Objet", "message": "Message"}]'
                    )
                    
                    response = st.session_state.client.messages.create(
                        model=model_choice,
                        max_tokens=max_tokens//2,
                        temperature=temperature,
                        messages=[{"role": "user", "content": single_email_prompt}]
                    )
                    
                    response_text = response.content[0].text.strip()
                    if response_text.startswith("```json"):
                        response_text = response_text.replace("```json", "").replace("```", "").strip()
                    
                    preview_email = json.loads(response_text)
                    if isinstance(preview_email, list) and len(preview_email) > 0:
                        preview_email = preview_email[0]
                    
                    st.session_state.preview_data = {
                        "prospect": get_display_name(df, preview_idx),
                        "email": preview_email
                    }
                    
                    update_stats(success=True, cost_estimate=0.001)
                    
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)[:100]}...")
                    update_stats(success=False)
        
        # Affichage de l'aperçu
        if st.session_state.preview_data:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            email_data = st.session_state.preview_data['email']
            
            st.markdown(f"""
                <div class="email-card">
                    <div class="email-subject">
                        <span class="emoji">📧</span> {email_data.get('subject', 'N/A')}
                    </div>
                    <div class="email-body">
                        {email_data.get('message', 'N/A').replace(chr(10), '<br>')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# GÉNÉRATION PRINCIPALE
with col_params:
    if df is not None and prompt:
        st.markdown('<div class="elegant-card">', unsafe_allow_html=True)
        
        if not st.session_state.generating:
            if st.button("🚀 Lancer la génération", type="primary", use_container_width=True):
                st.session_state.generating = True
                st.rerun()
        else:
            st.markdown('<span class="loading-text">🔄 Génération en cours...</span>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Zone d'affichage des résultats
placeholder_output = col_output.empty()

# PROCESSUS DE GÉNÉRATION
if st.session_state.generating and df is not None and prompt:
    try:
        if result_df is None:
            result_df = df.iloc[:start_idx].copy() if start_idx > 0 else pd.DataFrame()

        total = len(df)
        start_time = time.time()

        with col_output:
            st.markdown('<div class="elegant-card fade-in">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span class="emoji">🤖</span> Génération en cours</div>', unsafe_allow_html=True)
            
            progress_bar = st.progress(start_idx / total if total > 0 else 0)
            status_text = st.empty()
            display_area = st.empty()
            req_used = start_idx

            for idx in range(start_idx, total):
                row = df.iloc[idx]
                full_name = get_display_name(df, idx)

                status_text.markdown(f"**Traitement :** {full_name} ({idx+1}/{total})")

                try:
                    content_parts = [f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col]) and str(row[col]).strip()]
                    content = "\n".join(content_parts)
                    final_prompt = prompt.replace("{{PROSPECT_INFO}}", content)

                    # Appel API
                    response = st.session_state.client.messages.create(
                        model=model_choice,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=[{"role": "user", "content": final_prompt}]
                    )

                    if not response or not response.content or len(response.content) == 0:
                        raise ValueError("Réponse vide de l'API Claude")
                    
                    response_text = response.content[0].text.strip()
                    
                    if not response_text:
                        raise ValueError("Réponse vide")
                    
                    # Nettoyage
                    if response_text.startswith("```json"):
                        response_text = response_text.replace("```json", "").replace("```", "").strip()
                    elif response_text.startswith("```"):
                        response_text = response_text.replace("```", "").strip()
                    
                    # Gestion XML -> JSON si nécessaire
                    if response_text.startswith("<") or "<email" in response_text:
                        st.warning(f"Conversion XML pour {full_name}...")
                        import re
                        
                        email_pattern = r'<email\d*>.*?</email\d*>'
                        emails = re.findall(email_pattern, response_text, re.DOTALL)
                        
                        email_json = []
                        for i, email_xml in enumerate(emails[:4]):
                            subject_match = re.search(r'<subject[^>]*>(.*?)</subject[^>]*>', email_xml, re.DOTALL)
                            message_match = re.search(r'<message[^>]*>(.*?)</message[^>]*>', email_xml, re.DOTALL)
                            
                            if not message_match:
                                content_after_subject = re.sub(r'<subject[^>]*>.*?</subject[^>]*>', '', email_xml, flags=re.DOTALL)
                                message_match = re.search(r'>(.*)', content_after_subject.strip(), re.DOTALL)
                            
                            subject = subject_match.group(1).strip() if subject_match else f"Email {i+1} pour {full_name}"
                            message = message_match.group(1).strip() if message_match else "Contenu non disponible"
                            
                            subject = re.sub(r'<[^>]+>', '', subject).strip()
                            message = re.sub(r'<[^>]+>', '', message).strip()
                            
                            email_json.append({"subject": subject, "message": message})
                        
                        while len(email_json) < 4:
                            email_json.append({
                                "subject": f"Email {len(email_json)+1} - {full_name}",
                                "message": "Email généré automatiquement suite à une conversion XML."
                            })
                            
                    else:
                        try:
                            email_json = json.loads(response_text)
                        except json.JSONDecodeError as json_err:
                            st.error(f"Erreur JSON pour {full_name}")
                            raise ValueError(f"Parse JSON impossible: {json_err}")

                    # Validation
                    if not isinstance(email_json, list):
                        raise ValueError(f"Réponse non-liste: {type(email_json)}")
                    
                    if len(email_json) != 4:
                        st.warning(f"Emails incomplets pour {full_name}: {len(email_json)}/4")
                        while len(email_json) < 4:
                            email_json.append({
                                "subject": f"Email {len(email_json)+1} - {full_name}",
                                "message": "Email généré automatiquement."
                            })

                    # Validation emails
                    for i, email in enumerate(email_json):
                        if not isinstance(email, dict) or 'subject' not in email or 'message' not in email:
                            email_json[i] = {
                                "subject": f"Email {i+1} - {full_name} (corrigé)",
                                "message": "Email corrigé automatiquement."
                            }

                    estimated_cost = 0.003 if "sonnet" in model_choice else 0.001
                    update_stats(success=True, cost_estimate=estimated_cost)

                except Exception as e:
                    st.warning(f"Erreur pour {full_name} : {e}")
                    email_json = [
                        {
                            "subject": f"Email {i+1} - {full_name} [ERREUR]", 
                            "message": f"Erreur de génération.\n\nErreur: {str(e)}\n\nVeuillez réessayer."
                        }
                        for i in range(4)
                    ]
                    update_stats(success=False)

                # Ajout résultats
                new_row = row.to_dict()
                for i in range(4):
                    new_row[f"email_{i+1}_subject"] = email_json[i]["subject"]
                    new_row[f"email_{i+1}_message"] = email_json[i]["message"].replace("\\n", "\n")

                new_df = pd.DataFrame([new_row])
                result_df = pd.concat([result_df, new_df], ignore_index=True)

                try:
                    result_df.to_csv(TEMP_FILE, sep=";", index=False)
                except Exception as e:
                    st.warning(f"Erreur sauvegarde : {e}")

                # Affichage des résultats
                with display_area.container():
                    st.markdown(f"### Emails générés pour **{full_name}**")
                    
                    for i in range(4):
                        st.markdown(f"""
                            <div class="email-card">
                                <div class="email-subject">
                                    <span class="emoji">📧</span> Email {i+1}: {email_json[i]['subject']}
                                </div>
                                <div class="email-body">
                                    {email_json[i]['message'].replace(chr(10), '<br>')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                # Téléchargement intermédiaire
                if idx % 10 == 9:
                    try:
                        with open(TEMP_FILE, "rb") as f:
                            st.download_button(
                                "💾 Télécharger la progression",
                                data=f.read(),
                                file_name=f"emails_progress_{idx+1}.csv",
                                mime="text/csv",
                                key=f"dl_{idx}",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.warning(f"Erreur téléchargement : {e}")

                progress_bar.progress((idx + 1) / total)
                req_used += 1

                if req_used >= QUOTA_DAILY_REQ:
                    st.warning(f"⚠️ Quota journalier atteint ({QUOTA_DAILY_REQ})")
                    break

                time.sleep(0.1)

            # Finalisation
            status_text.markdown("**✅ Génération terminée**")
            
            # Téléchargement final
            if result_df is not None and len(result_df) > 0:
                csv = result_df.to_csv(index=False, sep=";").encode("utf-8")
                st.download_button(
                    "📥 Télécharger le fichier complet",
                    data=csv,
                    file_name=f"emails_silviomotion_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
                
                # Nettoyage
                try:
                    if os.path.exists(TEMP_FILE):
                        os.remove(TEMP_FILE)
                except Exception as e:
                    st.warning(f"⚠️ Fichier temporaire non supprimé : {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)

    finally:
        st.session_state.generating = False

# PAGE D'ACCUEIL ÉLÉGANTE
if uploaded_file is None:
    with col_output:
        st.markdown("""
            <div class="elegant-card fade-in">
                <div class="section-title"><span class="emoji">🚀</span> Bienvenue sur Silviomotion AI</div>
                
                <div style="margin: 1.5rem 0;">
                    <p style="font-size: 1.1rem; color: var(--text-secondary); line-height: 1.7;">
                        Générez automatiquement des emails de prospection ultra-personnalisés 
                        grâce à l'intelligence artificielle Claude d'Anthropic.
                    </p>
                </div>
                
                <div style="background: var(--bg-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1.5rem; margin: 1.5rem 0;">
                    <h4 style="color: var(--text-primary); margin-bottom: 1rem; font-weight: 600;">📋 Guide de démarrage</h4>
                    <ol style="color: var(--text-secondary); line-height: 1.6; padding-left: 1.2rem;">
                        <li style="margin-bottom: 0.5rem;"><strong>Configurez</strong> votre clé API Anthropic</li>
                        <li style="margin-bottom: 0.5rem;"><strong>Uploadez</strong> votre fichier CSV Sales Navigator</li>
                        <li style="margin-bottom: 0.5rem;"><strong>Personnalisez</strong> votre prompt de génération</li>
                        <li style="margin-bottom: 0.5rem;"><strong>Testez</strong> avec la prévisualisation</li>
                        <li><strong>Lancez</strong> la génération automatique</li>
                    </ol>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 2rem;">
                    <div style="background: var(--bg-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1.2rem; text-align: center;">
                        <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">⚡</div>
                        <div style="color: var(--primary-orange); font-weight: 600; margin-bottom: 0.3rem;">Ultra Rapide</div>
                        <div style="color: var(--text-muted); font-size: 0.85rem;">Centaines d'emails en minutes</div>
                    </div>
                    
                    <div style="background: var(--bg-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1.2rem; text-align: center;">
                        <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🎯</div>
                        <div style="color: var(--primary-orange); font-weight: 600; margin-bottom: 0.3rem;">Hyper Ciblé</div>
                        <div style="color: var(--text-muted); font-size: 0.85rem;">Personnalisation intelligente</div>
                    </div>
                    
                    <div style="background: var(--bg-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1.2rem; text-align: center;">
                        <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📊</div>
                        <div style="color: var(--primary-orange); font-weight: 600; margin-bottom: 0.3rem;">Analytics</div>
                        <div style="color: var(--text-muted); font-size: 0.85rem;">Métriques temps réel</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# SIDEBAR ÉLÉGANTE
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0 1.5rem 0; border-bottom: 1px solid var(--border-light);">
            <h3 style="color: var(--primary-orange); margin-bottom: 0.3rem; font-weight: 600;">📊 Analytics</h3>
            <p style="color: var(--text-muted); font-size: 0.9rem;">Métriques de performance</p>
        </div>
    """, unsafe_allow_html=True)
    
    stats = load_stats()
    
    if stats["total_requests"] > 0:
        st.markdown(f"""
            <div style="background: var(--bg-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1.2rem; margin: 1rem 0;">
                <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">Requêtes totales</div>
                <div style="color: var(--primary-orange); font-size: 1.5rem; font-weight: 700;">{stats['total_requests']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        success_rate = (stats["successful_requests"] / max(stats["total_requests"], 1)) * 100
        st.markdown(f"""
            <div style="background: var(--bg-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1.2rem; margin: 1rem 0;">
                <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">Taux de succès</div>
                <div style="color: var(--primary-orange); font-size: 1.5rem; font-weight: 700;">{success_rate:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
        
        total_cost = sum([day_data.get("cost", 0) for day_data in stats["daily_usage"].values()])
        st.markdown(f"""
            <div style="background: var(--bg-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1.2rem; margin: 1rem 0;">
                <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">Coût estimé</div>
                <div style="color: var(--primary-orange); font-size: 1.5rem; font-weight: 700;">${total_cost:.3f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Graphique évolution
        if len(stats["daily_usage"]) > 1:
            st.markdown("**📈 Évolution (7 derniers jours)**")
            last_days = dict(sorted(stats["daily_usage"].items())[-7:])
            chart_df = pd.DataFrame([
                {"Date": date_str, "Requêtes": data["requests"]}
                for date_str, data in last_days.items()
            ])
            st.line_chart(chart_df.set_index("Date"), use_container_width=True)
    else:
        st.markdown("""
            <div style="background: var(--bg-tertiary); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1.2rem; margin: 1rem 0; text-align: center;">
                <div style="color: var(--text-muted); font-size: 0.9rem;">Lancez votre première génération pour voir les métriques</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Reset button
    if st.button("🗑️ Reset Analytics", use_container_width=True):
        if os.path.exists(STATS_FILE):
            os.remove(STATS_FILE)
            st.success("✅ Analytics réinitialisées")
            st.rerun()
            
