from rest_framework import serializers
from .models import UserInfo, Instructor, Topics, Tags, Courses, Lessons, Rating, TopicTag, CourseTag, LessonTag, Uploaded

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topics
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__'

class UploadedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uploaded
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    uploads = UploadedSerializer(source='uploaded_set', many=True, read_only=True)
    
    class Meta:
        model = Lessons
        fields = ['lessonID', 'courseID', 'lessonName', 'lessonDescription', 'uploads']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'

class TopicTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicTag
        fields = '__all__'

class CourseTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTag
        fields = '__all__'

class LessonTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonTag
        fields = '__all__'
