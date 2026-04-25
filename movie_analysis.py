"""
mrs.py — Movie & Series Recommendation System (v3)
===================================================
Recommendation basis (hybrid, weighted):

  Layer 1 — Genre tags (5x)
      Primary axis. Action/Adventure/Drama etc. from IMDb metadata.

  Layer 2 — Inferred subgenre (4x)
      Because the dataset uses broad genre tags, many different shows share
      identical genre strings (GoT and Star Trek are both Action,Adventure,Drama).
      We infer a thematic subgenre from the title text:
        medieval_fantasy  → dragon, throne, knight, witch, magic, realm …
        scifi             → space, galaxy, alien, robot, future …
        crime_thriller    → heist, murder, detective, cop, mafia …
        superhero         → avenger, batman, spider, marvel, dc …
        war_military      → war, soldier, army, battle …
        horror            → zombie, demon, haunted, vampire …
        spy_espionage     → spy, cia, agent, mission …
      This makes GoT cluster with HotD, Vikings, Merlin — not with Star Trek.

  Layer 3 — Content type (3x)
      TV Series stays near TV Series; Movie near Movie.

  Layer 4 — Decade bucket (2x)
      Titles from the same era feel tonally similar.

  Layer 5 — Rating tier (2x)
      Prestige/Good/Average/Low buckets.

  Layer 6 — Director & lead actor (1x each)
      Stylistic signal, deliberately low-weighted to avoid cast over-fitting.

OLD vs NEW for "Game of Thrones":
  OLD: genre×2 + director + full_cast → cast/director dominated
       → missed House of the Dragon, Vikings (different cast, same director)
  NEW: subgenre×4 + genre×5 + type×3 → thematic clustering
       → GoT, HotD, Vikings, Black Sails, Marco Polo all share
         medieval_fantasy + Action,Adventure,Drama + TV_Series ✓
"""

import pandas as pd
import numpy as np
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ─────────────────────────────────────────────────────────────────────────────
# Subgenre keyword maps
# ─────────────────────────────────────────────────────────────────────────────

SUBGENRE_RULES = [
    ("medieval_fantasy",  r"dragon|throne|thrones|knight|witch|wizard|magic|realm|quest|elf|dwarf|orc|sorcerer|merlin|viking|medieval|sword|king|kingdom|legend|myth|rune|barbarian|warcraft|hobbit|tolkien|rings"),
    ("scifi_space",       r"space|galaxy|alien|robot|android|cyborg|future|mars|star.trek|star.wars|sci.fi|interstellar|cosmos|moon|astronaut|dystopia|cyberpunk"),
    ("superhero",         r"avenger|batman|spider|superman|marvel|x.men|ironman|thor|captain.america|hulk|wonder.woman|flash|gotham|wakanda|deadpool"),
    ("crime_thriller",    r"heist|murder|detective|cop|police|mafia|cartel|drug|hitman|serial.killer|forensic|criminal|prison|gang|underworld|mob"),
    ("horror",            r"zombie|demon|haunted|ghost|vampire|werewolf|horror|exorcist|paranormal|creature|slasher|supernatural|curse|monster"),
    ("war_military",      r"\bwar\b|soldier|army|battle|military|navy|marine|combat|wwii|vietnam|korea|siege|invasion|guerrilla|resistance"),
    ("spy_espionage",     r"\bspy\b|cia|mi6|fbi|agent|mission|espionage|intel|undercover|surveillance|covert|operation|mossad"),
    ("romance_drama",     r"love|romance|affair|wedding|marriage|heart|passion|relationship|date|couple|boyfriend|girlfriend"),
    ("comedy",            r"funny|comedy|laugh|humor|sitcom|parody|satire|farce"),
    ("animation",         r"animated|animation|cartoon|pixar|disney|anime"),
    ("sport",             r"\bsport\b|football|basketball|soccer|baseball|tennis|boxing|racing|athlete|olympic|championship|league"),
    ("documentary",       r"documentary|docuseries|true.crime|biography|history|real.life|nature|wildlife"),
]


def infer_subgenre(title: str, genre: str) -> str:
    """Return a space-separated string of matched subgenre tokens."""
    text = (title + " " + genre).lower()
    matched = []
    for label, pattern in SUBGENRE_RULES:
        if re.search(pattern, text):
            matched.append(label)
    return " ".join(matched) if matched else "general"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Load & clean
# ─────────────────────────────────────────────────────────────────────────────

def load_data(path: str = "imdb_dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df.fillna("", inplace=True)

    df["votes_clean"] = (
        df["votes"].astype(str)
        .str.replace(",", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0).astype(int)
    )

    df["decade"] = (df["year"] // 10 * 10).astype(str).apply(lambda d: f"decade_{d}s")

    def tier(r):
        if r >= 8.0: return "tier_prestige"
        if r >= 6.5: return "tier_good"
        if r >= 5.0: return "tier_average"
        return "tier_low"
    df["rating_tier"] = df["rating"].apply(tier)
    df["type_token"]  = df["type"].str.replace(" ", "_", regex=False)
    df["subgenre"]    = df.apply(lambda r: infer_subgenre(r["title"], r["genre"]), axis=1)
    df["title_lower"] = df["title"].str.lower().str.strip()
    df.reset_index(drop=True, inplace=True)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. Weighted soup
# ─────────────────────────────────────────────────────────────────────────────

def build_soup(row: pd.Series) -> str:
    genres     = row["genre"].replace(",", " ")
    subgenre   = row["subgenre"]
    type_tok   = row["type_token"]
    decade     = row["decade"]
    tier_tok   = row["rating_tier"]
    director   = row["director"].split(";")[0].strip()
    lead_actor = row["cast"].split(";")[0].strip()

    parts = (
        f"{subgenre} " * 4 +    # inferred theme  — highest weight
        f"{genres} " * 5 +      # raw genre tags  — high weight
        f"{type_tok} " * 3 +    # series vs movie — medium weight
        f"{decade} " * 2 +      # era             — medium weight
        f"{tier_tok} " * 2 +    # prestige tier   — medium weight
        f"{director} " +         # style           — low weight
        f"{lead_actor}"          # star            — low weight
    )
    return parts.strip()


def build_features(df: pd.DataFrame):
    df["soup"] = df.apply(build_soup, axis=1)
    vectorizer = TfidfVectorizer(
        max_features=20_000,
        ngram_range=(1, 2),
        stop_words="english",
        min_df=1,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(df["soup"])
    return matrix, vectorizer, df


# ─────────────────────────────────────────────────────────────────────────────
# 3. Recommendation function
# ─────────────────────────────────────────────────────────────────────────────

def get_matches(query: str, df) -> pd.DataFrame:
    """
    Return all titles whose name contains *query* (case-insensitive),
    sorted by rating descending.  Used to power the suggestion list in the UI
    before the user picks the exact title they want.
    """
    query_lower = query.lower().strip()
    if not query_lower:
        return pd.DataFrame()
    exact  = df[df["title_lower"] == query_lower]
    substr = df[df["title_lower"].str.contains(re.escape(query_lower), regex=True)]
    combined = pd.concat([exact, substr]).drop_duplicates()
    return combined.sort_values("rating", ascending=False)[
        ["title", "year", "type", "genre", "rating"]
    ].reset_index(drop=True)


def get_recommendations(query, df, tfidf_matrix, top_n=10, type_filter=None):
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
    sim_scores   = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    sim_series   = pd.Series(sim_scores, index=df.index).drop(idx)

    if type_filter and type_filter != "All":
        valid_idx  = df[df["type"] == type_filter].index
        sim_series = sim_series[sim_series.index.isin(valid_idx)]

    top_indices = sim_series.nlargest(top_n).index
    results     = df.loc[top_indices].copy()
    results["similarity"] = sim_series[top_indices].values

    return results[[
        "title", "year", "type", "genre", "rating", "votes_clean",
        "director", "cast", "runtime", "similarity", "imdb_url",
    ]].reset_index(drop=True), source_title, source_rating


# ─────────────────────────────────────────────────────────────────────────────
# 4. Build & pickle
# ─────────────────────────────────────────────────────────────────────────────

def build_and_save(csv_path="imdb_dataset.csv", model_path="recommendation_model.pkl"):
    print("Loading dataset ...")
    df = load_data(csv_path)
    print(f"  {len(df):,} titles loaded.")
    print("Building TF-IDF features ...")
    matrix, vectorizer, df = build_features(df)
    print(f"  Matrix shape: {matrix.shape}")
    payload = {"df": df, "tfidf_matrix": matrix, "vectorizer": vectorizer}
    print(f"Saving model -> {model_path} ...")
    with open(model_path, "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    print("Done.")
    return payload


# ─────────────────────────────────────────────────────────────────────────────
# 5. CLI smoke-test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    csv_path   = sys.argv[1] if len(sys.argv) > 1 else "imdb_dataset.csv"
    model_path = sys.argv[2] if len(sys.argv) > 2 else "recommendation_model.pkl"

    payload = build_and_save(csv_path, model_path)

    for sample in ["Game of Thrones", "Inception", "Breaking Bad", "The Dark Knight"]:
        recs, src, src_rating = get_recommendations(sample, payload["df"], payload["tfidf_matrix"], top_n=8)
        print(f"\nTop-8 for '{src}' (IMDb: {src_rating}):")
        if recs.empty:
            print("  No results.")
        else:
            print(recs[["title", "year", "type", "genre", "rating"]].to_string(index=False))