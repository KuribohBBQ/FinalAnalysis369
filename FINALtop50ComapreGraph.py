import duckdb as db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

conn = db.connect()

# unfiltered reviews
query_unfiltered = """
WITH countreviews AS(
    SELECT appid, game,
        SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
        SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews
    FROM read_parquet('filtercolumnsnowhitespace.parquet')
    GROUP BY appid, game
),
totalreviews AS(
    SELECT appid, game,
           positive_reviews + negative_reviews AS total_reviews,
           CAST(positive_reviews AS DOUBLE) /
           (positive_reviews + negative_reviews) AS review_score
    FROM countreviews
)
SELECT *
FROM totalreviews
ORDER BY total_reviews DESC
LIMIT 50
"""

df_unfiltered = conn.execute(query_unfiltered).fetchdf()


#filtered reviews
query_filtered = """
WITH countreviews AS(
    SELECT appid, game,
        SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
        SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews
    FROM read_parquet('reviews_deduped_keep2.parquet')
    GROUP BY appid, game
),
totalreviews AS(
    SELECT appid, game,
           positive_reviews + negative_reviews AS total_reviews,
           CAST(positive_reviews AS DOUBLE) /
           (positive_reviews + negative_reviews) AS review_score
    FROM countreviews
)
SELECT *
FROM totalreviews
ORDER BY total_reviews DESC
LIMIT 50
"""

df_filtered = conn.execute(query_filtered).fetchdf()

conn.close()


# merge games with same appid
df_compare = pd.merge(
    df_unfiltered[["appid", "game", "review_score"]],
    df_filtered[["appid", "review_score"]],
    on="appid",
    suffixes=("_unfiltered", "_filtered")
)

# Convert to percentage
df_compare["review_score_unfiltered"] *= 100
df_compare["review_score_filtered"] *= 100

x = np.arange(len(df_compare))
width = 0.4

plt.figure(figsize=(22, 10))

plt.bar(x - width/2, df_compare["review_score_unfiltered"], width, label="Unfiltered")
plt.bar(x + width/2, df_compare["review_score_filtered"], width, label="Filtered")

plt.xticks(x, df_compare["game"], rotation=90)
plt.ylabel("Positive Review Percentage")
plt.title("Top 50 Games: Filtered vs Unfiltered Review Score Comparison")
plt.legend()

plt.tight_layout()
plt.savefig("FINALcomparison_filtered_vs_unfiltered.png", dpi=200)
plt.show()

print("Saved comparison graph as FINALcomparison_filtered_vs_unfiltered.png")