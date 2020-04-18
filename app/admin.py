from django.contrib import admin
from app.models import Post, UserProfile, Topic, Category, Vote, BlogSuggestion
from django.db.models import ManyToOneRel, ForeignKey, OneToOneField

# Register your models here.

ShowAllAdminFeilds = lambda model: type('SubClass'+model.__name__, (admin.ModelAdmin,), {
    'list_display': [x.name for x in model._meta.fields],
    'list_select_related': [x.name for x in model._meta.fields if isinstance(x, (ManyToOneRel, ForeignKey, OneToOneField,))]
})


admin.site.register(Post, ShowAllAdminFeilds(Post))
admin.site.register(Topic, ShowAllAdminFeilds(Topic))
admin.site.register(Category, ShowAllAdminFeilds(Category))
admin.site.register(Vote, ShowAllAdminFeilds(Vote))
admin.site.register(UserProfile, ShowAllAdminFeilds(UserProfile))
admin.site.register(BlogSuggestion, ShowAllAdminFeilds(BlogSuggestion))


