from django.contrib.auth.backends import ModelBackend


class CustomAuthBackend(ModelBackend):
    def get_user(self, user_id):
        user = super().get_user(user_id)
        if user:
            user.default_api_client = user.opnsenseapiclient_set.filter(is_default=True).first()
            user.open_sense_api_clients = user.opnsenseapiclient_set.all()
        return user

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user:
            user.default_api_client = user.opnsenseapiclient_set.filter(is_default=True).first()
            user.open_sense_api_clients = user.opnsenseapiclient_set.all()

        return user
