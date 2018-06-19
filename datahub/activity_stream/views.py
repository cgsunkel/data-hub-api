import logging

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.utils.crypto import constant_time_compare
from django.utils.decorators import decorator_from_middleware
from mohawk import Receiver
from mohawk.exc import HawkFail
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


logger = logging.getLogger(__name__)

NO_CREDENTIALS_MESSAGE = 'Authentication credentials were not provided.'
INCORRECT_CREDENTIALS_MESSAGE = 'Incorrect authentication credentials.'


def _lookup_credentials(access_key_id):
    """Raises a HawkFail if the passed ID is not equal to
    settings.ACTIVITY_STREAM_ACCESS_KEY_ID
    """
    if not constant_time_compare(access_key_id,
                                 settings.ACTIVITY_STREAM_ACCESS_KEY_ID):
        raise HawkFail(f'No Hawk ID of {access_key_id}')

    return {
        'id': settings.ACTIVITY_STREAM_ACCESS_KEY_ID,
        'key': settings.ACTIVITY_STREAM_SECRET_ACCESS_KEY,
        'algorithm': 'sha256',
    }


def _seen_nonce(access_key_id, nonce, _):
    """Returns if the passed access_key_id/nonce combination has been
    used within settings.ACTIVITY_STREAM_NONCE_EXPIRY_SECONDS
    """
    cache_key = f'activity_stream:{access_key_id}:{nonce}'
    seen_cache_key = cache.get(cache_key, False)

    # cache.add only adds key if it isn't present
    cache.add(cache_key, True,
              timeout=settings.ACTIVITY_STREAM_NONCE_EXPIRY_SECONDS)

    if seen_cache_key:
        logger.warning(f'Already seen nonce {nonce}')

    return seen_cache_key


def _authorise(request):
    """Raises a HawkFail if the passed request cannot be authenticated"""
    return Receiver(
        _lookup_credentials,
        request.META['HTTP_AUTHORIZATION'],
        request.build_absolute_uri(),
        request.method,
        content=request.body,
        content_type=request.content_type,
        seen_nonce=_seen_nonce,
    )


class _ActivityStreamUser(AnonymousUser):
    """The User for Hawk-authenticated ActivityStream requests"""

    username = 'activity_stream_user'

    def __init__(self, hawk_receiver):
        """Sets the hawk receiver, which is used to set the
        Server-Authorization header
        """
        self.hawk_receiver = hawk_receiver

    @property
    def is_authenticated(self):
        """Return True unconditionally, since the User is only created
        after authentication
        """
        return True


class _ActivityStreamAuthentication(BaseAuthentication):

    def authenticate_header(self, request):
        """This is returned as the WWW-Authenticate header when
        AuthenticationFailed is raised. DRF also requires this
        to send a 401 (as opposed to 403)
        """
        return 'Hawk'

    def authenticate(self, request):
        """Authenticates a request using two mechanisms:

        1. The X-Forwarded-For-Header, compared against a whitelist
        2. A Hawk signature in the Authorization header

        If either of these suggest we cannot authenticate, AuthenticationFailed
        is raised, as required in the DRF authentication flow
        """
        if 'HTTP_X_FORWARDED_FOR' not in request.META:
            logger.warning(
                'Failed authentication: no X-Forwarded-For header passed'
            )
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

        x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR']
        remote_address = x_forwarded_for.split(',', maxsplit=1)[0].strip()

        if remote_address not in settings.ACTIVITY_STREAM_IP_WHITELIST:
            logger.warning(
                'Failed authentication: the X-Forwarded-For header did not '
                'start with an IP in the whitelist'
            )
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

        if 'HTTP_AUTHORIZATION' not in request.META:
            raise AuthenticationFailed(NO_CREDENTIALS_MESSAGE)

        try:
            hawk_receiver = _authorise(request)
        except HawkFail as e:
            logger.warning(f'Failed authentication {e}')
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

        return (_ActivityStreamUser(hawk_receiver), None)


class _ActivityStreamHawkResponseMiddleware:
    """Adds the Server-Authorization header to the response, so the originator
    of the request can authenticate the response
    """

    def process_response(self, viewset, response):
        """Adds the Server-Authorization header to the response, so the originator
        of the request can authenticate the response
        """
        response['Server-Authorization'] = viewset.request.user.hawk_receiver.respond(
            content=response.content,
            content_type=response['Content-Type'],
        )
        return response


class ActivityStreamViewSet(ViewSet):
    """List-only view set for the activity stream"""

    authentication_classes = (_ActivityStreamAuthentication,)
    permission_classes = (IsAuthenticated,)

    @decorator_from_middleware(_ActivityStreamHawkResponseMiddleware)
    def list(self, request):
        """A single page of activities"""
        return Response({'secret': 'content-for-pen-test'})
