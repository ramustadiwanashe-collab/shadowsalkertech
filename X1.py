from flask import Flask, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------- CREATE APP FIRST ----------------
app = Flask(__name__)
app.secret_key = "shadowwalker_secret"

# ---------------- DATABASE CONFIG ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ---------------- DATABASE MODELS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Create tables
with app.app_context():
    db.create_all()

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return """
    <h1>ShadowWalkerTech</h1>
    <a href='/login'>Login</a> |
    <a href='/register'>Create Account</a>
    """

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        if User.query.filter_by(username=username).first():
            return "User already exists"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return """
    <h2>Create Account</h2>
    <form method='POST'>
        Username:<br>
        <input name='username' required><br>
        Password:<br>
        <input type='password' name='password' required><br><br>
        <button type='submit'>Register</button>
    </form>
    """

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return """
    <h2>Login</h2>
    <form method='POST'>
        Username:<br>
        <input name='username' required><br>
        Password:<br>
        <input type='password' name='password' required><br><br>
        <button type='submit'>Login</button>
    </form>
    """

# ---------------- DASHBOARD WITH NOTES ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(username=session["user"]).first()

    # Add note
    if request.method == "POST":
        content = request.form["note"]
        if content.strip() != "":
            new_note = Note(content=content, user_id=user.id)
            db.session.add(new_note)
            db.session.commit()

    notes = Note.query.filter_by(user_id=user.id).all()

    notes_html = ""
    for note in notes:
        notes_html += f"""
        <div style='background:#111;color:#0f0;padding:10px;margin:10px;border-radius:5px;'>
            {note.content}
            <br>
            <a href='/delete/{note.id}' style='color:red;'>Delete</a>
        </div>
        """

    return f"""
    <h1>Welcome {session['user']} 🔥</h1>
    <h2>📘 Ethical Hacking Notes</h2>

    <form method='POST'>
        <textarea name='note' rows='4' cols='50' placeholder='Write ethical hacking notes...' required></textarea><br><br>
        <button type='submit'>Add Note</button>
    </form>

    <hr>
    {notes_html}

    <br>
    <a href='/logout'>Logout</a>
    """

# ---------------- DELETE NOTE ----------------
@app.route("/delete/<int:note_id>")
def delete(note_id):
    if "user" not in session:
        return redirect("/login")

    note = Note.query.get(note_id)
    if note:
        db.session.delete(note)
        db.session.commit()

    return redirect("/dashboard")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)