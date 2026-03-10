import duckdb as db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

conn = db.connect()

query = """
WITH countreviews AS(
    SELECT appid, game,
        SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
        SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews
    FROM read_parquet('filtercolumnsnowhitespace.parquet')
    GROUP BY appid, game
),
totalreviews AS(
    SELECT appid, game, positive_reviews, negative_reviews,
           positive_reviews + negative_reviews AS total_reviews
    FROM countreviews
)
SELECT *
FROM totalreviews
ORDER BY total_reviews DESC
LIMIT 50
"""

df = conn.execute(query).fetchdf()

# begin plotting
x = np.arange(len(df))          # 0..49
bar_width = 0.4

plt.figure(figsize=(16, 8))

plt.bar(x - bar_width/2, df["positive_reviews"], width=bar_width, label="Positive")
plt.bar(x + bar_width/2, df["negative_reviews"], width=bar_width, label="Negative")

plt.xticks(x, df["game"], rotation=75, ha="right")
plt.ylabel("Number of Reviews")
plt.title("Top 75 Games: Positive vs Negative Reviews")
plt.legend()
plt.tight_layout()

plt.savefig("FINALtop50_positive_negative.png", dpi=200)
plt.show()

print("Saved chart to FINALtop50_positive_negative.png")