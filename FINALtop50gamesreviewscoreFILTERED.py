import duckdb as db

conn = db.connect()

query = """
WITH
--ORIGINAL
orig_count AS (
  SELECT
    appid,
    game,
    SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
    SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews
  FROM read_parquet('filtercolumnsreview.parquet')
  GROUP BY appid, game
),
orig_total AS (
  SELECT
    appid,
    game,
    positive_reviews,
    negative_reviews,
    positive_reviews + negative_reviews AS total_reviews
  FROM orig_count
),
orig_scored AS (
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
    END AS orig_review_label,
    CAST(positive_reviews AS DOUBLE) / total_reviews AS orig_review_score
  FROM orig_total
),

--FILTERED
filt_count AS (
  SELECT
    appid,
    game,
    SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
    SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews
  FROM read_parquet('reviews_deduped_keep2.parquet')
  GROUP BY appid, game
),
filt_total AS (
  SELECT
    appid,
    game,
    positive_reviews,
    negative_reviews,
    positive_reviews + negative_reviews AS total_reviews
  FROM filt_count
),
filt_scored AS (
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
    END AS filt_review_label,
    CAST(positive_reviews AS DOUBLE) / total_reviews AS filt_review_score
  FROM filt_total
)

SELECT
  COALESCE(o.appid, f.appid) AS appid,
  COALESCE(o.game,  f.game)  AS game,

  o.total_reviews AS orig_total_reviews,
  o.orig_review_label,
  o.orig_review_score,

  f.total_reviews AS filt_total_reviews,
  f.filt_review_label,
  f.filt_review_score,

  (o.total_reviews - f.total_reviews) AS reviews_removed,
  (f.filt_review_score - o.orig_review_score) AS score_diff

FROM orig_scored o
FULL OUTER JOIN filt_scored f
  USING (appid, game)

WHERE o.total_reviews >= 100
  AND o.orig_review_label IS DISTINCT FROM f.filt_review_label

ORDER BY orig_total_reviews DESC;
"""

comparison = conn.execute(query).fetchall()

output_file = "label_comparison_original_vs_filtered.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for row in comparison:
        # FIXED: unpack in the same order as the SELECT
        (appid, game,
         orig_total, orig_label, orig_score,
         filt_total, filt_label, filt_score,
         reviews_removed, score_diff) = row

        f.write(
            f"AppID: {appid}\n"
            f"Game: {game}\n"
            f"ORIGINAL  - Total: {orig_total}  Label: {orig_label}  Score: {orig_score}\n"
            f"FILTERED  - Total: {filt_total}  Label: {filt_label}  Score: {filt_score}\n"
            f"Diff      - Score: {score_diff}  Total Reviews Removed: {reviews_removed}\n"
            + "-" * 80 + "\n"
        )

print(f"Wrote {output_file}")