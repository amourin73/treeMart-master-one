from django.contrib import admin

# Register your models here.
from .models import Cart
from.models import Tree

admin.site.register(Tree)
admin.site.register(Cart)