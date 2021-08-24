from rest_framework import permissions
from .authentications import JWTLocalAuthentication

class OperadorAuthenticated(permissions.BasePermission):
    
    def has_permission(self, request):
        return  request.user and  request.user.is_authenticated and request.user.is_operador


class LocalAuthenticated(permissions.BasePermission):

    def has_permission(self, request):
        auth = JWTLocalAuthentication.authenticate(request)
        return auth is not None