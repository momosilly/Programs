print("This application will tell you the strength of your password based on a scale 1-5")

user_password = input("Enter your password: ")

import re
import secrets
import string
sets = 0

if re.search(r"[a-z]", user_password):
    sets += 1
if re.search(r"[A-Z]", user_password):
    sets += 1
if re.search(r"\d", user_password):
    sets += 1
if re.search(r"[!@#$%^&*()_+\-=\[\]{}:;\"'<>,.?/]", user_password):
    sets += 1

length = len(user_password)

def generate_pass(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation

    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

if sets == 1 and 1 <= length <= 5:
    print("Very Weak, scale 1")
    if input("Your password is very weak, would you like to generate a stronger one? [yes, no] ") == "yes":
        print(f"Here's your new password: {generate_pass()}")
    else:
        pass
elif 1 <= sets <= 2 and 5 <= length <= 8:
    print("Weak, scale 2")
    if input("Your password is weak, would you like to generate a stronger one? [yes, no] ") == "yes":
        print(f"Here's your new password: {generate_pass()}")
    else:
        pass
elif 2 <= sets <= 3 and 8 <= length <= 10:
    print("Moderate, scale 3")
    if input("Your password is moderate, would you like to generate a stronger one? [yes, no] ") == "yes":
        print(f"Here's your new password: {generate_pass()}")
    else:
        pass
elif 3 <= sets <= 4 and 8 <= length <= 12:
    print("Strong, scale 4")
elif sets == 4 and length >= 12:
    print("Very strong, scale 5")
else:
    "Invalid or unsupported password format"