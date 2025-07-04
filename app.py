# email_generator_ui.py
# Version ultra-moderne - Design maximum avec Streamlit

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

# STYLES ULTRA-MODERNES
st.set_page_config(page_title="Silviomotion AI", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* RESET ET BASE */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #0a0a0a;
        color: #ffffff;
    }
    
    /* VARIABLES CSS */
    :root {
        --primary-orange: #ff6b35;
        --secondary-orange: #ff8c42;
        --accent-orange: #ff4500;
        --dark-bg: #0a0a0a;
        --card-bg: rgba(20, 20, 20, 0.8);
        --glass-bg: rgba(255, 255, 255, 0.05);
        --border-color: rgba(255, 107, 53, 0.3);
        --text-primary: #ffffff;
        --text-secondary: #b0b0b0;
        --shadow-primary: 0 8px 32px rgba(255, 107, 53, 0.2);
        --shadow-secondary: 0 4px 16px rgba(0, 0, 0, 0.4);
        --gradient-primary: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);
        --gradient-glass: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        --border-radius: 16px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* CONTENEUR PRINCIPAL */
    .main {
        background: radial-gradient(ellipse at top, rgba(255, 107, 53, 0.1) 0%, transparent 70%),
                    linear-gradient(180deg, #0a0a0a 0%, #121212 100%);
        min-height: 100vh;
        padding: 0;
    }
    
    .block-container {
        padding: 2rem 1rem;
        max-width: 1400px;
    }
    
    /* HEADER MODERNE */
    .modern-header {
        text-align: center;
        padding: 3rem 0 4rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .header-title {
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
        position: relative;
    }
    
    .header-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    .header-bg {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 107, 53, 0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
        z-index: -1;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* CARTES GLASS MORPHISM */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-primary), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        padding: 2rem;
        margin-bottom: 2rem;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: var(--gradient-primary);
        opacity: 0.6;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(255, 107, 53, 0.3), var(--shadow-secondary);
        border-color: var(--primary-orange);
    }
    
    /* SECTIONS MODERNES */
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-orange);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, var(--primary-orange) 0%, transparent 100%);
    }
    
    /* MÉTRIQUES MODERNES */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: var(--transition);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-primary);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--primary-orange);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--primary-orange);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* INPUTS MODERNES */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: rgba(20, 20, 20, 0.8) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        transition: var(--transition) !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-orange) !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
        outline: none !important;
    }
    
    /* BOUTONS ULTRA-MODERNES */
    .stButton > button {
        background: var(--gradient-primary) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
        font-size: 14px !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 32px rgba(255, 107, 53, 0.4) !important;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* BOUTON PRINCIPAL */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-orange) 0%, var(--primary-orange) 100%) !important;
        font-size: 16px !important;
        padding: 16px 32px !important;
        box-shadow: var(--shadow-primary) !important;
        font-weight: 700 !important;
    }
    
    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: var(--gradient-primary) !important;
        border-radius: 8px !important;
        height: 8px !important;
    }
    
    .stProgress > div > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    /* SIDEBAR MODERNE */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(10, 10, 10, 0.95) 0%, rgba(20, 20, 20, 0.95) 100%) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    /* EXPANDER MODERNE */
    .streamlit-expanderHeader {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--primary-orange) !important;
        font-weight: 600 !important;
        transition: var(--transition) !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--primary-orange) !important;
        background: rgba(255, 107, 53, 0.1) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.5rem !important;
    }
    
    /* EMAIL BOX ULTRA-MODERNE */
    .email-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        transition: var(--transition);
    }
    
    .email-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-primary);
    }
    
    .email-card:hover {
        transform: translateX(4px);
        border-color: var(--primary-orange);
    }
    
    .email-subject {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--secondary-orange);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .email-body {
        color: var(--text-secondary);
        line-height: 1.6;
        background: rgba(0, 0, 0, 0.3);
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid var(--primary-orange);
        font-size: 14px;
    }
    
    /* NOTIFICATIONS MODERNES */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px !important;
        border: none !important;
        backdrop-filter: blur(16px) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stSuccess {
        background: rgba(34, 197, 94, 0.1) !important;
        border-left: 4px solid #22c55e !important;
        color: #22c55e !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid #ef4444 !important;
        color: #ef4444 !important;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.1) !important;
        border-left: 4px solid #fbbf24 !important;
        color: #fbbf24 !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border-left: 4px solid #3b82f6 !important;
        color: #3b82f6 !important;
    }
    
    /* UPLOAD ZONE MODERNE */
    .stFileUploader > div {
        background: var(--glass-bg) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: 16px !important;
        transition: var(--transition) !important;
        padding: 2rem !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--primary-orange) !important;
        background: rgba(255, 107, 53, 0.05) !important;
    }
    
    /* CHECKBOX MODERNE */
    .stCheckbox > label {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
    }
    
    /* SLIDER MODERNE */
    .stSlider > div > div > div > div {
        background: var(--primary-orange) !important;
    }
    
    .stSlider > div > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* CUSTOM SCROLLBAR */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gradient-primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary-orange);
    }
    
    /* RESPONSIVE */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.5rem;
        }
        
        .glass-card {
            padding: 1.5rem;
        }
        
        .header-title {
            font-size: 2.5rem;
        }
    }
    
    /* ANIMATIONS */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fadeInUp {
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    /* LOADING SPINNER */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        animation: spin 1s linear infinite;
    }
    </style>
""", unsafe_allow_html=True)

# HEADER ULTRA-MODERNE
st.markdown("""
    <div class="modern-header">
        <div class="header-bg"></div>
        <h1 class="header-title">🎥 Silviomotion AI</h1>
        <p class="header-subtitle">Générateur d'emails ultra-personnalisés powered by Claude AI</p>
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
    st.markdown('<div class="glass-card animate-fadeInUp">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔑 Configuration API</div>', unsafe_allow_html=True)
    
    show_key = st.checkbox("Afficher la clé API", value=False)
    api_key_input = st.text_input("Clé API Anthropic", type="default" if show_key else "password", placeholder="sk-ant-...")
    
    if api_key_input and not st.session_state.api_validated:
        with st.spinner("Validation de la clé API..."):
            try:
                client = anthropic.Anthropic(api_key=api_key_input)
                # Test simple avec le modèle le moins cher
                test_response = client.messages.create(
                    model="claude-3-haiku-20240307", 
                    max_tokens=10, 
                    messages=[{"role": "user", "content": "Test"}]
                )
                st.session_state.client = client
                st.session_state.api_validated = True
                st.success("✅ Clé API validée avec succès !")
            except Exception as e:
                st.error(f"❌ Clé API invalide : {str(e)[:100]}...")
                st.session_state.api_validated = False
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not api_key_input:
        st.warning("⚠️ Veuillez entrer votre clé API Anthropic pour continuer.")
        st.stop()
    
    if not st.session_state.api_validated:
        st.stop()

# Variables pour la reprise de session
start_idx = 0
result_df = None

with col_params:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Dashboard Analytics</div>', unsafe_allow_html=True)
    
    stats = load_stats()
    
    # Métriques modernes
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats["total_requests"]}</div>
                <div class="metric-label">Total Requêtes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_stat2:
        success_rate = (stats["successful_requests"] / max(stats["total_requests"], 1)) * 100
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{success_rate:.1f}%</div>
                <div class="metric-label">Taux de Succès</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_stat3:
        today_usage = stats["daily_usage"].get(date.today().isoformat(), {"requests": 0})
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{today_usage['requests']}</div>
                <div class="metric-label">Aujourd'hui</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Graphique des 7 derniers jours
    if len(stats["daily_usage"]) > 0:
        last_7_days = sorted(stats["daily_usage"].items())[-7:]
        if last_7_days:
            dates = [item[0] for item in last_7_days]
            requests = [item[1]["requests"] for item in last_7_days]
            
            chart_data = pd.DataFrame({"Date": dates, "Requêtes": requests})
            st.bar_chart(chart_data.set_index("Date"), use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_params:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📁 Import de Données</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Déposez votre fichier CSV Sales Navigator", 
        type="csv",
        help="Format supporté: CSV avec séparateur ; ou ,"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

df = None
if uploaded_file:
    if uploaded_file.size == 0:
        st.error("❌ Le fichier est vide. Veuillez uploader un CSV valide avec des données.")
        st.stop()
    
    try:
        # Essayer différents séparateurs
        try:
            df = pd.read_csv(uploaded_file, sep=";")
        except:
            uploaded_file.seek(0)  # Remettre le curseur au début
            df = pd.read_csv(uploaded_file, sep=",")
        
        st.success(f"✅ Fichier chargé avec succès ! **{len(df)}** prospects trouvés.")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
        st.stop()

    # Gestion de la reprise de session
    if os.path.exists(TEMP_FILE):
        with col_params:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🔄 Reprise de Session</div>', unsafe_allow_html=True)
            
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
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙️ Configuration IA</div>', unsafe_allow_html=True)
    
    model_choice = st.selectbox("Modèle Claude :", [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-haiku-20240307"
    ])
    
    col_temp, col_tokens = st.columns(2)
    with col_temp:
        temperature = st.slider("Créativité", 0.0, 1.0, 0.7, 0.1)
    with col_tokens:
        max_tokens = st.selectbox("Longueur", [500, 1000, 1500, 2000, 3000], index=2)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_params:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✍️ Prompt Engineering</div>', unsafe_allow_html=True)
    
    prompt_history = load_prompt_history()
    prompt_names = list(prompt_history.keys())
    selected_prompt = st.selectbox("📚 Templates sauvegardés :", ["Nouveau prompt"] + prompt_names)

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
        "Prompt personnalisé", 
        value=default_prompt, 
        height=250,
        help="Utilisez {{PROSPECT_INFO}} pour insérer automatiquement les données du prospect",
        placeholder="Votre prompt d'instruction pour Claude..."
    )

    # Sauvegarde de prompt avec design moderne
    col1, col2 = st.columns([3, 1])
    with col1:
        new_prompt_name = st.text_input("💾 Nom du template", placeholder="Ex: Prompt Vidéo B2B")
    with col2:
        if st.button("💾 Save", use_container_width=True) and new_prompt_name.strip():
            if save_prompt_history(new_prompt_name.strip(), prompt):
                st.success(f"✅ Template sauvegardé !")
                time.sleep(1)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_params:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 Live Preview</div>', unsafe_allow_html=True)
    
    if df is not None and prompt:
        preview_idx = st.selectbox(
            "Prospect pour l'aperçu :",
            range(len(df)),
            format_func=lambda x: get_display_name(df, x)
        )
        
        if st.button("👁️ Générer Aperçu", use_container_width=True, help="Test gratuit de votre prompt"):
            with st.spinner("🤖 Claude génère votre aperçu..."):
                try:
                    row = df.iloc[preview_idx]
                    content_parts = []
                    for col in df.columns:
                        if pd.notna(row[col]) and str(row[col]).strip():
                            content_parts.append(f"{col}: {row[col]}")
                    
                    content = "\n".join(content_parts)
                    final_prompt = prompt.replace("{{PROSPECT_INFO}}", content)
                    
                    # Prompt modifié pour un seul email (économie)
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
                    st.error(f"❌ Erreur preview : {str(e)[:100]}...")
                    update_stats(success=False)
        
        # Affichage preview moderne
        if st.session_state.preview_data:
            st.markdown("---")
            email_data = st.session_state.preview_data['email']
            
            st.markdown(f"""
                <div class="email-card">
                    <div class="email-subject">
                        📧 {email_data.get('subject', 'N/A')}
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
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        if not st.session_state.generating:
            if st.button("🚀 LANCER LA GÉNÉRATION", type="primary", use_container_width=True):
                st.session_state.generating = True
                st.rerun()
        else:
            st.info("🔄 Génération en cours...")
        
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
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🤖 Génération en Cours</div>', unsafe_allow_html=True)
            
            progress_bar = st.progress(start_idx / total if total > 0 else 0)
            status_text = st.empty()
            display_area = st.empty()
            req_used = start_idx

            for idx in range(start_idx, total):
                row = df.iloc[idx]
                full_name = get_display_name(df, idx)

                status_text.markdown(f"**🔄 Processing:** {full_name} ({idx+1}/{total})")

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
                    
                    # Nettoyage robuste
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

                    # Validation structure
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

                # Affichage moderne des résultats
                with display_area.container():
                    st.markdown(f"### 📧 Emails générés pour **{full_name}**")
                    
                    for i in range(4):
                        st.markdown(f"""
                            <div class="email-card">
                                <div class="email-subject">
                                    📧 Email {i+1}: {email_json[i]['subject']}
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
                                "💾 Télécharger progression",
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
            status_text.markdown("**✅ Génération terminée !**")
            
            # Téléchargement final
            if result_df is not None and len(result_df) > 0:
                csv = result_df.to_csv(index=False, sep=";").encode("utf-8")
                st.download_button(
                    "📥 TÉLÉCHARGER LE FICHIER COMPLET",
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

# PAGE D'ACCUEIL MODERNE
if uploaded_file is None:
    with col_output:
        st.markdown("""
            <div class="glass-card animate-fadeInUp">
                <div class="section-title">🚀 Bienvenue sur Silviomotion AI</div>
                
                <div style="text-align: center; margin: 2rem 0;">
                    <div style="font-size: 1.2rem; color: var(--text-secondary); line-height: 1.8;">
                        <p>🎯 <strong style="color: var(--primary-orange);">Génération automatique</strong> d'emails ultra-personnalisés</p>
                        <p>🤖 <strong style="color: var(--primary-orange);">Powered by Claude AI</strong> - La plus avancée des IA</p>
                        <p>📈 <strong style="color: var(--primary-orange);">Analytics en temps réel</strong> - Trackez vos performances</p>
                        <p>💾 <strong style="color: var(--primary-orange);">Templates intelligents</strong> - Réutilisez vos meilleurs prompts</p>
                    </div>
                </div>
                
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; margin: 2rem 0;">
                    <h4 style="color: var(--secondary-orange); margin-bottom: 1rem;">📋 Guide de démarrage :</h4>
                    <div style="color: var(--text-secondary); line-height: 1.6;">
                        <p><strong style="color: var(--primary-orange);">1.</strong> Configurez votre clé API Anthropic</p>
                        <p><strong style="color: var(--primary-orange);">2.</strong> Uploadez votre fichier CSV Sales Navigator</p>
                        <p><strong style="color: var(--primary-orange);">3.</strong> Personnalisez votre prompt de génération</p>
                        <p><strong style="color: var(--primary-orange);">4.</strong> Testez avec la prévisualisation live</p>
                        <p><strong style="color: var(--primary-orange);">5.</strong> Lancez la génération automatique</p>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem;">
                    <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                        <div style="color: var(--primary-orange); font-weight: 600;">Ultra Rapide</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">Générez des centaines d'emails en minutes</div>
                    </div>
                    
                    <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                        <div style="color: var(--primary-orange); font-weight: 600;">Hyper Ciblé</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">Personnalisation basée sur les données prospect</div>
                    </div>
                    
                    <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                        <div style="color: var(--primary-orange); font-weight: 600;">Analytics Pro</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">Métriques de performance en temps réel</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# SIDEBAR MODERNE
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0 2rem 0;">
            <h3 style="color: var(--primary-orange); margin-bottom: 0.5rem;">📊 Analytics Pro</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">Dashboard temps réel</p>
        </div>
    """, unsafe_allow_html=True)
    
    stats = load_stats()
    
    if stats["total_requests"] > 0:
        st.markdown(f"""
            <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
                <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;">Statistiques globales</div>
                <div style="color: var(--primary-orange); font-size: 1.5rem; font-weight: 700;">{stats['total_requests']}</div>
                <div style="color: var(--text-secondary); font-size: 0.8rem;">Requêtes totales</div>
            </div>
        """, unsafe_allow_html=True)
        
        success_rate = (stats["successful_requests"] / max(stats["total_requests"], 1)) * 100
        st.markdown(f"""
            <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
                <div style="color: var(--primary-orange); font-size: 1.5rem; font-weight: 700;">{success_rate:.1f}%</div>
                <div style="color: var(--text-secondary); font-size: 0.8rem;">Taux de succès</div>
            </div>
        """, unsafe_allow_html=True)
        
        total_cost = sum([day_data.get("cost", 0) for day_data in stats["daily_usage"].values()])
        st.markdown(f"""
            <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
                <div style="color: var(--primary-orange); font-size: 1.5rem; font-weight: 700;">${total_cost:.3f}</div>
                <div style="color: var(--text-secondary); font-size: 0.8rem;">Coût estimé total</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Graphique évolution
        if len(stats["daily_usage"]) > 1:
            st.markdown("**📈 Évolution (7 jours)**")
            last_days = dict(sorted(stats["daily_usage"].items())[-7:])
            chart_df = pd.DataFrame([
                {"Date": date_str, "Requêtes": data["requests"]}
                for date_str, data in last_days.items()
            ])
            st.line_chart(chart_df.set_index("Date"), use_container_width=True)
    else:
        st.info("🔄 Lancez votre première génération pour voir les analytics")
    
    # Reset button moderne
    if st.button("🗑️ Reset Analytics", use_container_width=True):
        if os.path.exists(STATS_FILE):
            os.remove(STATS_FILE)
            st.success("✅ Analytics réinitialisées !")
            st.rerun()
