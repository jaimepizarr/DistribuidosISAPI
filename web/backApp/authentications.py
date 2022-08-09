import jwt
from django.conf import Settings, settings
from rest_framework import authentication, exceptions
from .models import Local


class JWTLocalAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'
    
    def authenticate(self, request):
        '''
        The `authenticate` method must be called on every request of the Rest API
        regardless of whether the endpoint requires authentication.
 
        `authenticate` has two possible return values:
 
        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this means we know authentication will fail. An example of
                    this is when the request does not include a token in the
                    headers.
 
        2) `(ruc, token)` - We return a ruc/token combination when
                             authentication is successful.
 
                            If neither case is met, that means there's an error
                            and we do not return anything.
                            We simple raise the `AuthenticationFailed`
                            exception and let Django REST Framework
                            handle the rest.
        '''
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None
        
        if len(auth_header) == 1 or len(auth_header)>2:
                return None
        
        prefix = auth_header[0].decode("utf-8").lower()
        token = auth_header[1].decode('utf-8')

        if prefix!=auth_header_prefix:
            return None
        return self._authenticate_credentials(request,token)

    def _authenticate_credentials(self,request,token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms=["HS256"])
        except:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            local = Local.objects.get(pk=payload["ruc"])
        except Local.DoesNotExist:
            msg= "No local matched the token"
            raise exceptions.AuthenticationFailed(msg)

        return (local,token)




