# email_generator_ui.py
# Version complète corrigée, stable et fonctionnelle

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

# STYLES
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

col_params, col_output = st.columns([1, 2])

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
    st.markdown('<div class="section">1. Entrez votre clé API Anthropic</div>', unsafe_allow_html=True)
    show_key = st.checkbox("Afficher la clé API", value=False)
    api_key_input = st.text_input("Clé API", type="default" if show_key else "password")
    
    if api_key_input and not st.session_state.api_validated:
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
            st.error(f"❌ Clé API invalide ou erreur : {e}")
            st.session_state.api_validated = False
    
    if not api_key_input:
        st.warning("⚠️ Veuillez entrer votre clé API Anthropic pour continuer.")
        st.stop()
    
    if not st.session_state.api_validated:
        st.stop()

# Variables pour la reprise de session
start_idx = 0
result_df = None

with col_params:
    st.markdown('<div class="section">📊 Statistiques d\'utilisation</div>', unsafe_allow_html=True)
    stats = load_stats()
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Total requêtes", stats["total_requests"])
    with col_stat2:
        success_rate = (stats["successful_requests"] / max(stats["total_requests"], 1)) * 100
        st.metric("Taux de succès", f"{success_rate:.1f}%")
    with col_stat3:
        today_usage = stats["daily_usage"].get(date.today().isoformat(), {"requests": 0})
        st.metric("Aujourd'hui", f"{today_usage['requests']}/{QUOTA_DAILY_REQ}")
    
    # Graphique des 7 derniers jours
    if len(stats["daily_usage"]) > 0:
        last_7_days = sorted(stats["daily_usage"].items())[-7:]
        if last_7_days:
            dates = [item[0] for item in last_7_days]
            requests = [item[1]["requests"] for item in last_7_days]
            
            chart_data = pd.DataFrame({"Date": dates, "Requêtes": requests})
            st.bar_chart(chart_data.set_index("Date"))

with col_params:
    st.markdown('<div class="section">2. Déposez le fichier CSV Sales Navigator</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Fichier CSV", type="csv")

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
        
        st.success(f"✅ Fichier chargé avec succès ! {len(df)} lignes trouvées.")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
        st.stop()

    # Gestion de la reprise de session
    if os.path.exists(TEMP_FILE):
        with col_params:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔁 Reprendre session"):
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
                if st.button("❌ Nouvelle session"):
                    try:
                        os.remove(TEMP_FILE)
                        result_df = None
                        start_idx = 0
                        st.success("✅ Nouvelle session démarrée")
                        st.rerun()
                    except Exception as e:
                        st.warning(f"Attention : {e}")

with col_params:
    st.markdown('<div class="section">3. Paramètres du modèle</div>', unsafe_allow_html=True)
    model_choice = st.selectbox("Modèle :", [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-haiku-20240307"
    ])
    temperature = st.slider("Température", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.selectbox("max_tokens", [500, 1000, 1500, 2000, 3000], index=2)

    st.markdown('<div class="section">4. Prompt personnalisable</div>', unsafe_allow_html=True)
    prompt_history = load_prompt_history()
    prompt_names = list(prompt_history.keys())
    selected_prompt = st.selectbox("📚 Choisir un prompt enregistré :", ["Nouveau prompt"] + prompt_names)

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
        "✍️ Éditez le prompt (utilisez {{PROSPECT_INFO}} pour insérer les données)", 
        value=default_prompt, 
        height=300,
        help="Le placeholder {{PROSPECT_INFO}} sera remplacé par les données du prospect"
    )

    # Sauvegarde de prompt
    col1, col2 = st.columns([3, 1])
    with col1:
        new_prompt_name = st.text_input("💾 Nom du nouveau prompt à enregistrer")
    with col2:
        if st.button("💾 Enregistrer") and new_prompt_name.strip():
            if save_prompt_history(new_prompt_name.strip(), prompt):
                st.success(f"✅ Prompt « {new_prompt_name.strip()} » enregistré.")
                time.sleep(1)
                st.rerun()

    # PRÉVISUALISATION EN DIRECT
    st.markdown('<div class="section">🔍 Prévisualisation</div>', unsafe_allow_html=True)
    
    if df is not None and prompt:
        preview_idx = st.selectbox(
            "Choisir un prospect pour la prévisualisation :",
            range(len(df)),
            format_func=lambda x: get_display_name(df, x)
        )
        
        if st.button("👁️ Générer aperçu", help="Génère un email de test pour voir le rendu"):
            with st.spinner("Génération de l'aperçu..."):
                try:
                    row = df.iloc[preview_idx]
                    content_parts = []
                    for col in df.columns:
                        if pd.notna(row[col]) and str(row[col]).strip():
                            content_parts.append(f"{col}: {row[col]}")
                    
                    content = "\n".join(content_parts)
                    final_prompt = prompt.replace("{{PROSPECT_INFO}}", content)
                    
                    # Générer un seul email pour l'aperçu (économie d'API)
                    preview_prompt = final_prompt.replace(
                        "Répondez UNIQUEMENT au format JSON suivant :\n[", 
                        "Répondez UNIQUEMENT au format JSON suivant :\n["
                    ).replace("Message 4\"}", "Message 1\"}]")
                    
                    # Prompt modifié pour un seul email
                    single_email_prompt = final_prompt.replace(
                        "générez 4 emails", "générez 1 email"
                    ).replace(
                        '[\n  {"subject": "Objet 1", "message": "Message 1"},\n  {"subject": "Objet 2", "message": "Message 2"},\n  {"subject": "Objet 3", "message": "Message 3"},\n  {"subject": "Objet 4", "message": "Message 4"}\n]',
                        '[{"subject": "Objet", "message": "Message"}]'
                    )
                    
                    response = st.session_state.client.messages.create(
                        model=model_choice,
                        max_tokens=max_tokens//2,  # Moins de tokens pour la preview
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
                    
                    # Mettre à jour les stats
                    update_stats(success=True, cost_estimate=0.001)
                    
                except Exception as e:
                    st.error(f"❌ Erreur prévisualisation : {e}")
                    update_stats(success=False)
        
        # Affichage de la prévisualisation
        if st.session_state.preview_data:
            with st.expander(f"📧 Aperçu pour {st.session_state.preview_data['prospect']}", expanded=True):
                email_data = st.session_state.preview_data['email']
                st.markdown(f"**📧 Objet :** {email_data.get('subject', 'N/A')}")
                st.text_area(
                    "Message :", 
                    value=email_data.get('message', 'N/A'), 
                    height=200,
                    disabled=True,
                    key="preview_message"
                )

# Zone d'affichage des résultats
placeholder_output = col_output.empty()

# Génération des emails
with col_params:
    if df is not None and prompt and st.button("🚀 Générer les emails", type="primary") and not st.session_state.generating:
        st.session_state.generating = True
        try:
            if result_df is None:
                result_df = df.iloc[:start_idx].copy() if start_idx > 0 else pd.DataFrame()

            total = len(df)
            start_time = time.time()

            with col_output:
                progress_bar = st.progress(start_idx / total if total > 0 else 0)
                status_text = st.empty()
                display_area = st.empty()
                req_used = start_idx

                for idx in range(start_idx, total):
                    row = df.iloc[idx]
                    full_name = get_display_name(df, idx)

                    status_text.text(f"🔄 Traitement de {full_name} ({idx+1}/{total})")

                    try:
                        content_parts = [f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col]) and str(row[col]).strip()]
                        content = "\n".join(content_parts)
                        final_prompt = prompt.replace("{{PROSPECT_INFO}}", content)

                        # Appel API avec gestion d'erreur renforcée
                        response = st.session_state.client.messages.create(
                            model=model_choice,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            messages=[{"role": "user", "content": final_prompt}]
                        )

                        # Vérification robuste de la réponse
                        if not response or not response.content or len(response.content) == 0:
                            raise ValueError("Réponse vide de l'API Claude")
                        
                        response_text = response.content[0].text.strip()
                        
                        # Debug: afficher la réponse brute en cas de problème
                        if not response_text:
                            st.warning(f"Réponse vide pour {full_name}")
                            raise ValueError("Réponse vide")
                        
                        # Nettoyage plus robuste de la réponse
                        if response_text.startswith("```json"):
                            response_text = response_text.replace("```json", "").replace("```", "").strip()
                        elif response_text.startswith("```"):
                            response_text = response_text.replace("```", "").strip()
                        
                        # Détection et conversion XML vers JSON si nécessaire
                        if response_text.startswith("<") or "<email" in response_text:
                            st.warning(f"Réponse XML détectée pour {full_name}, conversion en cours...")
                            # Conversion basique XML vers JSON
                            import re
                            
                            # Extraire les emails du XML
                            email_pattern = r'<email\d*>.*?</email\d*>'
                            emails = re.findall(email_pattern, response_text, re.DOTALL)
                            
                            email_json = []
                            for i, email_xml in enumerate(emails[:4]):  # Limiter à 4 emails
                                # Extraire subject et message
                                subject_match = re.search(r'<subject[^>]*>(.*?)</subject[^>]*>', email_xml, re.DOTALL)
                                message_match = re.search(r'<message[^>]*>(.*?)</message[^>]*>', email_xml, re.DOTALL)
                                
                                # Si pas de balises message, prendre tout le contenu après subject
                                if not message_match:
                                    content_after_subject = re.sub(r'<subject[^>]*>.*?</subject[^>]*>', '', email_xml, flags=re.DOTALL)
                                    message_match = re.search(r'>(.*)', content_after_subject.strip(), re.DOTALL)
                                
                                subject = subject_match.group(1).strip() if subject_match else f"Email {i+1} pour {full_name}"
                                message = message_match.group(1).strip() if message_match else "Contenu non disponible"
                                
                                # Nettoyer les balises HTML/XML restantes
                                subject = re.sub(r'<[^>]+>', '', subject).strip()
                                message = re.sub(r'<[^>]+>', '', message).strip()
                                
                                email_json.append({
                                    "subject": subject,
                                    "message": message
                                })
                            
                            # Compléter si moins de 4 emails trouvés
                            while len(email_json) < 4:
                                email_json.append({
                                    "subject": f"Email {len(email_json)+1} - {full_name}",
                                    "message": "Email généré automatiquement suite à une conversion XML."
                                })
                                
                        else:
                            # Tentative de parsing JSON normal
                            try:
                                email_json = json.loads(response_text)
                            except json.JSONDecodeError as json_err:
                                st.error(f"Erreur JSON pour {full_name}. Réponse brute: {response_text[:200]}...")
                                raise ValueError(f"Impossible de parser JSON: {json_err}")

                        # Validation de la structure
                        if not isinstance(email_json, list):
                            raise ValueError(f"La réponse n'est pas une liste: {type(email_json)}")
                        
                        if len(email_json) != 4:
                            st.warning(f"Nombre d'emails incorrect pour {full_name}: {len(email_json)} au lieu de 4")
                            # Compléter avec des emails par défaut si nécessaire
                            while len(email_json) < 4:
                                email_json.append({
                                    "subject": f"Email supplémentaire {len(email_json)+1} - {full_name}",
                                    "message": "Email généré automatiquement suite à une réponse incomplète."
                                })

                        # Validation de chaque email
                        for i, email in enumerate(email_json):
                            if not isinstance(email, dict) or 'subject' not in email or 'message' not in email:
                                email_json[i] = {
                                    "subject": f"Email {i+1} - {full_name} (corrigé)",
                                    "message": "Email corrigé automatiquement suite à une structure invalide."
                                }

                        estimated_cost = 0.003 if "sonnet" in model_choice else 0.001
                        update_stats(success=True, cost_estimate=estimated_cost)

                    except Exception as e:
                        st.warning(f"Erreur pour {full_name} : {e}")
                        # Emails de fallback en cas d'erreur
                        email_json = [
                            {
                                "subject": f"Email {i+1} - {full_name} [ERREUR]", 
                                "message": f"Une erreur s'est produite lors de la génération de cet email.\n\nErreur: {str(e)}\n\nVeuillez réessayer ou modifier le prompt."
                            }
                            for i in range(4)
                        ]
                        update_stats(success=False)

                    # Ajout au DataFrame résultat
                    new_row = row.to_dict()
                    for i in range(4):
                        new_row[f"email_{i+1}_subject"] = email_json[i]["subject"]
                        new_row[f"email_{i+1}_message"] = email_json[i]["message"].replace("\\n", "\n")

                    new_df = pd.DataFrame([new_row])
                    result_df = pd.concat([result_df, new_df], ignore_index=True)

                    try:
                        result_df.to_csv(TEMP_FILE, sep=";", index=False)
                    except Exception as e:
                        st.warning(f"Erreur de sauvegarde temporaire : {e}")

                    # Affichage unique dans zone réservée
                    with display_area.container():
                        st.markdown(f"### 📧 Emails pour {full_name}")
                        for i in range(4):
                            with st.expander(f"Email {i+1}: {email_json[i]['subject']}", expanded=(i == 0)):
                                st.markdown(f"**Objet:** {email_json[i]['subject']}")
                                st.text_area(
                                    "Message:", 
                                    value=email_json[i]['message'], 
                                    height=150, 
                                    key=f"email_{idx}_{i}",
                                    disabled=True
                                )

                    if idx % 10 == 9:
                        try:
                            with open(TEMP_FILE, "rb") as f:
                                st.download_button(
                                    "📅 Télécharger progression intermédiaire",
                                    data=f.read(),
                                    file_name=f"emails_progress_{idx+1}.csv",
                                    mime="text/csv",
                                    key=f"dl_{idx}"
                                )
                        except Exception as e:
                            st.warning(f"Erreur bouton téléchargement : {e}")

                    progress_bar.progress((idx + 1) / total)
                    req_used += 1

                    if req_used >= QUOTA_DAILY_REQ:
                        st.warning(f"Quota atteint ({QUOTA_DAILY_REQ}), arrêt automatique.")
                        break

                    time.sleep(0.2)

                # Finalisation
                status_text.text("✅ Génération terminée !")
                
                # Téléchargement final
                if result_df is not None and len(result_df) > 0:
                    csv = result_df.to_csv(index=False, sep=";").encode("utf-8")
                    st.download_button(
                        "📥 Télécharger le fichier final complet",
                        data=csv,
                        file_name=f"emails_silviomotion_{date.today().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    
                    # Nettoyer le fichier temporaire
                    try:
                        if os.path.exists(TEMP_FILE):
                            os.remove(TEMP_FILE)
                    except Exception as e:
                        st.warning(f"⚠️ Impossible de supprimer le fichier temporaire : {e}")

        finally:
            st.session_state.generating = False

# Affichage d'informations si pas de fichier
if uploaded_file is None:
    with col_output:
        st.info("👆 Uploadez un fichier CSV pour commencer la génération d'emails personnalisés.")
        st.markdown("""
        ### 📋 Instructions :
        1. **Clé API** : Entrez votre clé API Anthropic
        2. **Fichier CSV** : Uploadez votre export Sales Navigator 
        3. **Prompt** : Personnalisez le prompt ou utilisez un modèle sauvegardé
        4. **Génération** : Lancez la génération automatique
        
        ### 💡 Fonctionnalités :
        - ✅ **Prévisualisation en direct** - Testez vos prompts avant génération
        - ✅ **Statistiques d'utilisation** - Suivez vos performances et coûts
        - ✅ Reprise de session en cas d'interruption
        - ✅ Sauvegarde automatique des prompts
        - ✅ Téléchargement progressif des résultats
        - ✅ Gestion automatique du quota API
        - ✅ **Métriques temps réel** pendant la génération
        """)

# Onglet statistiques avancées dans la sidebar
with st.sidebar:
    st.markdown("### 📊 Statistiques détaillées")
    stats = load_stats()
    
    if stats["total_requests"] > 0:
        st.write(f"**Requêtes totales :** {stats['total_requests']}")
        st.write(f"**Succès :** {stats['successful_requests']}")
        st.write(f"**Échecs :** {stats['failed_requests']}")
        
        # Coût estimé total
        total_cost = sum([day_data.get("cost", 0) for day_data in stats["daily_usage"].values()])
        st.write(f"**Coût estimé :** ${total_cost:.3f}")
        
        # Graphique linéaire des derniers jours
        if len(stats["daily_usage"]) > 1:
            st.markdown("**Évolution (7 derniers jours) :**")
            last_days = dict(sorted(stats["daily_usage"].items())[-7:])
            chart_df = pd.DataFrame([
                {"Date": date_str, "Requêtes": data["requests"], "Coût": data.get("cost", 0)}
                for date_str, data in last_days.items()
            ])
            st.line_chart(chart_df.set_index("Date"))
    else:
        st.info("Aucune statistique disponible")
    
    # Bouton de reset des stats
    if st.button("🗑️ Reset statistiques"):
        if os.path.exists(STATS_FILE):
            os.remove(STATS_FILE)
            st.success("Stats réinitialisées !")
            st.rerun()
