from flask import Flask, render_template, url_for, request, redirect, session
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import secrets
from utils import file_exists

app = Flask(__name__)

# Membaca dataset
data = pd.read_csv('steam_user_test.csv')

# Menyiapkan data user-item
user_item_matrix = data.pivot_table(index='user_id', columns='game_name', values='hours', fill_value=0)

# Menghitung similarity matrix menggunakan cosine similarity
item_similarity = cosine_similarity(user_item_matrix.T)

# Membuat DataFrame similarity matrix
item_similarity_df = pd.DataFrame(item_similarity, index=user_item_matrix.columns, columns=user_item_matrix.columns)

# Fungsi rekomendasi berdasarkan collaborative filtering dengan menampilkan yang paling direkomendasikan
def get_top_recommended_games_collaborative(limit=10):
    # Menghitung rata-rata playtime untuk setiap game
    average_playtime = user_item_matrix.mean()

    # Matriks dengan bobot berdasarkan similarity dan playtime rata-rata
    weighted_matrix = item_similarity_df.mul(average_playtime, axis=0)

    # Menjumlahkan bobot untuk mendapatkan nilai total rekomendasi
    total_recommendation_score = weighted_matrix.sum(axis=1)

    # Mengurutkan game berdasarkan nilai total rekomendasi
    top_recommended_games = total_recommendation_score.sort_values(ascending=False).index[:limit]

    return top_recommended_games

#mirip kek di atas tapi ini ada ketambahan argumen 1 nama game
def get_top_recommended_games_collaborative_game_similarity(game_name, limit=10):
    # Mendapatkan vector similarity untuk game yang dipilih
    selected_game_similarity = item_similarity_df[game_name]

    # Mengurutkan game berdasarkan similarity
    top_recommended_games = selected_game_similarity.sort_values(ascending=False).index[1:limit+1]

    return top_recommended_games

# Fungsi untuk mendapatkan game yang direkomendasikan
def get_recommended_games():
    # Implementasikan logika bisnis untuk mendapatkan game yang direkomendasikan di sini
    top_recommendations = get_top_recommended_games_collaborative(limit=10)
    
    return top_recommendations

# Fungsi untuk mendapatkan game yang direkomendasikan
def get_all_games():
    all_games = data['game_name'].unique()
    all_games.sort()
    
    return all_games

# Route untuk halaman utama
app.secret_key = secrets.token_hex(16)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_game = request.form['selected_game']
        session['selected_game'] = selected_game
        return redirect(url_for('result'))

    recommended_games = get_recommended_games()
    all_games = get_all_games()
    return render_template('index.html', recommended_games=recommended_games, all_games=all_games)

@app.route('/result')
def result():
    selected_game = session.get('selected_game', None)
    if not selected_game:
        return redirect(url_for('index'))

    recommended_games = get_top_recommended_games_collaborative_game_similarity(selected_game)

    return render_template('result.html', selected_game=selected_game, recommended_games=recommended_games, file_exists=file_exists)

if __name__ == '__main__':
    app.run(debug=True)
