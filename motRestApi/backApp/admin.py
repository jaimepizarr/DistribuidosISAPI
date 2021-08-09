from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from backApp.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None,{"fields":("is_operador","is_motorizado")}),
        )
    