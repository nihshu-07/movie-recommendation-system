import streamlit as st
import pickle
import pandas as pd
import requests

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>

/* Entire app background */
.stApp {
    background: linear-gradient(to right, #141E30, #243B55);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Main title */
.title {
    text-align: center;
    font-size: 60px;
    font-weight: 800;
    color: #FF4B4B;
    margin-top: 10px;
    margin-bottom: 5px;
    text-shadow: 2px 2px 15px rgba(255,75,75,0.5);
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 20px;
    color: #D3D3D3;
    margin-bottom: 40px;
}

/* Select box label */
.stSelectbox label {
    color: white !important;
    font-size: 18px !important;
    font-weight: 600;
}

/* Dropdown style */
div[data-baseweb="select"] > div {
    background-color: #1E293B;
    border: 2px solid #FF4B4B;
    border-radius: 12px;
    color: white;
}

/* Button */
.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #FF4B4B, #FF6A3D);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 12px;
    font-size: 18px;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(255,75,75,0.4);
}

/* Button hover */
.stButton > button:hover {
    transform: translateY(-3px);
    background: linear-gradient(90deg, #ff2e2e, #ff7b54);
    box-shadow: 0 8px 20px rgba(255,75,75,0.6);
}

/* Selected movie info box */
.selected-movie {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 20px;
    margin-top: 20px;
    margin-bottom: 30px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
}

/* Recommendation cards */
.movie-card {
    background: rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 20px;
    text-align: center;
    margin-top: 10px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    min-height: 320px;
}

/* Hover effect on cards */
.movie-card:hover {
    transform: translateY(-8px);
    box-shadow: 0px 12px 24px rgba(255,75,75,0.4);
}

/* Movie title inside cards */
.movie-card h4 {
    color: #FF6A3D;
    font-size: 20px;
    margin-bottom: 10px;
}

/* Movie details text */
.movie-card p {
    color: #E5E7EB;
    font-size: 14px;
    margin: 5px 0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111827;
    color: white;
    border-right: 1px solid #2D3748;
}

/* Sidebar heading */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FF4B4B;
}

/* Poster images */
img {
    border-radius: 18px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.5);
}

/* Footer */
.footer {
    text-align: center;
    color: #B0B0B0;
    margin-top: 40px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# ---------- Load Data ----------
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# ---------- Fetch Poster ----------
def fetch_movie_details(movie_id):
    api_key = "d4ae7ac9713970fab7385733790daa83"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    data = requests.get(url).json()

    poster_path = data.get('poster_path')
    poster = (
        "https://image.tmdb.org/t/p/w500/" + poster_path
        if poster_path
        else "https://via.placeholder.com/300x450?text=No+Poster"
    )

    title = data.get('title', 'No Title')
    overview = data.get('overview', 'No description available.')
    rating = data.get('vote_average', 'N/A')
    release_date = data.get('release_date', 'N/A')

    genres = ", ".join([genre['name'] for genre in data.get('genres', [])])

    return {
        "poster": poster,
        "title": title,
        "overview": overview,
        "rating": rating,
        "release_date": release_date,
        "genres": genres
    }

# ---------- Recommendation Function ----------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        details = fetch_movie_details(movie_id)
        recommendations.append(details)

    return recommendations

# ---------- Header ----------
st.markdown('<div class="title">🎬 Movie Recommender System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Find movies similar to your favorites instantly</div>',
    unsafe_allow_html=True
)

# ---------- Sidebar ----------
st.sidebar.header("About")
st.sidebar.write("""
This recommender system suggests movies based on similarity.

Built with:
- Python
- Streamlit
- Pandas
- Pickle
- TMDB API
""")

# ---------- Select Movie ----------
selected_movie = st.selectbox(
    "Choose a movie",
    movies['title'].values
)

# ---------- Recommendation Button ----------
if st.button("Recommend Movies"):
    recommendations = recommend(selected_movie)

    st.subheader("Top Recommendations")

    cols = st.columns(5)

    for col, movie in zip(cols, recommendations):
        with col:
            st.image(movie["poster"], use_container_width=True)

            st.markdown(f"""
            <div class='movie-card'>
                <h4>{movie["title"]}</h4>
                <p><b>⭐ Rating:</b> {movie["rating"]}</p>
                <p><b>📅 Release:</b> {movie["release_date"]}</p>
                <p><b>🎭 Genre:</b> {movie["genres"]}</p>
                <p style="font-size:13px;">{movie["overview"][:120]}...</p>
            </div>
            """, unsafe_allow_html=True)