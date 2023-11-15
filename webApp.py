from flask import Flask, render_template, redirect, request, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secret key of your choice

client_id = 'abcdc6ec5e66488ab295abb3a4401917'
client_secret = '9ed30e1571364288b2a8a1b690f2ea91'

# Define the SpotifyOAuth instance
sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri='http://localhost:8888/callback', scope='user-library-read user-top-read')

@app.route('/')
def show_top_tracks():
    user, top_tracks = fetch_top_tracks()
    html_content = generate_html(user, top_tracks)
    return render_template('index.html', content=html_content)

def fetch_top_tracks():
    if 'token_info' not in session or sp_oauth.is_token_expired(session['token_info']):
        return None, None

    sp = spotipy.Spotify(auth=session['token_info']['access_token'])
    user = sp.current_user()
    top_tracks = sp.current_user_top_tracks(limit=10, time_range='medium_term')
    return user, top_tracks

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect(url_for('show_top_tracks'))

def generate_html(user, top_tracks):
    if user is None or top_tracks is None:
        return "<h1>Error: Unable to fetch top tracks. Please try again.</h1>"

    html_content = f"<h1>Welcome, {user['display_name']}!</h1>"
    for idx, track in enumerate(top_tracks['items']):
        track_info = f"{idx + 1}. {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}"
        html_content += f"<p>{track_info}</p>"

    return html_content

if __name__ == '__main__':
    app.run(debug=True)
