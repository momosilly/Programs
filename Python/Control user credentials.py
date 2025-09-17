class UserInfo:
    def __init__(self):
        self.username = input("Create a username: ")
        self.password = input("Create a password: ")

    def login(self):
        username_input = input("Enter your username to log in: ")
        password_input = input("Enter your password to log in: ")
        self.check_username(username_input, password_input)
        
    def check_username(self, username_to_check, password_to_check):
        if username_to_check == self.username and password_to_check == self.password:
            print("You gained access! Welcome to our amazing platfrom")
            return True
        else:
            print("You didnt gain access")
            return False
   
user = UserInfo()
user.login()
print("Edited")