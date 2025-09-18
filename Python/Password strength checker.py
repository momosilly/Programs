print("This application will tell you the strength of your password based on a scale 1-5")

user_password = input("Enter your password: ")

import re
very_weak = r"^[0-9]$|^[a-z]{1,6}$|^[A-Z]{1,6}$|^.{1,5}$"

if re.fullmatch(very_weak, user_password):
    print("Very weak")
else:
    print("Looks strong")