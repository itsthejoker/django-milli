from django.contrib import admin

from .models import IgnoreMe, SaveMe

# Register your models here.

admin.site.register(SaveMe)
admin.site.register(IgnoreMe)
