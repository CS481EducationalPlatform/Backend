from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserInfoViewAll, TopicViewAll, TagViewAll, CourseViewAll,
    LessonViewAll, AppliedTagViewAll, AppliedTopicViewAll, UploadedViewAll,
)

router = DefaultRouter()
router.register(r'userinfo', UserInfoViewAll, basename="userinfo")
router.register(r'topics', TopicViewAll, basename="topics")
router.register(r'tags', TagViewAll, basename="tags")
router.register(r'courses', CourseViewAll, basename="courses")
router.register(r'lessons', LessonViewAll, basename="lessons")
router.register(r'appliedtags', AppliedTagViewAll, basename="appliedtags")
router.register(r'uploaded', UploadedViewAll, basename="uploaded")
router.register(r'appliedtopics', AppliedTopicViewAll, basename="appliedtopics")

urlpatterns = [
    path('', include(router.urls)),
]
