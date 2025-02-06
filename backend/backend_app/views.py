from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UserInfo, Topics, Tags, Courses, Lessons, AppliedTags, Pages, Uploaded
from .serializers import UserInfoSerializer, TopicSerializer, TagSerializer, CourseSerializer, LessonSerializer, AppliedTagSerializer, PageSerializer, UploadedSerializer

class UserInfoViewAll(viewsets.ModelViewSet):
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer

class TopicViewAll(viewsets.ModelViewSet):
    queryset = Topics.objects.all()
    serializer_class = TopicSerializer

class TagViewAll(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer

class CourseViewAll(viewsets.ModelViewSet):
    queryset = Courses.objects.all()
    serializer_class = CourseSerializer

class LessonViewAll(viewsets.ModelViewSet):
    queryset = Lessons.objects.all()
    serializer_class = LessonSerializer

class AppliedTagViewAll(viewsets.ModelViewSet):
    queryset = AppliedTags.objects.all()
    serializer_class = AppliedTagSerializer

class PageViewAll(viewsets.ModelViewSet):
    queryset = Pages.objects.all()
    serializer_class = PageSerializer

class UploadedViewAll(viewsets.ModelViewSet):
    queryset = Uploaded.objects.all()
    serializer_class = UploadedSerializer