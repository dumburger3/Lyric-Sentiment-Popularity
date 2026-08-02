# Billboard Hot 100 Lyric Sentiment & Popularity Analysis

Do a song's lyrics predict where it lands on the Billboard Hot 100?

A bit of context - Hello, I'm Danny and one of the things that has had the biggest impact on 
my life is music. Whenever, I'm feeling down, or need something to relax to, or just want something in
the background, music has always found a way in my life. Some of my favorite artists include
Daniel Caesar, Ariana Grande, Lauv, and a whole lot more. But the biggest thing about me is I listen to all
kinds of music, whether that be R&B, Pop, Video game music, 2010 party bops, KPOP/JPOP, you name it. A good amount 
of these songs that I listen to, however, are pretty popular and that made me wonder what about these songs 
make them popular. For example, I wanted to look at how only the lyrics, nothing else, would have an impact
on how well they perform.

This project collects the Hot 100 chart, pulls each song's lyrics, scores them for
emotional content with a transformer-based classifier, and tests whether those
signals can predict chart rank.

**Short answer: no.** A Random Forest trained only on lyric and sentiment features
performs worse than predicting the mean rank for every song (R² = -0.17). That's a
null result, and it's the point — chart position is driven by factors outside the
lyrics themselves (artist popularity, playlist placement, marketing, radio, virality).

---

## Data

- **Source:** Billboard Hot 100, chart week of **August 4, 2025** (via `billboard.py`)
- **Lyrics:** Genius API (via `lyricsgenius`)
- **Size:** 100 songs collected, **99 retained** after cleaning
  - 1 song dropped (*"Takedown"* — no lyrics returned by Genius)

## Pipeline

| # | File | What it does |
|---|------|--------------|
| 1 | `notebooks/1-data_collection.py` | Pulls the Hot 100 and fetches lyrics + release year per song. Normalizes artist-name formatting between Billboard and Genius (`x` / `with` / `and` → `&`) to improve match rate. |
| 2 | `notebooks/2-data_clean_wrangle.ipynb` | Strips Genius page metadata from raw lyrics via regex, drops songs with no lyrics, then runs emotion classification and writes the sentiment dataset. |
| 3 | `notebooks/3-data_EDA.ipynb` | Distributions, emotion breakdowns, emotion-by-rank comparisons, word frequency, and word clouds (stopwords and profanity filtered). |
| 4 | `notebooks/4-popularity_predictor.ipynb` | Feature engineering, Random Forest regression, cross-validation, and feature-importance analysis. |

Run them in order. Notebook 1 pulls the **current** chart, so re-running it will
produce a different dataset than the one in this repo.

## Sentiment classification

Uses [`j-hartmann/emotion-english-distilroberta-base`](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base),
which scores seven emotions: anger, disgust, fear, joy, neutral, sadness, surprise.

Songs run longer than the model's input window, so lyrics are split into chunks and
each chunk's scores are averaged **weighted by chunk length** — this keeps the final
profile representative of the whole song instead of just the opening verse.

## Feature engineering

24 features across four groups:

- **Raw emotion scores** — the seven emotion probabilities
- **Derived sentiment** — negative/positive aggregates, positive-to-negative ratio,
  spread across emotions, peak intensity, joy−sadness and anger−fear differentials
- **Text metrics** — character length, word count, average word length, lexical density
- **Time** — release year, song age, recency flag

**Chart-derived columns (`peak_rank`, `weeks_on_chart`, `last_week`) are deliberately
excluded.** They are downstream of the target and would leak it, producing an
impressive-looking model that has learned nothing about lyrics.

## Results

**Model:** `RandomForestRegressor` (200 trees, max_depth 15), 79 train / 20 test

| Metric | Value |
|---|---|
| Test RMSE | 33.52 |
| Test MAE | 30.07 |
| Test R² | **-0.17** |
| 5-fold CV RMSE | 31.07 ± 2.38 |

A negative R² means the model does worse than a constant baseline. Average prediction
error is roughly **30 chart positions** on a 100-position scale.

**Top features:** sadness, joy, neutral, lexical density, average word length — no
single feature carries meaningful signal, and importance is spread almost evenly
across all 24, which is itself a sign there's nothing there to find.

**Emotion correlations with rank** are all weak (|r| < 0.11). The strongest is neutral
at r = 0.11, hinting emotionally flat lyrics may rank slightly worse, but the effect
is well within noise at this sample size.

### Descriptive findings

Even without predictive power, the data shows a clear tonal skew:

- **64%** of charting songs (63 of 99) have a negative dominant emotion
  (anger, sadness, fear, or disgust)
- Distribution: neutral 25, anger 23, sadness 21, fear 17, joy 6, surprise 5, disgust 2
- Only **11 of 99** songs are dominated by a positive emotion
- Median song: ~344 words / ~1,721 characters

## Limitations

- **n = 99 from a single chart week.** Too small to generalize, and 24 features on 99
  rows invites overfitting — a meaningful share of the negative R² is likely sample
  size rather than proof that lyrics carry zero signal.
- **The emotion model is trained on English.** Non-English lyrics and heavy slang are
  scored unreliably.
- **Rank is a poor target.** Chart position at a single point in time conflates new
  releases climbing with older hits declining.

## Next steps

- Pull multiple chart weeks / years for a larger, time-aware dataset
- Predict `peak_rank` or chart longevity instead of current rank
- Add non-lyric features (artist follower count, release strategy, playlist adds) to
  quantify how much of the variance lyrics *can't* explain
- Compare against a baseline regressor to formalize the null result

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Windows
pip install -r requirements.txt
```

Requires Python 3.11+. Add a `.env` file in the project root:

```
GENIUS_ACCESS_TOKEN=your_token_here
```

Get a token from the [Genius API dashboard](https://genius.com/api-clients).
