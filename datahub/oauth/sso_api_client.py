from django.conf import settings
from requests import RequestException
from rest_framework import serializers

from datahub.core.api_client import APIClient, TokenAuth


class SSORequestError(Exception):
    """An SSO API request error."""


class IntrospectionSerializer(serializers.Serializer):
    """
    Serializer used only to validate introspection responses.

    Note: This includes only the fields we care about.
    """

    active = serializers.BooleanField()
    username = serializers.CharField()
    email_user_id = serializers.EmailField()
    exp = serializers.IntegerField()


def introspect_token(token):
    """Get details about an access token from the introspection endpoint in Staff SSO."""
    return _request('post', 'o/introspect/', IntrospectionSerializer, data={'token': token})


def _request(method, path, response_serializer_class, **kwargs):
    """
    Internal utility function to make a generic API request to Staff SSO.

    As this deals with authentication, this aims to be more robust than might be the case
    for other API requests.
    """
    api_client = _get_api_client()

    try:
        response = api_client.request(method, path, **kwargs)
    except RequestException as exc:
        raise SSORequestError('SSO request failed') from exc

    try:
        response_data = response.json()
    except ValueError as exc:
        raise SSORequestError('SSO response parsing failed') from exc

    try:
        serializer = response_serializer_class(data=response_data)
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as exc:
        raise SSORequestError('SSO response validation failed') from exc

    return serializer.validated_data


def _get_api_client():
    return APIClient(
        settings.STAFF_SSO_BASE_URL,
        TokenAuth(settings.STAFF_SSO_AUTH_TOKEN, token_keyword='Bearer'),
        default_timeout=settings.STAFF_SSO_REQUEST_TIMEOUT,
    )