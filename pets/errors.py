class UserNotFound(Exception):
    def __init__(self, msg='User not found'):
        super().__init__(msg)
        self.msg = msg


class PetNotFound(Exception):
    def __init__(self, msg='Pet not found'):
        super().__init__(msg)
        self.msg = msg
