from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Follow

User = get_user_model()

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('pk', 'username', 'email')
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по username и email'
    empty_value_display = settings.ADMIN_PAN_EMPTY_VALUE
    save_on_top = True
    actions = ['Delete', ]


@admin.register(Follow)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = settings.ADMIN_PAN_EMPTY_VALUE
    save_on_top = True
    actions = ['Delete', ]
