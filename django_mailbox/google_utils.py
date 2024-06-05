import logging

from django.conf import settings
import requests
from social.apps.django_app.default.models import UserSocialAuth
try:
    from allauth.socialaccount.models import SocialAccount, SocialApp
except ImportError:
    SocialAccount, SocialApp = None, None

logger = logging.getLogger(__name__)


class AccessTokenNotFound(Exception):
    pass


class RefreshTokenNotFound(Exception):
    pass


def get_google_consumer_key():
    if SocialApp:
        app = SocialApp.objects.filter(provider='google').first()
        if app:
            return app.client_id
    return settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY


def get_google_consumer_secret():
    if SocialApp:
        app = SocialApp.objects.filter(provider='google').first()
        if app:
            return app.secret
    return settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET


def get_google_account(email, key=None):
    try:
        if SocialAccount:
            me = SocialAccount.objects.get(uid=email, provider='google')
        else:
            me = UserSocialAuth.objects.get(uid=email, provider="google-oauth2")
        return me.extra_data[key] if key else me
    except (UserSocialAuth.DoesNotExist, SocialAccount.DoesNotExist, KeyError):
        raise RefreshTokenNotFound if key == 'refresh_token' else AccessTokenNotFound


def get_google_access_token(email):
    # TODO: This should be cacheable
    return get_google_account(email, key='access_token')


def update_google_extra_data(email, extra_data):
    me = get_google_account(email)
    me.extra_data = extra_data
    me.save()


def get_google_refresh_token(email):
    return get_google_account(email, key='refresh_token')


def google_api_get(email, url):
    headers = dict(
        Authorization="Bearer %s" % get_google_access_token(email),
    )
    r = requests.get(url, headers=headers)
    logger.info("I got a %s", r.status_code)
    if r.status_code == 401:
        # Go use the refresh token
        refresh_authorization(email)
        r = requests.get(url, headers=headers)
        logger.info("I got a %s", r.status_code)
    if r.status_code == 200:
        try:
            return r.json()
        except ValueError:
            return r.text


def google_api_post(email, url, post_data, authorized=True):
    # TODO: Make this a lot less ugly. especially the 401 handling
    headers = dict()
    if authorized is True:
        headers.update(dict(
            Authorization="Bearer %s" % get_google_access_token(email),
        ))
    r = requests.post(url, headers=headers, data=post_data)
    if r.status_code == 401:
        refresh_authorization(email)
        r = requests.post(url, headers=headers, data=post_data)
    if r.status_code == 200:
        try:
            return r.json()
        except ValueError:
            return r.text


def refresh_authorization(email):
    refresh_token = get_google_refresh_token(email)
    post_data = dict(
        refresh_token=refresh_token,
        client_id=get_google_consumer_key(),
        client_secret=get_google_consumer_secret(),
        grant_type='refresh_token',
    )
    results = google_api_post(
        email,
        "https://accounts.google.com/o/oauth2/token?access_type=offline",
        post_data,
        authorized=False)
    results.update({'refresh_token': refresh_token})
    update_google_extra_data(email, results)


def fetch_user_info(email):
    result = google_api_get(
        email,
        "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
    )
    return result
