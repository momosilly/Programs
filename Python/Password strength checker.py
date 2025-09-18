print("This application will tell you the strength of your password based on a scale 1-5")

user_password = input("Enter your password: ")

import re
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

if sets == 1 and 1 <= length <= 5:
    print("Very Weak")
elif 1 <= sets <= 2 and 5 <= length <= 8:
    print("Weak")
elif 2 <= sets <= 3 and 8 <= length <= 10:
    print("Moderate")
elif 3 <= sets <= 4 and 8 <= length <= 12:
    print("Strong")
elif sets == 4 and length >= 12:
    print("Very strong")