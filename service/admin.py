
from django.contrib import admin
from .models import CustomUser, Opportunity, Application


admin.site.register(CustomUser)
admin.site.register(Opportunity)
admin.site.register(Application)