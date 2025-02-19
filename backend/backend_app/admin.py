from django.contrib import admin
from .models import UserInfo, Topics, Tags, Courses, Lessons, AppliedTags, AppliedTopics, Uploaded

#Register ability for admins to view entities
admin.site.register(UserInfo)
admin.site.register(Topics)
admin.site.register(Tags)
admin.site.register(Courses)
admin.site.register(Lessons)
admin.site.register(AppliedTags)
admin.site.register(AppliedTopics)
admin.site.register(Uploaded)
