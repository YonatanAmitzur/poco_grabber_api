from uuid import uuid4
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'poco_common.core'

    def ready(self):
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in
        user_logged_in.disconnect(update_last_login)  # needed for django<2.0
        user_logged_in.disconnect(dispatch_uid='update_last_login')  # needed for django>=2.0
        user_logged_in.connect(set_new_session_key_signal)


def set_new_session_key_signal(sender, user, request, **kwargs):
    """
     Setting new session key contains the user id when user login.
     Generate the session key and set the session key in request.session object.
    """
    current_session_key = request.session.session_key
    new_session_key = f'_{user.slug}_poco_sessions_{uuid4().hex}'
    request.session._session_key = new_session_key
    # Save the new session key in redis cache
    request.session.save(must_create=True)
    # Remove the old session key from redis cache
    if current_session_key:
        request.session.delete(current_session_key)
