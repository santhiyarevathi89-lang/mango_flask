import os
from pymongo import MongoClient
from flask import Flask, render_template_string, request, redirect, url_for, session, flash

# ================= FLASK CONFIG =================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "secret_key_123")

# ================= LOGIN =================
USERNAME = os.environ.get("APP_USERNAME", "admin")
PASSWORD = os.environ.get("APP_PASSWORD", "1234")

# ================= MONGODB CONNECTION =================
mongo_uri = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://Cloud_base_v1S:cloud_123@cluster0.hlc6abe.mongodb.net/cloud_db?retryWrites=true&w=majority"
)

try:
    mongo_client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
        readPreference="secondaryPreferred"
    )
    mongo_client.server_info()  # Test connection
    mongo_db = mongo_client["cloud_db"]
    mongo_collection = mongo_db["BACK_COVER_ASSY"]
    print("✅ MongoDB Atlas Connected")
except Exception as e:
    print("❌ MongoDB Atlas Connection Failed:", e)
    mongo_collection = None

# ================= FLASK ROUTES =================
@app.route("/")
def root():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Username or Password")
    return render_template_string("""
        <h2>Login</h2>
        <form method="post">
            <input name="username" placeholder="Username" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul>
            {% for msg in messages %}
              <li>{{ msg }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
    """)

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if mongo_collection:
        try:
            docs = list(
                mongo_collection.find({}, {"_id":0})
                .sort("datetime",-1)
                .limit(200)
            )
        except Exception as e:
            print("❌ Mongo read error:", e)
            docs = []
    else:
        docs = []

    return render_template_string("""
        <h2>Dashboard</h2>
        <a href="{{ url_for('logout') }}">Logout</a>
        <table border="1">
            <tr>
                {% if docs %}
                    {% for key in docs[0].keys() %}
                        <th>{{ key }}</th>
                    {% endfor %}
                {% endif %}
            </tr>
            {% for doc in docs %}
                <tr>
                    {% for value in doc.values() %}
                        <td>{{ value }}</td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </table>
    """, docs=docs)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Server running → http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
