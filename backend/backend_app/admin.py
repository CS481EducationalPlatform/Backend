from django.contrib import admin
from .models import UserInfo, Instructor, Topics, Courses, Lessons, Rating, Tags, TopicTag, CourseTag, LessonTag, Uploaded

#Register ability for admins to view entities
admin.site.register(UserInfo)
admin.site.register(Instructor)
admin.site.register(Topics)
admin.site.register(Courses)
admin.site.register(Lessons)
admin.site.register(Rating)
admin.site.register(Tags)
admin.site.register(TopicTag)
admin.site.register(CourseTag)
admin.site.register(LessonTag)
admin.site.register(Uploaded)
