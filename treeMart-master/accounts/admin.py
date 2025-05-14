# from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'location', 'user_type')  # Replace 'is_normal_user' with 'user_type'
    list_filter = ('user_type',)  # Replace 'is_normal_user' with 'user_type'
    search_fields = ('user__username',)

admin.site.register(Profile, ProfileAdmin)
