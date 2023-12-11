
# cookieapp/authenticate.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions


def enforce_csrf(request):
    check = CSRFCheck()
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
 

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # print("git heree")
        header = self.get_header(request)
        # print("git heree", header)
        if header is None:
            raise exceptions.AuthenticationFailed("Invalid token")

        raw_token = self.get_raw_token(header)

        if raw_token is None:
            raise exceptions.AuthenticationFailed("Invalid token")

        validated_token = self.get_validated_token(raw_token)

        # print(raw_token, validated_token)

        return self.get_user(validated_token), validated_token
