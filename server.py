from flask import Flask, request, redirect, url_for, render_template
from google.cloud import firestore
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from secret import secret_key
import json

db = firestore.Client.from_service_account_json("credential.json")
collection_users = "users"
collection_name = "crop_yields"

class User(UserMixin):
    def __init__(self, username):
        super().__init__()
        self.id = username
        self.username = username

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

login = LoginManager(app)
login.login_view = '/static/login.html'



@login.user_loader
def load_user(username):
    user_ref = db.collection(collection_users).document(username).get()
    if user_ref.exists:
        return User(username)
    return None

@app.route('/register', methods=['GET'])
def register():
    return redirect(url_for('static', filename='register.html'))

@app.route('/register1', methods=['POST'])
def register1():
    if request.method == 'POST':
        username = request.values['e']
        password = request.values['p']

        user_ref = db.collection(collection_users).document(username).get()
        if user_ref.exists:
           return redirect('/static/register.html?error=Utente%20gi%C3%A0%20esistente')
        db.collection(collection_users).document(username).set({"password": password})
        return redirect('/static/login.html')

    return redirect('/static/login.html')

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/index'))
    username = request.values['e']
    password = request.values['p']

    user_ref = db.collection(collection_users).document(username).get()

    if not user_ref.exists or user_ref.to_dict().get("password") != password:
        return redirect('/static/login.html?error=Credenziali%20errate')

    if user_ref.exists and user_ref.to_dict()["password"] == password:
        login_user(User(username))
        return redirect('/index')
    return redirect('/static/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/index')


@app.route('/index', methods=['GET'])
def index():
    return redirect(url_for('static', filename='index.html'))

@app.route('/map', methods=['GET'])
@login_required
def map():
    return redirect(url_for('static', filename='map.html'))

@app.route('/graph', methods=['GET'])
@login_required
def graph():
    return redirect(url_for('static', filename='graph.html'))

@app.route('/graph2', methods=['GET'])
@login_required
def graph2():
    return redirect(url_for('static', filename='graph2.html'))

@app.route('/get_data', methods=['GET'])
@login_required
def get_data():
    docs = db.collection(collection_name).stream()
    data = [doc.to_dict() for doc in docs]
    return json.dumps(data), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
