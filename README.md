<div align="center">

# 🎬 CineMatch
### AI-Powered Movie & Series Recommendation System

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![IMDb](https://img.shields.io/badge/IMDb-F5C518?style=for-the-badge&logo=imdb&logoColor=black)](https://imdb.com)

*Discover your next favourite watch — powered by TF-IDF & Cosine Similarity*

---

![CineMatch Banner](https://img.shields.io/badge/🎬%20CineMatch-Netflix%20Dark%20Theme-E50914?style=for-the-badge)

</div>

---

## 📌 Table of Contents

- [About](#-about)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Dataset](#-dataset)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Test Cases](#-test-cases)
- [Deployment](#-deployment)

---

## 🎯 About

**CineMatch** is a content-based movie and web series recommendation system built with a Netflix-inspired dark UI. Search for any title and instantly get intelligent recommendations based on genre, theme, era, rating tier, director, and cast — not just popularity.

> Built as a **Data Mining Project** using TF-IDF vectorization and Cosine Similarity on 20,000 IMDb titles.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Smart Search** | Substring matching with "Did you mean?" suggestions |
| 🎬 **Source Card** | Full details of your searched title — rating, cast, director, IMDb link |
| 🃏 **Recommendation Cards** | Top N results with genre tags, similarity %, rating bars |
| 📊 **Similarity Chart** | Interactive Plotly bar chart showing cosine similarity scores |
| 🎛️ **Filters** | Filter by content type — Movie, TV Series, Mini Series, TV Movie |
| 🕐 **Will Be Added Soon** | Graceful screen when a title isn't in the library |
| 🌑 **Netflix Dark Theme** | Full Netflix-style UI with red accents and dark backgrounds |
| ⚡ **Auto Model Build** | Model builds automatically on first run — no manual setup needed |

---

## 🧠 How It Works

CineMatch uses a **hybrid weighted TF-IDF + Cosine Similarity** approach:

```
Search Query
     │
     ▼
┌─────────────────────────────────────┐
│         Substring Matching          │
│   Finds all titles containing query │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│       Feature Soup (Weighted)       │
│                                     │
│  Inferred Subgenre  ████████ 4x     │
│  Genre Tags         ██████████ 5x   │
│  Content Type       ██████ 3x       │
│  Decade Bucket      ████ 2x         │
│  Rating Tier        ████ 2x         │
│  Director           ██ 1x           │
│  Lead Actor         ██ 1x           │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│    TF-IDF Vectorization             │
│    20,000 features, bigrams         │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│    Cosine Similarity                │
│    Ranked Top-N Results             │
└─────────────────────────────────────┘
     │
     ▼
   Results + Similarity Chart
```

### Why Subgenre Inference?

The IMDb dataset uses broad genre tags — `Action, Adventure, Drama` is shared by **Game of Thrones**, **Star Trek**, and **Mahabharat**. To fix this, CineMatch infers thematic subgenres from title text:

| Subgenre Token | Trigger Keywords |
|---|---|
| `medieval_fantasy` | dragon, throne, knight, viking, witch, magic... |
| `scifi_space` | space, galaxy, alien, robot, future... |
| `crime_thriller` | heist, murder, detective, cop, mafia... |
| `superhero` | avenger, batman, spider, marvel... |
| `horror` | zombie, demon, haunted, vampire... |

This ensures **Game of Thrones → House of the Dragon, Vikings** rather than random action shows.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Frontend** | Streamlit + Custom CSS (Netflix Theme) |
| **ML Model** | scikit-learn TF-IDF + Cosine Similarity |
| **Visualisation** | Plotly interactive bar charts |
| **Data Processing** | Pandas, NumPy |
| **Model Storage** | Python Pickle |
| **Language** | Python 3.9+ |

---

## 📊 Dataset

- **Source:** IMDb Top 20,000 Titles
- **Size:** 20,000 titles
- **Fields:** `title`, `year`, `type`, `genre`, `rating`, `votes`, `director`, `cast`, `runtime`, `imdb_url`

| Content Type | Count |
|---|---|
| 🎬 Movies | 15,978 |
| 📺 TV Series | 3,110 |
| 📽️ Mini Series | 637 |
| 🎥 TV Movies | 275 |
| **Total** | **20,000** |

**Rating range:** 1.0 ⭐ to 9.6 ⭐

---

## 📁 Project Structure

```
CINEMATCH/
│
├── app.py                  # Streamlit UI — Netflix dark theme
├── movie_analysis.py                  # Recommendation engine — TF-IDF model
├── imdb_dataset.csv        # IMDb dataset (20,000 titles)
├── requirements.txt        # Python dependencies
└── README.md               # You are here
```

> `recommendation_model.pkl` is auto-generated on first run and not committed to the repo.

---

## ⚙️ Installation

**1. Clone the repository:**
```bash
git clone https://github.com/Lakshya438/CINEMATCH.git
cd CINEMATCH
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Build the model (first time only):**
```bash
python movie_analysis.py
```

**4. Run the app:**
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` 🎉

---

## 🚀 Usage

1. **Type** any movie or series name in the search bar
2. **Click** a suggestion from the "Did you mean?" list if multiple matches appear
3. **View** the source card with full details of your searched title
4. **Browse** the recommendation cards below
5. **Analyse** the cosine similarity chart to understand match strength
6. **Filter** by content type using the sidebar
7. **Adjust** the number of recommendations (5–20) using the slider

### Quick Search Examples

| Search | What You Get |
|---|---|
| `Game of Thrones` | House of the Dragon, Vikings, The Last Kingdom |
| `Breaking Bad` | Better Call Saul, Ozark, Narcos |
| `Inception` | Interstellar, The Matrix, Tenet |
| `Stranger Things` | Dark, The OA, Haunting of Hill House |
| `Parasite` | Memories of Murder, Oldboy, The Host |

---

## 🧪 Test Cases

| ID | Query | Expected Output |
|---|---|---|
| TC-01 | `Game of Thrones` | Medieval fantasy series — House of Dragon, Vikings |
| TC-02 | `Inception` | Sci-Fi/Action movies — Mad Max, Pacific Rim |
| TC-03 | `Breaking Bad` | Crime drama series — 9.5/10 rating shown |
| TC-04 | `Asur` | "Did you mean?" → Asur, Asuran, Devasuram |
| TC-05 | `Avengers` | MCU superhero cluster |
| TC-06 | `xyznonexistent` | 🕐 "Will Be Added Soon" screen |
| TC-07 | `The Dark Knight` + Movie filter | Only movies — 96% match for Dark Knight Rises |
| TC-08 | `Stranger Things` + TV Series filter | Only TV series — horror/supernatural cluster |

---

## 🌐 Deployment

Deployed on **Streamlit Community Cloud** — free hosting.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://lakshya438-cinematch.streamlit.app)

**To deploy your own:**
1. Fork this repo
2. Go to [Website](https://cineematch.streamlit.app/)
3. Connect your GitHub and select this repo
4. Set main file as `app.py`
5. Click Deploy!

---

## 👨‍💻 Author

**Lakshya**
- GitHub: [@Lakshya438](https://github.com/Lakshya438)

---

## 📄 License

This project is for educational purposes as part of a Data Mining course project.

---

<div align="center">

Made with ❤️ and 🎬 | Data Mining Project 2026

⭐ Star this repo if you found it useful!

</div>
