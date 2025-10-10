from flask import Flask, request, render_template
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    dbname="mydatabase",
    user="myuser",
    password="mypassword",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name").lower()
        answer = request.form.get("answer")

        if name and answer:
            cur.execute (
                "INSERT INTO answers (name, answer) VALUES (%s, %s)",
                (name, answer)
            )
            conn.commit()
            return f"Thanks, {name}! Your answer has been saved"
        
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    answers = None
    if request.method == "POST":
        name = request.form.get("name").lower()
        if name:
            cur.execute("SELECT name, answer FROM answers WHERE name = %s", (name,))
            answers = cur.fetchall()

    return render_template("login.html", answers=answers)

if __name__ == "__main__":
    app.run(debug=True)