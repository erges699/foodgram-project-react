from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
    )
    list_display_links = ('username',)
    list_filter = ('username',)
    search_fields = ('username', 'email',)
    empty_value_display = '-пусто-'
    save_on_top = True
