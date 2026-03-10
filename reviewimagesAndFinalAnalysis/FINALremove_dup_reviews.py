import duckdb as db
import os

conn = db.connect()

os.makedirs("duckdb_temp", exist_ok=True)
conn.execute("PRAGMA temp_directory='duckdb_temp';")
conn.execute("PRAGMA preserve_insertion_order=false;")
conn.execute("PRAGMA threads=2;")
conn.execute("PRAGMA memory_limit='8GB';")

#count original rows
original_count = conn.execute("""
SELECT COUNT(*) 
FROM read_parquet('filtercolumnsnowhitespace.parquet')
""").fetchone()[0]

# 
query = """
COPY (
  WITH suspicious AS (
    SELECT
      review,
      MIN(recommendationid) AS keep_recommendationid
    FROM read_parquet('filtercolumnsnowhitespace.parquet')
    GROUP BY review
    HAVING length(review) > 20 AND COUNT(*) > 10
  )
  SELECT r.*
  FROM read_parquet('filtercolumnsnowhitespace.parquet') r
  LEFT JOIN suspicious s
    USING (review)
  WHERE
    s.review IS NULL
    OR r.recommendationid = s.keep_recommendationid
)
TO 'reviews_deduped_keep2.parquet'
(FORMAT parquet);
"""
conn.execute(query)

#count rows after removing duplicate reviews
deduped_count = conn.execute("""
SELECT COUNT(*)
FROM read_parquet('reviews_deduped_keep2.parquet')
""").fetchone()[0]

# count how many were removed
removed = original_count - deduped_count

print("Wrote reviews_deduped_keep2.parquet")
print(f"Original rows: {original_count:,}")
print(f"After deduplication: {deduped_count:,}")
print(f"Duplicate reviews removed: {removed:,}")

conn.close()