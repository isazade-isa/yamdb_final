from django.contrib import admin

from reviews.models import Category, Genre, Title, Review, Comment


class CategoryGenreAdmin(admin.ModelAdmin):
    list_display = (
        'slug',
        'name'
    )
    search_fields = ('slug',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'category'
    )
    search_fields = ('name',)
    list_filter = ('category',)
    empty_value_display = '-пусто-'


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'title',
        'text',
        'score',
        'pub_date'
    )
    search_fields = ('title',)
    list_filter = ('author', 'title')
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'review',
        'text',
        'pub_date'
    )
    search_fields = ('review',)
    list_filter = ('author', 'review')
    empty_value_display = '-пусто-'


admin.site.register(Category, CategoryGenreAdmin)
admin.site.register(Genre, CategoryGenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
