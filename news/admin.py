from django.contrib import admin
from .models import Article, Category, Tag

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_date', 'sentiment_label')
    list_filter = ('category', 'published_date')
    search_fields = ('title', 'content')

admin.site.register(Category)
admin.site.register(Tag)