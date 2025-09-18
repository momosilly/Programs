from flask import Flask, render_template, request
import re
import secrets
import string
#print("This application will tell you the strength of your password based on a scale 1-5")

#password = input("Enter your password: ")

app = Flask(__name__)

def check_strength(password):

    sets = 0

    if re.search(r"[a-z]", password):
        sets += 1
    if re.search(r"[A-Z]", password):
        sets += 1
    if re.search(r"\d", password):
        sets += 1
    if re.search(r"[!@#$%^&*()_+\-=\[\]{}:;\"'<>,.?/]", password):
        sets += 1

    length = len(password)

    if sets == 1 and 1 <= length <= 5:
        return "Very Weak, scale 1"
    elif 1 <= sets <= 2 and 5 <= length <= 8:
        return "Weak, scale 2"
    elif 2 <= sets <= 3 and 8 <= length <= 10:
        return "Moderate, scale 3"
    elif 3 <= sets <= 4 and 8 <= length <= 12:
        return "Strong, scale 4"
    elif sets == 4 and length >= 12:
        return "Very strong, scale 5"
    else:
        return "Invalid or unsupported password format"

def generate_pass(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation

    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

@app.route("/", methods=['GET', 'POST'])
def index():
    strength = None
    new_password = None
    if request.method == "POST":
        user_password = request.form['password']
        strength = check_strength(user_password)
        if "Weak" in strength or "Very Weak" in strength or "Moderate" in strength:
            if request.form == 'yes':
                new_password = generate_pass()
        return render_template('index.html', strength=strength, new_password=new_password)
if __name__ == '__main__':
    app.run(debug=True)