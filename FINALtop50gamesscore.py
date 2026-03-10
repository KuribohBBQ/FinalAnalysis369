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
SELECT
    *,
    CASE
        WHEN total_reviews < 50 THEN
            CASE
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .79 THEN 'Positive'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .69 THEN 'Mostly Positive'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .39 THEN 'Mixed'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .19 THEN 'Mostly Negative'
                ELSE 'Negative'
            END

        WHEN total_reviews < 500 THEN
            CASE
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .79 THEN 'Very Positive'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .69 THEN 'Mostly Positive'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .39 THEN 'Mixed'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .19 THEN 'Mostly Negative'
                ELSE 'Very Negative'
            END

        ELSE
            CASE
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .94 THEN 'Overwhelmingly Positive'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .79 THEN 'Very Positive'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .69 THEN 'Mostly Positive'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .39 THEN 'Mixed'
                WHEN CAST(positive_reviews AS DOUBLE) / total_reviews > .19 THEN 'Mostly Negative'
                ELSE 'Overwhelmingly Negative'
            END
    END AS review_label,
    CAST(positive_reviews AS DOUBLE) / total_reviews AS review_score
FROM totalreviews;
"""
top50gameswithscores = conn.execute(query).fetchall()

output_file = "FINALgames_with_review_scores.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for appid, game, positive_reviews, negative_reviews, total_reviews, review_label, review_score in top50gameswithscores:
        f.write(
            f"AppID: {appid}\n"
            f"Game Title: {game}\n"
            f"Positive Reviews: {positive_reviews}\n"
            f"Negative Reviews: {negative_reviews}\n"
            f"Total Reviews: {total_reviews}\n"
            f"Review Label: {review_label}\n"
            f"Review Score: {review_score}\n"
            + "-" * 70 + "\n"
        )

print(f"Results written to {output_file}")