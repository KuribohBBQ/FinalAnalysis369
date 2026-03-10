import duckdb as db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

conn = db.connect()


query_unfiltered = """
WITH countreviews AS (
    SELECT
        appid,
        game,
        SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
        SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews
    FROM read_parquet('filtercolumnsnowhitespace.parquet')
    GROUP BY appid, game
),
totalreviews AS (
    SELECT
        appid,
        game,
        positive_reviews + negative_reviews AS total_reviews
    FROM countreviews
)
SELECT *
FROM totalreviews
ORDER BY total_reviews DESC
LIMIT 50
"""
df_unfiltered = conn.execute(query_unfiltered).fetchdf()


query_filtered = """
WITH countreviews AS (
    SELECT
        appid,
        game,
        SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
        SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews
    FROM read_parquet('reviews_deduped_keep2.parquet')
    GROUP BY appid, game
),
totalreviews AS (
    SELECT
        appid,
        game,
        positive_reviews + negative_reviews AS total_reviews
    FROM countreviews
)
SELECT *
FROM totalreviews
ORDER BY total_reviews DESC
LIMIT 50
"""
df_filtered = conn.execute(query_filtered).fetchdf()

conn.close()

# -------- Merge games with same appid --------
df_compare = pd.merge(
    df_unfiltered[["appid", "game", "total_reviews"]],
    df_filtered[["appid", "total_reviews"]],
    on="appid",
    suffixes=("_unfiltered", "_filtered")
)

df_compare = df_compare.sort_values("total_reviews_unfiltered", ascending=False).reset_index(drop=True)

x = np.arange(len(df_compare))
width = 0.4

plt.figure(figsize=(22, 10))

plt.bar(x - width/2, df_compare["total_reviews_unfiltered"], width, label="Unfiltered")
plt.bar(x + width/2, df_compare["total_reviews_filtered"], width, label="Filtered")

plt.xticks(x, df_compare["game"], rotation=90)
plt.ylabel("Total Review Count")
plt.title("Top 50 Games: Filtered vs Unfiltered Total Review Count Comparison")
plt.legend()

plt.tight_layout()
plt.savefig("FINALcomparison_total_reviews_filtered_vs_unfiltered.png", dpi=200)
plt.show()

print("Saved comparison graph as FINALcomparison_total_reviews_filtered_vs_unfiltered.png")