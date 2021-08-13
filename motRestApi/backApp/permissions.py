from rest_framework import permissions

class OperadorAuthenticated(permissions.BasePermission):
    
    def has_permission(self, request):
        return  request.user and  request.user.is_authenticated and request.user.is_operador

