import numpy as np
import joblib
from datetime import datetime
from services.tmdb_client import get_movie_recommendations_tmdb, get_movie_details
def get_hybrid_recommendations(user_id, rated_data, top_n=20):
    if not rated_data:
        return []
    high_rated = [m_id for m_id, rating in rated_data if rating >= 4]
    candidates = []
    seen_ids = set([m_id for m_id, _ in rated_data]) 
    for m_id in high_rated[:3]:
        results = get_movie_recommendations_tmdb(m_id).get('results', [])
        for movie in results:
            if movie['id'] not in seen_ids:
                candidates.append(movie)
                seen_ids.add(movie['id'])
    years = []
    genre_stats = {}
    
    for m_id, rating in rated_data:
        if rating >= 4:
            details = get_movie_details(m_id)
            if details:
                if details.get('release_date'):
                    years.append(int(details['release_date'][:4]))
                
                for g in details.get('genres', []):
                    gid = g['id']
                    genre_stats[gid] = genre_stats.get(gid, 0) + 1

    avg_fav_year = sum(years) / len(years) if years else 2015
    top_genres = sorted(genre_stats, key=genre_stats.get, reverse=True)[:2]

    
    final_scored = []
    for movie in candidates:
        score = movie.get('vote_average', 0) 
        
        m_genres = movie.get('genre_ids', [])
        if any(g in m_genres for g in top_genres):
            score += 2.0
            
       
        m_year = int(movie.get('release_date', '0')[:4]) if movie.get('release_date') else 2015
        if abs(m_year - avg_fav_year) <= 5:
            score += 1.5

        final_scored.append((score, movie))

   
    final_scored.sort(key=lambda x: x[0], reverse=True)
    return [m for s, m in final_scored[:top_n]]