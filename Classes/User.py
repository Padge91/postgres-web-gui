

class User(object):
    min_password_length = 12
    supported_special_characters = "!?@$#&"
    supported_numbers = "1234567890"

    def __init__(self, username, password, date_created, date_modified=None, session=None, session_expire=None, admin=False):
        self.username = username
        self.password = self.validate_password(password)
        self.date_created = date_created
        self.date_modified = date_modified
        self.session = session
        self.session_expire = session_expire
        self.admin = admin

    @staticmethod
    def load_by_id(user_id):
        # get user fields
        return User()

    @staticmethod
    def load_by_session(session):
        return User()

    def validate_password(self, password):
        if len(password) < User.min_password_length:
            return "Password must be at least "+str(User.min_password_length)+" characters."

        found = False
        for i in range(0, len(password)):
            if password[i] in User.supported_special_characters:
                found = True
                break
        if not found:
            raise Exception("Password must include at least one special character ("+str(User.supported_special_characters)+").")

        found = False
        for i in range(0, len(password)):
            if password[i] in User.supported_numbers:
                found = True
                break
        if not found:
            raise Exception("Password must include at least one number.")

        return password

    def persist(self):
        # save to db
        return True



