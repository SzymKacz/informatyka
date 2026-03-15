import os
import joblib
from services.tmdb_client import get_movie_recommendations_tmdb

current_dir = os.path.dirname(__file__)
MODEL_PATH = os.path.join(current_dir, '..', 'models', 'svd_model.pkl')

def get_hybrid_recommendations(user_id, rated_data, top_n=10):
    if not rated_data:
        return []

   
    algo = None
    if os.path.exists(MODEL_PATH):
        try:
            algo = joblib.load(MODEL_PATH)
            print("✅ Model SVD załadowany pomyślnie.")
        except Exception as e:
            print(f"⚠️ Błąd ładowania modelu: {e}")

    
    top_liked = [m_id for m_id, rat in rated_data if rat >= 4]
    
    candidates = []
    
    for m_id in top_liked[:3]: 
        res = get_movie_recommendations_tmdb(m_id)
        candidates.extend(res.get('results', []))

    unique_recs = {}
    already_rated = {m_id for m_id, _ in rated_data}

    
    for movie in candidates:
        m_id = movie['id']
        if m_id in already_rated or m_id in unique_recs:
            continue
            
        
        cf_score = 0
        if algo:
            
            prediction = algo.predict(user_id, m_id)
            cf_score = prediction.est 

       
        tmdb_score = movie.get('vote_average', 0)
        
       
        final_score = (cf_score * 0.7) + (tmdb_score / 2 * 0.3)
        
        unique_recs[m_id] = (final_score, movie)

  
    sorted_recs = sorted(unique_recs.values(), key=lambda x: x[0], reverse=True)
    return [movie for score, movie in sorted_recs][:top_n]