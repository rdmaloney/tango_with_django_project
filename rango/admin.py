from django.contrib import admin

from rango.models import Category, Page
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
# Update the admin interface to auto populate the slug field
admin.site.register(Category, CategoryAdmin)

class PageAdmin(admin.ModelAdmin):
   list_display = ('title', 'category', 'url')

admin.site.register(Page, PageAdmin)
