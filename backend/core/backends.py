import bcrypt
from neomodel import DoesNotExist
from .models import User


class NeomodelAuthBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.nodes.get(email=username)
            if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                return user
        except DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.nodes.get(uid=user_id)
        except DoesNotExist:
            return None
