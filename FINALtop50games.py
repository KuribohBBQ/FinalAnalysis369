import duckdb as db

conn = db.connect()

query = """
WITH countreviews AS(
    SELECT appid, game,
    SUM(CASE
            WHEN voted_up = 1 THEN 1
            ELSE 0
            END) AS positive_reviews,
    SUM(CASE
            WHEN voted_up = 0 THEN 1
            ELSE 0
            END) AS negative_reviews
    FROM read_parquet('filtercolumnsnowhitespace.parquet')
    GROUP BY appid, game
),
totalreviews AS(
SELECT appid, game, positive_reviews, negative_reviews,
positive_reviews + negative_reviews AS total_reviews 
FROM countreviews
ORDER BY total_reviews DESC
)
SELECT *
FROM totalreviews
LIMIT 50
"""
top50games = conn.execute(query).fetchall()

output_file = "FINALtop50_games.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for appid, game, positive_reviews, negative_reviews, total_reviews in top50games:
        f.write(
            f"Appid: {appid}\n"
            f"Game Title: {game}\n"
            f"Positive Reviews: {positive_reviews}\n"
            f"Negative Reviews: {negative_reviews}\n"
            f"Total Reviews: {total_reviews}\n"
            + "-"*60 + "\n"
        )

print(f"Results written to {output_file}")