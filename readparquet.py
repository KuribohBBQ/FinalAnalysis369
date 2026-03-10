import duckdb

con = duckdb.connect()

# ['recommendationid', 'appid', 'game', 'author_steamid', 'author_num_games_owned', 'author_num_reviews', 'author_playtime_forever', 
# 'author_playtime_last_two_weeks', 'author_playtime_at_review', 'author_last_played', 'language', 'review', 
# 'timestamp_created', 'timestamp_updated', 'voted_up', 'votes_up', 'votes_funny', 'weighted_vote_score', 'comment_count', 
# 'steam_purchase', 'received_for_free', 'written_during_early_access', 'hidden_in_steam_china', 'steam_china_location']

df = con.execute("""
SELECT *
FROM read_parquet('filtercolumnsreview.parquet')
LIMIT 5
""").fetchdf()

print(df)