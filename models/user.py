import hashlib


class User:
    def set_basic_info(self, id, first_name: str):
        t_hashed = hashlib.sha256(first_name.encode())
        self.user_id = id
        self.first_name = t_hashed.hexdigest()
