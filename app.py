"""
app.py — Movie & Web Series Recommendation App  (Netflix Dark Theme)
Run:  streamlit run app.py
"""

import pickle
import re
import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch – Find Your Next Watch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Netflix-style CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Netflix+Sans:wght@400;700&family=Barlow:ital,wght@0,300;0,400;0,600;0,700;1,300&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #141414 !important;
    color: #e5e5e5 !important;
    font-family: 'Barlow', 'Helvetica Neue', Arial, sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding-top: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #000 !important;
    border-right: 1px solid #2a2a2a !important;
}
[data-testid="stSidebar"] * { color: #e5e5e5 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label { color: #aaa !important; font-size: 0.82rem !important; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #1f1f1f !important;
    border: 1px solid #333 !important;
    border-radius: 4px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span { color: #e5e5e5 !important; }
[data-testid="stSidebar"] .stSlider [data-testid="stSlider"] div div div div {
    background: #e50914 !important;
}

/* Sidebar metrics */
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: #1a1a1a !important;
    border-radius: 6px !important;
    border: 1px solid #2a2a2a !important;
    padding: 0.6rem 0.8rem !important;
    margin-bottom: 0.4rem !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #e50914 !important; font-size: 1.3rem !important; }
[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color: #999 !important; font-size: 0.72rem !important; }

/* ── Netflix Hero Banner ── */
.nf-hero {
    position: relative;
    background: linear-gradient(180deg,
        rgba(20,20,20,0) 0%,
        rgba(20,20,20,0.4) 40%,
        rgba(20,20,20,0.95) 85%,
        #141414 100%),
        linear-gradient(90deg, #1a0000 0%, #141414 60%);
    padding: 3.5rem 3rem 2.5rem;
    margin: -1rem -1rem 0 -1rem;
    border-bottom: 3px solid #e50914;
    overflow: hidden;
}
.nf-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 80% 60% at 80% 50%,
        rgba(229,9,20,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.nf-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.8rem;
    letter-spacing: 0.04em;
    color: #e50914;
    line-height: 1;
    text-shadow: 0 2px 30px rgba(229,9,20,0.5);
    margin: 0 0 0.2rem;
}
.nf-logo span { color: #fff; }
.nf-tagline {
    font-family: 'Barlow', sans-serif;
    font-size: 1rem;
    font-weight: 300;
    color: #aaa;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0;
}
.nf-stats-row {
    display: flex;
    gap: 2rem;
    margin-top: 1.5rem;
}
.nf-stat {
    text-align: center;
}
.nf-stat-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    color: #e50914;
    line-height: 1;
}
.nf-stat-label {
    font-size: 0.7rem;
    color: #777;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Search box ── */
.stTextInput > div > div > input {
    background: #1f1f1f !important;
    border: 2px solid #333 !important;
    border-radius: 4px !important;
    color: #fff !important;
    caret-color: #e50914 !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #e50914 !important;
    box-shadow: 0 0 0 2px rgba(229,9,20,0.15) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #555 !important; }

/* ── Section labels ── */
.nf-section-label {
    font-family: 'Barlow', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #777;
    margin: 0 0 0.6rem;
}

/* ── Quick pick & suggestion buttons ── */
.stButton > button {
    background: #1f1f1f !important;
    border: 1px solid #333 !important;
    color: #ccc !important;
    border-radius: 3px !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    padding: 0.35rem 0.6rem !important;
    transition: all 0.15s !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-align: left !important;
}
.stButton > button:hover {
    background: #e50914 !important;
    border-color: #e50914 !important;
    color: #fff !important;
    transform: translateY(-1px) !important;
}
/* suggestion buttons — slightly taller with left-align */
[data-testid="stHorizontalBlock"] .stButton > button {
    padding: 0.55rem 0.75rem !important;
    font-size: 0.78rem !important;
    white-space: normal !important;
    height: auto !important;
    line-height: 1.35 !important;
}

/* ── Searched title detail card ── */
.nf-source-detail {
    border: 1px solid #3a1a1a;
    border-left: 5px solid #e50914;
    border-radius: 8px;
    margin-bottom: 1.2rem;
    overflow: hidden;
}
.nf-source-detail-inner {
    padding: 1.3rem 1.6rem;
    background: linear-gradient(135deg, #1a0a0a 0%, #1a1a1a 100%);
}
.src-eyebrow {
    font-size: 0.62rem;
    color: #e50914;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-weight: 700;
    margin-bottom: 0.4rem;
}
.src-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: #fff;
    letter-spacing: 0.05em;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}
.src-sub {
    font-size: 0.8rem;
    color: #777;
    margin-bottom: 0.5rem;
}

/* ── Source title banner ── */
.nf-source-banner {
    background: linear-gradient(90deg, rgba(229,9,20,0.15) 0%, transparent 100%);
    border-left: 4px solid #e50914;
    padding: 0.8rem 1.2rem;
    border-radius: 0 6px 6px 0;
    margin: 1.2rem 0;
}
.nf-source-banner .label { font-size: 0.7rem; color: #aaa; text-transform: uppercase; letter-spacing: 0.1em; }
.nf-source-banner .title { font-family: 'Bebas Neue', sans-serif; font-size: 1.7rem; color: #fff; letter-spacing: 0.05em; line-height: 1.1; }

/* ── Metric row ── */
[data-testid="stMetric"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="stMetricValue"] {
    color: #e50914 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.8rem !important;
}
[data-testid="stMetricLabel"] { color: #888 !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.08em; }

/* ── Movie Cards ── */
.nf-card {
    background: #1a1a1a;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 0.9rem;
    border: 1px solid #2a2a2a;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    position: relative;
}
.nf-card:hover {
    transform: scale(1.02);
    border-color: #e50914;
    box-shadow: 0 8px 32px rgba(229,9,20,0.2), 0 2px 8px rgba(0,0,0,0.6);
    z-index: 10;
}
.nf-card-accent {
    height: 3px;
    background: linear-gradient(90deg, #e50914, #ff6b35);
}
.nf-card-body { padding: 1rem 1.1rem 0.9rem; }
.nf-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
}
.nf-card-rank {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem;
    color: #333;
    line-height: 1;
    margin-right: 0.5rem;
    min-width: 2rem;
    flex-shrink: 0;
}
.nf-card-title-block { flex: 1; }
.nf-card-title {
    font-family: 'Barlow', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #fff;
    line-height: 1.2;
    margin: 0 0 0.15rem;
}
.nf-card-year {
    font-size: 0.78rem;
    color: #777;
    font-weight: 300;
}
.nf-match-badge {
    background: #e50914;
    color: #fff;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 0.2rem 0.55rem;
    border-radius: 3px;
    flex-shrink: 0;
    align-self: flex-start;
}
.nf-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    margin: 0.5rem 0;
}
.nf-tag {
    background: #2a2a2a;
    border: 1px solid #383838;
    color: #bbb;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
}
.nf-tag-type { background: rgba(229,9,20,0.12); border-color: rgba(229,9,20,0.3); color: #ff6b6b; }
.nf-rating-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin: 0.4rem 0;
}
.nf-imdb-badge {
    background: #f5c518;
    color: #000;
    font-size: 0.65rem;
    font-weight: 800;
    padding: 0.1rem 0.4rem;
    border-radius: 2px;
}
.nf-rating-num { color: #f5c518; font-weight: 700; font-size: 0.9rem; }
.nf-rating-sep { color: #444; font-size: 0.75rem; }
.nf-votes { color: #666; font-size: 0.75rem; }
.nf-meta { color: #777; font-size: 0.78rem; margin: 0.25rem 0; line-height: 1.4; }
.nf-meta b { color: #aaa; font-weight: 600; }
.nf-imdb-link {
    display: inline-block;
    margin-top: 0.55rem;
    color: #e50914;
    font-size: 0.78rem;
    font-weight: 600;
    text-decoration: none;
    letter-spacing: 0.04em;
    border-bottom: 1px solid transparent;
    transition: border-color 0.15s;
}
.nf-imdb-link:hover { border-bottom-color: #e50914; }

/* ── Featured hero cards (landing) ── */
.nf-featured-card {
    background: linear-gradient(180deg, #1f1f1f 0%, #141414 100%);
    border: 1px solid #2a2a2a;
    border-top: 3px solid #e50914;
    border-radius: 6px;
    padding: 1.1rem;
    margin-bottom: 0.8rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
.nf-featured-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(229,9,20,0.18);
}
.nf-featured-title { font-size: 0.95rem; font-weight: 700; color: #fff; margin: 0 0 0.3rem; }
.nf-featured-year  { font-size: 0.75rem; color: #777; }
.nf-featured-genre { font-size: 0.75rem; color: #aaa; margin: 0.3rem 0; }

/* ── Divider ── */
hr { border: none; border-top: 1px solid #2a2a2a !important; margin: 1.2rem 0 !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 4px !important;
    color: #ccc !important;
}

/* ── Spinner text ── */
.stSpinner p { color: #aaa !important; }

/* scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0d0d; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #e50914; }
</style>
""", unsafe_allow_html=True)


# ── Load model ────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading recommendation engine…")
def load_model(path: str = "recommendation_model.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)

try:
    payload      = load_model()
    df           = payload["df"]
    tfidf_matrix = payload["tfidf_matrix"]
except FileNotFoundError:
    st.error("❌  `recommendation_model.pkl` not found. Run `python mrs.py` first.")
    st.stop()


# ── Helpers ───────────────────────────────────────────────────────────────────
from sklearn.metrics.pairwise import cosine_similarity

def get_matches(query: str):
    """Return all titles that contain the query string, sorted by rating desc."""
    query_lower = query.lower().strip()
    if not query_lower:
        return pd.DataFrame()
    # Exact match first, then substring
    exact = df[df["title_lower"] == query_lower]
    substr = df[df["title_lower"].str.contains(re.escape(query_lower), regex=True)]
    combined = pd.concat([exact, substr]).drop_duplicates()
    return combined.sort_values("rating", ascending=False)[
        ["title", "year", "type", "genre", "rating"]
    ].reset_index(drop=True)


def get_recommendations(query, top_n=10, type_filter=None):
    query_lower = query.lower().strip()
    exact = df[df["title_lower"] == query_lower]
    if not exact.empty:
        idx = exact["rating"].idxmax()
    else:
        mask = df["title_lower"].str.contains(re.escape(query_lower), regex=True)
        matches = df[mask]
        if matches.empty:
            return pd.DataFrame(), None, None
        idx = matches["rating"].idxmax()

    source_title  = df.loc[idx, "title"]
    source_rating = df.loc[idx, "rating"]
    sim_scores    = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    sim_series    = pd.Series(sim_scores, index=df.index).drop(idx)

    working = df.copy()
    working["similarity"] = sim_series
    working = working.drop(idx)

    if type_filter and type_filter != "All":
        working = working[working["type"] == type_filter]

    working = working.nlargest(top_n, "similarity")
    return working.reset_index(drop=True), source_title, source_rating


def rating_bar(rating):
    """Return coloured rating bar HTML (out of 10)."""
    pct = int(rating * 10)
    colour = "#e50914" if rating < 5 else "#f5c518" if rating < 7.5 else "#46d369"
    return (
        f'<div style="display:inline-block;width:60px;height:5px;'
        f'background:#2a2a2a;border-radius:3px;vertical-align:middle;margin:0 6px">'
        f'<div style="width:{pct}%;height:100%;background:{colour};border-radius:3px"></div>'
        f'</div>'
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;
                    color:#e50914;letter-spacing:0.06em;line-height:1">
            CINE<span style="color:#fff">MATCH</span>
        </div>
        <div style="font-size:0.65rem;color:#555;letter-spacing:0.12em;
                    text-transform:uppercase;margin-top:2px">
            AI Recommendation Engine
        </div>
    </div>
    <hr style="border-color:#222;margin:0.8rem 0">
    """, unsafe_allow_html=True)

    st.markdown('<div class="nf-section-label">Content Type</div>', unsafe_allow_html=True)
    type_filter = st.selectbox("", ["All", "Movie", "TV Series", "Mini Series", "TV Movie"], label_visibility="collapsed")

    st.markdown('<div class="nf-section-label" style="margin-top:1rem">Results Count</div>', unsafe_allow_html=True)
    top_n = st.slider("", 5, 20, 10, label_visibility="collapsed")

    st.markdown('<hr style="border-color:#222;margin:1rem 0">', unsafe_allow_html=True)
    st.markdown('<div class="nf-section-label">Library Stats</div>', unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    s1.metric("Total", f"{len(df):,}")
    s2.metric("Movies", f"{(df['type']=='Movie').sum():,}")
    s3, s4 = st.columns(2)
    s3.metric("TV Series", f"{(df['type']=='TV Series').sum():,}")
    s4.metric("Mini Series", f"{(df['type']=='Mini Series').sum():,}")

    st.markdown("""
    <div style="margin-top:1.5rem;font-size:0.68rem;color:#444;
                text-transform:uppercase;letter-spacing:0.08em;text-align:center">
        Source: IMDb Top-20,000 Dataset
    </div>
    """, unsafe_allow_html=True)


# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="nf-hero">
    <div class="nf-logo">CINE<span>MATCH</span></div>
    <p class="nf-tagline">AI-powered movie &amp; series recommendations · 20,000 titles</p>
</div>
""", unsafe_allow_html=True)


# ── Search bar ────────────────────────────────────────────────────────────────
st.markdown('<div class="nf-section-label" style="margin-top:1.5rem">Search Title</div>', unsafe_allow_html=True)
query = st.text_input("", placeholder="Search for a movie or series…  e.g. Game of Thrones, Inception, Breaking Bad",
                      label_visibility="collapsed")

# Quick picks
st.markdown('<div class="nf-section-label" style="margin-top:0.8rem">Trending Searches</div>', unsafe_allow_html=True)
quick  = ["Inception", "Breaking Bad", "Game of Thrones", "Interstellar", "The Dark Knight", "Stranger Things", "Parasite", "Dark"]
cols   = st.columns(len(quick))
for col, title in zip(cols, quick):
    if col.button(title, use_container_width=True):
        query = title

st.markdown("<hr>", unsafe_allow_html=True)


# ── Results ───────────────────────────────────────────────────────────────────
if query:
    # ── Step 1: find all matching titles and show as suggestions ──────────────
    matches = get_matches(query)
    exact_hit = not matches.empty and matches.iloc[0]["title"].lower() == query.lower()

    if not matches.empty and not exact_hit:
        st.markdown('<div class="nf-section-label" style="margin-top:0.5rem">Did you mean?</div>', unsafe_allow_html=True)
        # Show up to 8 suggestions as clickable cards
        n_cols = min(len(matches), 4)
        rows_needed = (min(len(matches), 8) + n_cols - 1) // n_cols
        match_subset = matches.head(8)
        for row_i in range(rows_needed):
            row_matches = match_subset.iloc[row_i*n_cols : row_i*n_cols + n_cols]
            btn_cols = st.columns(n_cols)
            for col, (_, mrow) in zip(btn_cols, row_matches.iterrows()):
                label = f"{mrow['title']} ({int(mrow['year'])})"
                badge = "🎬" if mrow["type"] == "Movie" else "📺"
                if col.button(f"{badge} {label}", use_container_width=True, key=f"sug_{mrow['title']}"):
                    query = mrow["title"]
                    exact_hit = True
        st.markdown("<hr>", unsafe_allow_html=True)

    # ── Step 2: show recommendations for the selected/exact title ─────────────
    with st.spinner("Scanning the library…"):
        recs, source_title, source_rating = get_recommendations(query, top_n=top_n, type_filter=type_filter)

    if recs is None or recs.empty:
        st.markdown(f"""
        <div style="text-align:center;padding:3.5rem 2rem;background:#1a1a1a;
                    border-radius:10px;border:1px solid #2a2a2a;margin:1.5rem 0;">
            <div style="font-size:3.5rem;margin-bottom:1rem">&#127909;</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                        color:#fff;letter-spacing:0.06em;margin-bottom:0.8rem">
                {query.upper()}
            </div>
            <div style="display:inline-block;background:#e50914;color:#fff;
                        font-size:0.72rem;font-weight:700;letter-spacing:0.14em;
                        text-transform:uppercase;padding:0.35rem 1.1rem;
                        border-radius:3px;margin-bottom:1rem">
                &#128336;&nbsp; Will Be Added Soon
            </div>
            <div style="color:#666;font-size:0.88rem;max-width:360px;
                        margin:0.8rem auto 0;line-height:1.6;">
                This title is not in our library yet.<br>
                We are constantly expanding &mdash; check back soon!
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Searched title full detail card ───────────────────────────────────
        src_row = df[df["title_lower"] == source_title.lower()]
        if src_row.empty:
            src_row = df[df["title_lower"].str.contains(re.escape(source_title.lower()), regex=True)]
        src = src_row.iloc[0] if not src_row.empty else None

        if src is not None:
            src_genres = "".join(
                f'<span class="nf-tag">{g.strip()}</span>'
                for g in str(src["genre"]).split(",") if g.strip()
            )
            src_cast  = "; ".join(str(src["cast"]).split(";")[:3])
            src_votes = f"{int(src['votes_clean']):,}" if src["votes_clean"] > 0 else "—"
            src_rating_bar = rating_bar(src["rating"])
            st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a0a0a 0%,#1a1a1a 100%);"
     class="nf-source-detail">
  <div class="nf-source-detail-inner">
    <div class="src-eyebrow">&#9654;&nbsp; Searching based on</div>
    <div class="src-title">{src["title"]}</div>
    <div class="src-sub">{int(src["year"])} &nbsp;&middot;&nbsp; {src["type"]} &nbsp;&middot;&nbsp; {src["runtime"] or "&mdash;"}</div>
    <div class="nf-tags" style="margin:0.5rem 0;">
      <span class="nf-tag nf-tag-type">{src["type"]}</span>
      {src_genres}
    </div>
    <div class="nf-rating-row">
      <span class="nf-imdb-badge">IMDb</span>
      <span class="nf-rating-num">{src["rating"]}</span>
      {src_rating_bar}
      <span class="nf-votes">{src_votes} votes</span>
    </div>
    <div class="nf-meta" style="margin-top:0.5rem;">&#127909; <b>Director:</b> {src["director"] or "&mdash;"}</div>
    <div class="nf-meta">&#127917; <b>Cast:</b> {src_cast or "&mdash;"}</div>
    <a class="nf-imdb-link" href="{src["imdb_url"]}" target="_blank"
       style="display:inline-block;margin-top:0.6rem;font-size:0.8rem;">
      VIEW ON IMDb &nbsp;&#8250;
    </a>
  </div>
</div>
""", unsafe_allow_html=True)

        # Metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Matches Found", len(recs))
        m2.metric("IMDb Rating", f"{source_rating} / 10")
        m3.metric("Top Match", f"{recs['similarity'].iloc[0]*100:.0f}%")
        movies_n = (recs["type"] == "Movie").sum()
        series_n = len(recs) - movies_n
        m4.metric("Movies / Series", f"{movies_n} / {series_n}")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f'<div class="nf-section-label">Top {len(recs)} Recommendations</div>', unsafe_allow_html=True)

        # Two-column card grid
        left_col, right_col = st.columns(2)
        for i, row in recs.iterrows():
            col = left_col if i % 2 == 0 else right_col
            match_pct  = f"{row['similarity']*100:.0f}%"
            votes_fmt  = f"{row['votes_clean']:,}" if row['votes_clean'] > 0 else "—"
            cast_short = "; ".join(str(row["cast"]).split(";")[:2])
            genre_tags = "".join(
                f'<span class="nf-tag">{g.strip()}</span>'
                for g in str(row["genre"]).split(",") if g.strip()
            )
            col.markdown(f"""
<div class="nf-card">
  <div class="nf-card-accent"></div>
  <div class="nf-card-body">
    <div class="nf-card-top">
      <span class="nf-card-rank">#{i+1:02d}</span>
      <div class="nf-card-title-block">
        <div class="nf-card-title">{row['title']}</div>
        <div class="nf-card-year">{int(row['year'])} &nbsp;·&nbsp; {row['runtime'] or '—'}</div>
      </div>
      <span class="nf-match-badge">{match_pct}</span>
    </div>
    <div class="nf-tags">
      <span class="nf-tag nf-tag-type">{row['type']}</span>
      {genre_tags}
    </div>
    <div class="nf-rating-row">
      <span class="nf-imdb-badge">IMDb</span>
      <span class="nf-rating-num">{row['rating']}</span>
      {rating_bar(row['rating'])}
      <span class="nf-rating-sep">·</span>
      <span class="nf-votes">{votes_fmt} votes</span>
    </div>
    <div class="nf-meta">🎬 <b>Dir:</b> {row['director'] or '—'}</div>
    <div class="nf-meta">🎭 <b>Cast:</b> {cast_short or '—'}</div>
    <a class="nf-imdb-link" href="{row['imdb_url']}" target="_blank">
      VIEW ON IMDb &nbsp;›
    </a>
  </div>
</div>
""", unsafe_allow_html=True)


        # ── Cosine Similarity Chart ───────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="nf-section-label">📊 Cosine Similarity Analysis</div>', unsafe_allow_html=True)

        avg_sim = recs["similarity"].mean() * 100
        max_sim = recs["similarity"].max()  * 100
        min_sim = recs["similarity"].min()  * 100

        st.markdown(f"""
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-left:4px solid #e50914;
            border-radius:0 8px 8px 0;padding:1rem 1.4rem;margin-bottom:1rem;">
  <div style="display:flex;flex-wrap:wrap;gap:2rem;align-items:flex-start">
    <div>
      <div style="font-size:0.62rem;color:#777;text-transform:uppercase;letter-spacing:0.1em">How it works</div>
      <div style="font-size:0.84rem;color:#ccc;margin-top:0.3rem;max-width:520px;line-height:1.6">
        Cosine similarity measures the angle between two title vectors in TF-IDF space.
        <b style="color:#fff">100%</b> = identical feature vectors. <b style="color:#fff">0%</b> = no overlap.
        All shown results scored above <b style="color:#e50914">{min_sim:.1f}%</b>.
      </div>
    </div>
    <div style="display:flex;gap:1.5rem;flex-wrap:wrap">
      <div style="text-align:center">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:#e50914">{max_sim:.1f}%</div>
        <div style="font-size:0.65rem;color:#777;text-transform:uppercase;letter-spacing:0.08em">Highest Match</div>
      </div>
      <div style="text-align:center">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:#f5c518">{avg_sim:.1f}%</div>
        <div style="font-size:0.65rem;color:#777;text-transform:uppercase;letter-spacing:0.08em">Average Match</div>
      </div>
      <div style="text-align:center">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:#aaa">{min_sim:.1f}%</div>
        <div style="font-size:0.65rem;color:#777;text-transform:uppercase;letter-spacing:0.08em">Lowest Match</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        import plotly.graph_objects as go

        titles_short = [t if len(t) <= 28 else t[:26] + "\u2026" for t in recs["title"].tolist()]
        sims_pct     = (recs["similarity"] * 100).round(1).tolist()
        bar_colors   = ["#46d369" if s >= 70 else "#f5c518" if s >= 55 else "#e50914" for s in sims_pct]

        fig = go.Figure()
        fig.add_hline(
            y=avg_sim, line_dash="dot", line_color="#f5c518", line_width=1.5,
            annotation_text=f"Avg {avg_sim:.1f}%",
            annotation_position="top right",
            annotation_font=dict(color="#f5c518", size=11),
        )
        fig.add_trace(go.Bar(
            x=titles_short,
            y=sims_pct,
            marker_color=bar_colors,
            marker_line_color="rgba(0,0,0,0)",
            text=[f"{s:.1f}%" for s in sims_pct],
            textposition="outside",
            textfont=dict(color="#ccc", size=11, family="Arial"),
            hovertemplate="<b>%{x}</b><br>Cosine Similarity: %{y:.1f}%<extra></extra>",
        ))
        fig.update_layout(
            plot_bgcolor="#141414",
            paper_bgcolor="#141414",
            font=dict(color="#e5e5e5", family="Arial"),
            title=dict(
                text=f"Cosine Similarity — Recommendations for <b>{source_title}</b>",
                font=dict(size=14, color="#fff"),
                x=0,
            ),
            xaxis=dict(tickfont=dict(size=10, color="#aaa"), tickangle=-30, showgrid=False, linecolor="#2a2a2a"),
            yaxis=dict(
                title=dict(text="Cosine Similarity (%)", font=dict(size=11, color="#888")),
                tickfont=dict(size=10, color="#aaa"),
                gridcolor="#2a2a2a",
                range=[0, min(max_sim + 12, 105)],
                ticksuffix="%",
            ),
            margin=dict(t=50, b=80, l=60, r=30),
            height=380,
            bargap=0.25,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
<div style="display:flex;gap:1.2rem;margin-top:-0.5rem;padding:0.5rem 0;flex-wrap:wrap">
  <div style="display:flex;align-items:center;gap:6px">
    <div style="width:14px;height:14px;background:#46d369;border-radius:2px"></div>
    <span style="font-size:0.75rem;color:#aaa">Strong match &ge; 70%</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px">
    <div style="width:14px;height:14px;background:#f5c518;border-radius:2px"></div>
    <span style="font-size:0.75rem;color:#aaa">Good match 55&ndash;70%</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px">
    <div style="width:14px;height:14px;background:#e50914;border-radius:2px"></div>
    <span style="font-size:0.75rem;color:#aaa">Moderate match &lt; 55%</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px">
    <div style="width:2px;height:14px;background:#f5c518;border:1px dashed #f5c518;border-radius:1px"></div>
    <span style="font-size:0.75rem;color:#aaa">Average similarity line</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Landing page (no query) ───────────────────────────────────────────────────
else:
    # Top-rated featured section
    st.markdown('<div class="nf-section-label">Top Rated in Library</div>', unsafe_allow_html=True)
    featured = df[df["rating"] >= 9.0].sample(min(6, (df["rating"] >= 9.0).sum()), random_state=7)
    f_cols   = st.columns(3)
    for i, (_, row) in enumerate(featured.iterrows()):
        with f_cols[i % 3]:
            genre_badges = " · ".join(g.strip() for g in str(row["genre"]).split(",") if g.strip())
            st.markdown(f"""
<div class="nf-featured-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div class="nf-featured-title">{row['title']}</div>
    <div style="background:#1a1a1a;border:1px solid #333;border-radius:3px;
                padding:0.15rem 0.45rem;font-size:0.72rem;color:#f5c518;font-weight:700;
                white-space:nowrap;margin-left:0.5rem">⭐ {row['rating']}</div>
  </div>
  <div class="nf-featured-year">{int(row['year'])} · {row['type']}</div>
  <div class="nf-featured-genre">{genre_badges}</div>
  <a href="{row['imdb_url']}" target="_blank"
     style="color:#e50914;font-size:0.75rem;font-weight:700;text-decoration:none;
            letter-spacing:0.05em;border-bottom:1px solid transparent">
    VIEW ON IMDb ›
  </a>
</div>
""", unsafe_allow_html=True)

    # Trending now
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="nf-section-label">Popular · 2020s</div>', unsafe_allow_html=True)
    trending = df[(df["year"] >= 2020) & (df["votes_clean"] > 100000)].nlargest(6, "votes_clean")
    t_cols   = st.columns(3)
    for i, (_, row) in enumerate(trending.iterrows()):
        with t_cols[i % 3]:
            genre_badges = " · ".join(g.strip() for g in str(row["genre"]).split(",") if g.strip())
            st.markdown(f"""
<div class="nf-featured-card" style="border-top-color:#f5c518">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div class="nf-featured-title">{row['title']}</div>
    <div style="background:#1a1a1a;border:1px solid #333;border-radius:3px;
                padding:0.15rem 0.45rem;font-size:0.72rem;color:#f5c518;font-weight:700;
                white-space:nowrap;margin-left:0.5rem">⭐ {row['rating']}</div>
  </div>
  <div class="nf-featured-year">{int(row['year'])} · {row['type']}</div>
  <div class="nf-featured-genre">{genre_badges}</div>
  <a href="{row['imdb_url']}" target="_blank"
     style="color:#e50914;font-size:0.75rem;font-weight:700;text-decoration:none;
            letter-spacing:0.05em">VIEW ON IMDb ›</a>
</div>
""", unsafe_allow_html=True)