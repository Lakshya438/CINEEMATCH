"""
IMDb Large Dataset Builder — 10,000 to 500,000+ titles
=======================================================

Uses IMDb's OFFICIAL FREE datasets from https://datasets.imdbws.com/
No scraping. No API key. No rate limits. Updated daily by IMDb.

Files downloaded (~700 MB total, one-time):
  • title.basics.tsv.gz    — title, year, type, genres, runtime
  • title.ratings.tsv.gz   — IMDb rating + vote count
  • title.crew.tsv.gz      — director/writer IDs
  • name.basics.tsv.gz     — person name lookup table
  • title.principals.tsv.gz — cast (actors/actresses)

Output: imdb_dataset.csv with 10k–500k rows depending on your filters.

Requirements:
    pip install pandas tqdm requests

Usage:
    python imdb_dataset_builder.py
"""

import os
import gzip
import shutil
import requests
import pandas as pd
from tqdm import tqdm

# ══════════════════════════════════════════════════════
#  CONFIGURATION — tweak these to control output size
# ══════════════════════════════════════════════════════

OUTPUT_CSV   = "imdb_dataset.csv"
DATA_DIR     = "imdb_raw"          # where .tsv.gz files are saved

# ── Filters ────────────────────────────────────────────
TITLE_TYPES  = ["movie", "tvSeries", "tvMovie", "tvMiniSeries"]
# Options: movie, tvSeries, tvMovie, tvMiniSeries, tvSpecial,
#          short, tvShort, video, videoGame, tvEpisode

MIN_VOTES    = 1000      # minimum IMDb votes  (raise for fewer, higher-quality rows)
                         # 1000  → ~85,000 titles
                         # 500   → ~130,000 titles
                         # 100   → ~250,000 titles
                         # 0     → all ~500,000 rated titles

MIN_RATING   = 0.0       # minimum IMDb rating (0.0 = no filter)
MIN_YEAR     = 1900      # earliest release year
MAX_RESULTS  = 20000     # cap output rows (None = no cap, sorted by votes desc)

# ── Cast settings ──────────────────────────────────────
MAX_CAST     = 3         # number of actors to include per title

# ══════════════════════════════════════════════════════

IMDB_FILES = {
    "basics":     "https://datasets.imdbws.com/title.basics.tsv.gz",
    "ratings":    "https://datasets.imdbws.com/title.ratings.tsv.gz",
    "crew":       "https://datasets.imdbws.com/title.crew.tsv.gz",
    "names":      "https://datasets.imdbws.com/name.basics.tsv.gz",
    "principals": "https://datasets.imdbws.com/title.principals.tsv.gz",
}

os.makedirs(DATA_DIR, exist_ok=True)


# ──────────────────────────────────────────────────────
# Step 1: Download files
# ──────────────────────────────────────────────────────

def download_file(url: str, dest: str):
    """Download with progress bar, skip if already exists."""
    if os.path.exists(dest):
        size_mb = os.path.getsize(dest) / (1024 * 1024)
        print(f"  ✓ Already downloaded: {os.path.basename(dest)} ({size_mb:.1f} MB)")
        return

    print(f"  ↓ Downloading {os.path.basename(dest)} …")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; IMDb-Dataset-Builder/1.0)"}
    with requests.get(url, stream=True, headers=headers, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        with open(dest, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, unit_divisor=1024,
            desc=os.path.basename(dest), ncols=70,
        ) as bar:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                f.write(chunk)
                bar.update(len(chunk))


def download_all():
    print("\n📥  Downloading IMDb datasets (one-time, ~700 MB total)…")
    paths = {}
    for key, url in IMDB_FILES.items():
        fname = url.split("/")[-1]
        dest  = os.path.join(DATA_DIR, fname)
        download_file(url, dest)
        paths[key] = dest
    return paths


# ──────────────────────────────────────────────────────
# Step 2: Load TSV files into DataFrames
# ──────────────────────────────────────────────────────

def load_tsv(path: str, cols=None, dtype=None) -> pd.DataFrame:
    print(f"  Loading {os.path.basename(path)} …", end=" ", flush=True)
    df = pd.read_csv(
        path, sep="\t", na_values="\\N", low_memory=False,
        usecols=cols, dtype=dtype,
    )
    print(f"{len(df):,} rows")
    return df


# ──────────────────────────────────────────────────────
# Step 3: Build the dataset
# ──────────────────────────────────────────────────────

def build_dataset(paths: dict) -> pd.DataFrame:
    print("\n🔧  Building dataset …\n")

    # ── Load basics ───────────────────────────────────
    basics = load_tsv(
        paths["basics"],
        cols=["tconst", "titleType", "primaryTitle", "startYear", "runtimeMinutes", "genres"],
    )
    # Filter by type
    basics = basics[basics["titleType"].isin(TITLE_TYPES)].copy()
    # Filter by year
    basics["startYear"] = pd.to_numeric(basics["startYear"], errors="coerce")
    basics = basics[basics["startYear"] >= MIN_YEAR]
    print(f"  After type/year filter: {len(basics):,} titles")

    # ── Load ratings ──────────────────────────────────
    ratings = load_tsv(
        paths["ratings"],
        cols=["tconst", "averageRating", "numVotes"],
    )
    ratings = ratings[ratings["numVotes"] >= MIN_VOTES]
    if MIN_RATING > 0:
        ratings = ratings[ratings["averageRating"] >= MIN_RATING]
    print(f"  After vote/rating filter: {len(ratings):,} titles")

    # ── Merge basics + ratings ────────────────────────
    df = basics.merge(ratings, on="tconst", how="inner")
    print(f"  After merge: {len(df):,} titles")

    # ── Sort by votes descending ──────────────────────
    df = df.sort_values("numVotes", ascending=False)

    # ── Cap results ───────────────────────────────────
    if MAX_RESULTS:
        df = df.head(MAX_RESULTS)
        print(f"  Capped to top {MAX_RESULTS:,} by vote count")

    ids = set(df["tconst"])
    print(f"\n  Working with {len(df):,} titles\n")

    # ── Load crew (directors) ─────────────────────────
    crew = load_tsv(paths["crew"], cols=["tconst", "directors"])
    crew = crew[crew["tconst"].isin(ids)]

    # ── Load names lookup ─────────────────────────────
    names = load_tsv(
        paths["names"],
        cols=["nconst", "primaryName"],
    )
    name_map = dict(zip(names["nconst"], names["primaryName"]))
    del names  # free memory

    def resolve_names(id_str, max_n=3):
        if pd.isna(id_str):
            return ""
        parts = str(id_str).split(",")[:max_n]
        return "; ".join(name_map.get(p, p) for p in parts if p)

    print("  Resolving director names …")
    crew["director_names"] = crew["directors"].apply(resolve_names)
    df = df.merge(crew[["tconst", "director_names"]], on="tconst", how="left")

    # ── Load principals (cast) ────────────────────────
    print("  Loading cast (this may take a moment) …")
    principals = load_tsv(
        paths["principals"],
        cols=["tconst", "ordering", "nconst", "category"],
    )
    actors = principals[
        principals["tconst"].isin(ids) &
        principals["category"].isin(["actor", "actress"])
    ].copy()
    actors = actors.sort_values("ordering")
    actors["name"] = actors["nconst"].map(name_map)

    print("  Aggregating cast per title …")
    cast_agg = (
        actors.groupby("tconst")["name"]
        .apply(lambda x: "; ".join(x.dropna().iloc[:MAX_CAST]))
        .reset_index()
        .rename(columns={"name": "cast"})
    )
    df = df.merge(cast_agg, on="tconst", how="left")
    del principals, actors, cast_agg

    # ── Clean & rename columns ────────────────────────
    def fmt_runtime(val):
        try:
            mins = int(float(val))
            h, m = divmod(mins, 60)
            return f"{h}h {m}m" if h else f"{m}m"
        except (ValueError, TypeError):
            return ""

    def fmt_type(t):
        mapping = {
            "movie":         "Movie",
            "tvSeries":      "TV Series",
            "tvMovie":       "TV Movie",
            "tvMiniSeries":  "Mini Series",
            "tvSpecial":     "TV Special",
            "short":         "Short",
        }
        return mapping.get(t, t)

    df["runtime"]  = df["runtimeMinutes"].apply(fmt_runtime)
    df["type"]     = df["titleType"].apply(fmt_type)
    df["year"]     = df["startYear"].astype("Int64").astype(str).replace("<NA>", "")
    df["imdb_url"] = "https://www.imdb.com/title/" + df["tconst"] + "/"
    df["votes"]    = df["numVotes"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
    df["genre"]    = df["genres"].fillna("")

    # ── Final column selection ────────────────────────
    final = df[[
        "tconst", "primaryTitle", "year", "averageRating", "votes",
        "genre", "runtime", "director_names", "cast", "type", "imdb_url",
    ]].rename(columns={
        "tconst":          "imdb_id",
        "primaryTitle":    "title",
        "averageRating":   "rating",
        "director_names":  "director",
    })

    final = final.fillna("").reset_index(drop=True)
    return final


# ──────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  IMDb Large Dataset Builder")
    print("  Source: https://datasets.imdbws.com/ (official, free)")
    print("=" * 60)

    # Download
    paths = download_all()

    # Build
    df = build_dataset(paths)

    # Save
    print(f"\n💾  Saving → {OUTPUT_CSV} …")
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    # Summary
    print("\n" + "=" * 60)
    print(f"  ✅  Done!")
    print(f"  Rows:    {len(df):,}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  File:    {OUTPUT_CSV}")
    print(f"  Size:    {os.path.getsize(OUTPUT_CSV) / (1024*1024):.1f} MB")
    print("=" * 60)

    # Preview
    print("\nSample rows:")
    print(df[["title", "year", "rating", "genre", "director", "cast", "type"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()