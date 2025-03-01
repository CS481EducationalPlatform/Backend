from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserInfoViewAll, InstructorViewAll, TopicViewAll, CourseViewAll,
    LessonViewAll, RatingViewAll, TagViewAll, TopicTagViewAll, 
    CourseTagViewAll, LessonTagViewAll, UploadedViewAll
)

router = DefaultRouter()
router.register(r'userinfo', UserInfoViewAll, basename="userinfo")
router.register(r'instructors', InstructorViewAll, basename="instructors")
router.register(r'topics', TopicViewAll, basename="topics")
router.register(r'courses', CourseViewAll, basename="courses")
router.register(r'lessons', LessonViewAll, basename="lessons")
router.register(r'ratings', RatingViewAll, basename="ratings")
router.register(r'tags', TagViewAll, basename="tags")
router.register(r'topic-tags', TopicTagViewAll, basename="topic-tags")
router.register(r'course-tags', CourseTagViewAll, basename="course-tags")
router.register(r'lesson-tags', LessonTagViewAll, basename="lesson-tags")
router.register(r'uploaded', UploadedViewAll, basename="uploaded")

urlpatterns = [
    path('', include(router.urls)),
]
