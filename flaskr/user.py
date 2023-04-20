#User class which is used for logins
class User():

    def __init__(self, username):
        self.name = username

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.name)
        except AttributeError:
            raise NotImplementedError(
                "No 'id' attribute - override 'get_id'") from None