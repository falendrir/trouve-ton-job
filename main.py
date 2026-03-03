import time
import hashlib
import concurrent.futures
from datetime import datetime

import streamlit as st
import pandas as pd
from jobspy import scrape_jobs

# ─── Configuration de la page ────────────────────────────────────────────────
st.set_page_config(page_title="Trouve ton job", page_icon="🎯", layout="wide")

# ─── Bandeau HTML/CSS ─────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    text-align: center;
">
    <h1 style="color: white; font-size: 2.5rem; margin: 0 0 0.5rem 0;">
        🎯 Trouve ton job !
    </h1>
    <p style="color: #a0aec0; font-size: 1.1rem; margin: 0;">
        Scrape Indeed, LinkedIn &amp; Glassdoor en quelques secondes
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
### Instructions
1. Sélectionnez les sites de recherche que vous souhaitez utiliser.
2. Renseignez le nom du travail que vous cherchez.
3. Choisissez la durée de publication des offres d'emploi (en heures).
4. Saisissez la ville et le pays où vous souhaitez trouver un emploi.
5. Cliquez sur **Scrape les jobs** pour lancer la recherche.
""")

# ─── Session state ─────────────────────────────────────────────────────────
if "search_history" not in st.session_state:
    st.session_state.search_history = []   # liste de dicts {params, results, timestamp}
if "current_jobs" not in st.session_state:
    st.session_state.current_jobs = pd.DataFrame()
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# ─── Cache helper ──────────────────────────────────────────────────────────
def make_cache_key(sites, job, ville, pays, hours, result):
    raw = f"{sorted(sites)}-{job}-{ville}-{pays}-{hours}-{result}"
    return hashlib.md5(raw.encode()).hexdigest()

@st.cache_data(ttl=3600, show_spinner=False)
def cached_scrape(cache_key, sites, job, ville, pays, hours, result):
    """Scrape chaque site en parallèle puis concatène."""
    def scrape_one(site):
        return scrape_jobs(
            site_name=[site],
            search_term=job,
            location=ville,
            hours_old=hours,
            country_indeed=pays,
            results_wanted=result,
        )

    frames = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(scrape_one, s): s for s in sites}
        for future in concurrent.futures.as_completed(futures):
            try:
                df = future.result()
                if not df.empty:
                    df["_source"] = futures[future]
                    frames.append(df)
            except Exception as e:
                st.warning(f"Erreur sur {futures[future]} : {e}")

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# ─── Sidebar ───────────────────────────────────────────────────────────────
site_options = ["Indeed", "LinkedIn", "Glassdoor"]

with st.sidebar:
    st.header("⚙️ Configuration")
    choice = st.multiselect(
        "📡 Diffusé sur :",
        site_options,
        default=["LinkedIn"],
        help="Sélectionnez les sites sur lesquels vous souhaitez rechercher des emplois.",
    )
    job    = st.text_input("🚀 Quel job cherches-tu ?",  key="job")
    ville  = st.text_input("📍 Ville",                   key="location")
    pays   = st.text_input("🏳️ Pays",                   key="pays", value="France")
    hours  = st.slider(
        "🕒 Publié depuis moins de (heures) :",
        min_value=1, max_value=168, value=48,
        help="Filtre les offres d'emploi selon leur date de publication.",
    )
    result = st.slider(
        "📊 Volume de résultats :",
        min_value=1, max_value=100, value=20,
        help="Limite le nombre d'offres par site.",
    )

    col1, col2 = st.columns(2)

    # ── Bouton Scrape ──────────────────────────────────────────────────────
    if col2.button("🔍 Scrape", use_container_width=True):
        if not choice:
            st.error("Sélectionne au moins un site.")
        elif not job.strip():
            st.error("Renseigne un intitulé de poste.")
        else:
            cache_key = make_cache_key(choice, job, ville, pays, hours, result)
            with st.spinner("Recherche en parallèle sur les plateformes… 🔍"):
                bar = st.progress(0)
                for pct in range(0, 60, 10):
                    time.sleep(0.15)
                    bar.progress(pct)
                try:
                    jobs_df = cached_scrape(cache_key, tuple(choice), job, ville, pays, hours, result)
                    bar.progress(100)
                    st.session_state.current_jobs = jobs_df
                    st.session_state.search_done  = True

                    # Sauvegarde dans l'historique (max 10 entrées)
                    st.session_state.search_history.insert(0, {
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "job": job, "ville": ville, "pays": pays,
                        "sites": ", ".join(choice),
                        "nb_results": len(jobs_df),
                        "data": jobs_df.copy(),
                    })
                    st.session_state.search_history = st.session_state.search_history[:10]
                except Exception as e:
                    st.error(f"Une erreur est survenue : {e}")

    # ── Bouton Reset ───────────────────────────────────────────────────────
    if col1.button("🔄 Reset", use_container_width=True):
        st.session_state.current_jobs = pd.DataFrame()
        st.session_state.search_done  = False
        st.rerun()

    # ── Historique ─────────────────────────────────────────────────────────
    if st.session_state.search_history:
        st.divider()
        st.subheader("🕘 Historique")
        for i, entry in enumerate(st.session_state.search_history):
            label = f"{entry['timestamp']} — {entry['job']} ({entry['nb_results']} résultats)"
            if st.button(label, key=f"hist_{i}", use_container_width=True):
                st.session_state.current_jobs = entry["data"]
                st.session_state.search_done  = True
                st.rerun()

# ─── Zone principale ───────────────────────────────────────────────────────
jobs = st.session_state.current_jobs

if not st.session_state.search_done:
    st.info("👈 Configure ta recherche dans la barre latérale puis clique sur **Scrape**.")

elif jobs.empty:
    st.warning("Aucun job trouvé avec ces critères. Essaie d'élargir la fenêtre de temps ou de changer les mots-clés.")

else:
    cols_to_show = [c for c in ["title", "company", "location", "date_posted", "job_url", "_source"] if c in jobs.columns]

    # ── Métriques ─────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 Jobs trouvés",        len(jobs))
    m2.metric("🏢 Entreprises uniques", jobs["company"].nunique()  if "company"  in jobs.columns else "—")
    m3.metric("📍 Villes uniques",      jobs["location"].nunique() if "location" in jobs.columns else "—")
    pct_url = int(jobs["job_url"].notna().mean() * 100) if "job_url" in jobs.columns else 0
    m4.metric("🔗 Avec lien direct",    f"{pct_url} %")

    # Répartition par source
    if "_source" in jobs.columns:
        st.markdown("**Répartition par site :**  " +
            "  |  ".join(f"**{s}** : {n}" for s, n in jobs["_source"].value_counts().items()))

    st.divider()

    # ── Filtres inline ─────────────────────────────────────────────────────
    with st.expander("🔎 Filtres sur les résultats", expanded=False):
        fc1, fc2 = st.columns(2)
        kw_include = fc1.text_input("Inclure (mot-clé dans le titre)", "")
        kw_exclude = fc2.text_input("Exclure (mot-clé dans le titre)", "")

    filtered = jobs.copy()
    if kw_include and "title" in filtered.columns:
        filtered = filtered[filtered["title"].str.contains(kw_include, case=False, na=False)]
    if kw_exclude and "title" in filtered.columns:
        filtered = filtered[~filtered["title"].str.contains(kw_exclude, case=False, na=False)]

    st.subheader(f"📋 {len(filtered)} offres affichées")

    # ── Tableau avec URLs cliquables ───────────────────────────────────────
    display_df = filtered[cols_to_show].copy()
    if "job_url" in display_df.columns:
        display_df["job_url"] = display_df["job_url"].apply(
            lambda url: f'<a href="{url}" target="_blank">🔗 Voir l\'offre</a>' if pd.notna(url) and url else ""
        )
        st.write(
            display_df.to_html(escape=False, index=False),
            unsafe_allow_html=True,
        )
    else:
        st.dataframe(display_df, use_container_width=True)

    # ── Export CSV ─────────────────────────────────────────────────────────
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Télécharger les résultats (CSV)",
        data=csv,
        file_name=f"jobs_{job}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )