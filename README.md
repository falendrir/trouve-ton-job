# 🎯 Trouve ton Job !

Une application web interactive développée avec **Streamlit** pour scraper des offres d'emploi sur **Indeed**, **LinkedIn** et **Glassdoor** en quelques secondes.

---

## 📸 Aperçu

> Scrape plusieurs plateformes simultanément, filtre les résultats, consulte ton historique de recherche et exporte en CSV.

---

## ✨ Fonctionnalités

- 🔍 **Multi-sources** : scraping en parallèle sur Indeed, LinkedIn et Glassdoor
- ⚡ **Recherche rapide** : exécution concurrente avec `ThreadPoolExecutor`
- 💾 **Cache intelligent** : résultats mis en cache 1 heure (évite les requêtes redondantes)
- 🕘 **Historique** : conservation des 10 dernières recherches avec rechargement en un clic
- 🔎 **Filtres dynamiques** : inclusion/exclusion par mot-clé dans les titres
- 📊 **Métriques** : nombre de jobs, entreprises uniques, villes, % avec lien direct
- 🔗 **Liens cliquables** : accès direct aux offres depuis le tableau
- 📥 **Export CSV** : téléchargement des résultats filtrés

---

## 🛠️ Stack technique

| Composant | Technologie |
|-----------|-------------|
| Interface | [Streamlit](https://streamlit.io/) |
| Scraping | [JobSpy](https://github.com/Bunsly/JobSpy) |
| Data | [Pandas](https://pandas.pydata.org/) |
| Parallélisme | `concurrent.futures` |
| Cache | `st.cache_data` (TTL 1h) |

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/falendrir/trouve-ton-job.git
cd trouve-ton-job
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement sur [http://localhost:8501](http://localhost:8501).

---

## 📦 Dépendances (`requirements.txt`)

```
streamlit
pandas
jobspy
```

---

## 📖 Utilisation

1. **Sélectionner les sites** : choisir parmi Indeed, LinkedIn, Glassdoor
2. **Saisir le poste** : ex. `Data Analyst`, `Développeur Python`
3. **Définir la localisation** : ville + pays (ex. `Paris`, `France`)
4. **Régler les filtres** :
   - Délai de publication (1 à 168 heures)
   - Volume de résultats par site (1 à 100)
5. **Cliquer sur 🔍 Scrape** et consulter les résultats
6. **Filtrer** les offres par mots-clés
7. **Exporter** en CSV si besoin

---

## 📁 Structure du projet

```
trouve-ton-job/
│
├── app.py               # Application principale Streamlit
├── requirements.txt     # Dépendances Python
└── README.md            # Documentation
```

---

## ⚠️ Limitations connues

- Le scraping de LinkedIn peut être limité par des mécanismes anti-bot
- Les résultats dépendent de la disponibilité des plateformes tierces
- Le cache est local à la session Streamlit (réinitialisé au redémarrage)

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour proposer une amélioration :

1. Fork le projet
2. Crée une branche (`git checkout -b feature/ma-feature`)
3. Commit tes changements (`git commit -m 'feat: ajout de ma feature'`)
4. Push la branche (`git push origin feature/ma-feature`)
5. Ouvre une Pull Request

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**. Voir le fichier `LICENSE` pour plus de détails.

---

> Fait avec ❤️ et Streamlit
