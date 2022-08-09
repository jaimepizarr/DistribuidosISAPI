from django.apps.registry import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from backApp.models import * 

# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     add_fieldsets = (
#         (None,{"fields":("is_operador","is_motorizado")}),
#         (None, {'fields': ('email', 'password')}),
#         )
#     ordering = ('email',)
admin.site.register(User)

admin.site.register(Local)
admin.site.register(Motorizado)
admin.site.register(Order)
admin.site.register(Location)
admin.site.register(Client)