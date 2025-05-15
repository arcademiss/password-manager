class Credentials:
    def __init__(self, title, username, password, last_modified, nonce):
        self.title = title
        self.username = username
        self.password = password
        self.last_modified = last_modified
        self.nonce = nonce

    def set_username(self, username):
        self.username = username

    def set_title(self, title):
        self.title = title

    def set_password(self, password):
        self.password = password

    def set_last_modified(self, last_modified):
        self.last_modified = last_modified

    def get_title(self):
        return self.title

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_last_modified(self):
        return self.last_modified

    def __repr__(self):
        return f"Credentials(title='{self.title}', username='{self.username}')"
