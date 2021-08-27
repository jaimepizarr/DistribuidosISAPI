from rest_framework import permissions
from .authentications import JWTLocalAuthentication

class OperadorAuthenticated(permissions.BasePermission):
    
    def has_permission(self, request):
        return  request.user and  request.user.is_authenticated and request.user.is_operador


class LocalAuthenticated(permissions.BasePermission):
    def has_permission(self, request,view):
        authentication = JWTLocalAuthentication()
        auth = authentication.authenticate(request)
        request.data["local"]= auth[0].ruc
        return auth is not None