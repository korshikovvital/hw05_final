from django.contrib import admin
from .models import Post, Group,Comment


# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author','image', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)
