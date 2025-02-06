from rest_framework import serializers
from .models import UserInfo, Topics, Tags, Courses, Lessons, AppliedTags, Pages, Uploaded

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topics
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lessons
        fields = '__all__'

class AppliedTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedTags
        fields = '__all__'

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pages
        fields = '__all__'

class UploadedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uploaded
        fields = '__all__'