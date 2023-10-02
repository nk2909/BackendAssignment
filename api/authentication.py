from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from .models import NonBuiltInUserToken


class UserTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        try:
            token = request.headers.get("Authorization")
            access_token = token.split(" ")[1]

        except:
            raise exceptions.AuthenticationFailed("Authentication Token require")

        if not token:
            return None

        try:
            access_token = token.split(" ")[1]
            user = NonBuiltInUserToken.objects.get(key=access_token)

        except IndexError as e:
            raise exceptions.AuthenticationFailed("Token Perfix missing") from e

        except NonBuiltInUserToken.DoesNotExist as e:
            raise exceptions.AuthenticationFailed("Token is Invalid") from e

        return (user.user, None)
