import duckdb as db
import pandas as pd
import matplotlib.pyplot as plt

# Connect to DuckDB
conn = db.connect()

query = """
WITH countreviews AS(
    SELECT appid, game,
        SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
        SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews
    FROM read_parquet('reviews_deduped_keep1.parquet')
    GROUP BY appid, game
),
totalreviews AS(
    SELECT appid, game, positive_reviews, negative_reviews,
           positive_reviews + negative_reviews AS total_reviews
    FROM countreviews
)
SELECT
    *,
    CAST(positive_reviews AS DOUBLE) / total_reviews AS review_score
FROM totalreviews
ORDER BY total_reviews DESC
LIMIT 75
"""

# Fetch results
df = conn.execute(query).fetchdf()

# Convert to percentage
df["review_score"] = df["review_score"] * 100

# Create bar chart
plt.figure(figsize=(20, 10))  
plt.bar(df["game"], df["review_score"])

plt.xticks(rotation=90)
plt.ylabel("Positive Review Percentage")
plt.title("Top 75 Games by Total Reviews – Positive Review Percentage FILTERED")
plt.tight_layout()

plt.savefig("FINALtop50_review_score_bar_chartFILTERED.png", dpi=200)
plt.show()

print("Bar chart saved as top50_review_score_bar_chartFILTERED.png")