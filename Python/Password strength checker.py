print("This application will tell you the strength of your password based on a scale 1-5")

user_password = input("Enter your password: ")

import re
very_weak = r"^[a-z]+$|^[A-Z]+$|^[0-9]{1,6}$|^.{1,5}$" #Explanation: ^[a-z]+$ only lowercase letters any lenght, ^[A-Z]+$ same as lowercase condition ^[0-9]{1,6}$ only digits up to 6 characters ^.{1,5}% any combination but < 5 total

if re.fullmatch(very_weak, user_password):
    print("Very weak")
else:
    print("Looks strong")