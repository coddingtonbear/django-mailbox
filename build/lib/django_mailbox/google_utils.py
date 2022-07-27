import logging

from django.conf import settings
import requests
from social.apps.django_app.default.models import UserSocialAuth


logger = logging.getLogger(__name__)


class AccessTokenNotFound(Exception):
    pass


class RefreshTokenNotFound(Exception):
    pass


def get_google_consumer_key():
    return settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY


def get_google_consumer_secret():
    return settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET


def get_google_access_token(email):
    # TODO: This should be cacheable
    try:
        me = UserSocialAuth.objects.get(uid=email, provider="google-oauth2")
        return me.extra_data['access_token']
    except (UserSocialAuth.DoesNotExist, KeyError):
        raise AccessTokenNotFound


def update_google_extra_data(email, extra_data):
    try:
        me = UserSocialAuth.objects.get(uid=email, provider="google-oauth2")
        me.extra_data = extra_data
        me.save()
    except (UserSocialAuth.DoesNotExist, KeyError):
        raise AccessTokenNotFound


def get_google_refresh_token(email):
    try:
        me = UserSocialAuth.objects.get(uid=email, provider="google-oauth2")
        return me.extra_data['refresh_token']
    except (UserSocialAuth.DoesNotExist, KeyError):
        raise RefreshTokenNotFound


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
