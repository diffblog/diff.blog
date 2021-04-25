from django.contrib import admin
from app.models import Post, UserProfile, Topic, Category, Vote, BlogSuggestion
from django.db.models import ManyToOneRel, ForeignKey, OneToOneField

# Register your models here.

show_all_admin_fields = lambda model: type(
    "SubClass" + model.__name__,
    (admin.ModelAdmin,),
    {
        "list_display": [x.name for x in model._meta.fields],
        "list_select_related": [
            x.name
            for x in model._meta.fields
            if isinstance(
                x,
                (
                    ManyToOneRel,
                    ForeignKey,
                    OneToOneField,
                ),
            )
        ],
    },
)

show_blog_suggestion_fields = lambda model: type(
    "SubClass" + model.__name__,
    (admin.ModelAdmin,),
    {
        "list_display": [x.name for x in model._meta.fields],
        "list_editable": ["status"],
        "list_select_related": [
            x.name
            for x in model._meta.fields
            if isinstance(
                x,
                (
                    ManyToOneRel,
                    ForeignKey,
                    OneToOneField,
                ),
            )
        ],
    },
)

admin.site.register(Post, show_all_admin_fields(Post))
admin.site.register(Topic, show_all_admin_fields(Topic))
admin.site.register(Category, show_all_admin_fields(Category))
admin.site.register(Vote, show_all_admin_fields(Vote))
admin.site.register(UserProfile, show_all_admin_fields(UserProfile))
admin.site.register(BlogSuggestion, show_blog_suggestion_fields(BlogSuggestion))
