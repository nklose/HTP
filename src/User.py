class User:

    def __init__(self, username, email, password, handle):
        self.username = ""
        self.email = ""
        self.password = ""
        self.handle = ""

    def set_user(self, username):
        cursor = con.cursor()
        # name cannot be blank
        if username == "":
            error("You must enter a username.")
            return False
        # name must be alphanumeric; symbols are rejected prior to database lookup
        elif not username.isalnum():
            error("Your username can only contain letters and numbers.")
            return False
        # name must be between 4 and 16 characters
        elif len(username) < 4 or len(username) > 16:
            error("Your username must be between 4 and 16 characters.")
            return False
        # name must not already exist in database
        else:
            sql = "SELECT * FROM users WHERE username = %s;"
            database = Database()
            database.execute_query(sql, username)
