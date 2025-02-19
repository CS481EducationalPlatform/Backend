from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator, MaxValueValidator

#An entity that allows for User Information to Better Identify Users of the Application
class UserInfo(models.Model):
    userID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for User Identification
    email = models.EmailField(unique=True, max_length=320, null=False) #Not Null field, for User Email
    username = models.CharField(max_length=100, null=True) #Nullable field, for User Username
    password = models.CharField(max_length=100, null=False) #Not Null field, for User Password, Needs to be encrypted later(?)
    isTeacher = models.BooleanField(default=False) #Not Null field, for Teacher Designation, Students first then Teacher

    def save(self, *args, **kwargs):
      # Hash the password before saving
      self.password = make_password(self.password)
      super().save(*args, **kwargs)

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"User : {self.userID} : Has UserName : {self.username} : Has Email : {self.email} : And Is A : {'Student' if self.isTeacher else 'Teacher'}"

#An entity that allows for Topic Creation before applying to a Course, as this should enable easy addition of Topics
class Topics(models.Model):
    topicID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for Topic Identification
    topicName = models.CharField(max_length=100, null=False) #Not Null field, for Topic Designation

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"Topic : {self.topicName} : Has ID : {self.topicID}"

#An entity that allows for Tag Creation before applying multiple to a Course, as this allows easy addition of Tags and applying multiple per Course
class Tags(models.Model):
    tagID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for Tag Identification
    tagName = models.CharField(max_length=100, null=False) #Not Null field, for Tag Designation

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"Tag : {self.tagName} : Has ID : {self.tagID}"

#An entity that allows for one User to create multiple Courses, and for Courses to have overlapping names, use an existing Topic, and be approved by Admin
#Deleting a Course results in all Lessons->Pages->Files being deleted as well attached to that CourseID
class Courses(models.Model):
    userID = models.ForeignKey(UserInfo, on_delete=models.PROTECT,null=False) #Foreign Key to UserInfo to designate Course to a User for Management Purposes
    courseID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for Course Identification
    courseName = models.CharField(max_length=100, null=False) #Not Null field, for Course Designation
    courseDescription = models.TextField(null=False) #Not Null field, for Course Description for Users
    isApproved = models.BooleanField(default=False) #Not Null field, for Approval of Course Visibility by Administrators
    rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['userID', 'courseName'], name='UniqueCourseNamePerUser')
        ]
        
    def __str__(self):
        return f"Course : {self.courseName} : Has ID : {self.courseID} : And User : {self.userID.userID if self.userID is not None else 'Not Found'} : With Description : {self.courseDescription} : Rating : {self.rating} : Approval : {self.isApproved}"

#An entity that allows for one Course to have multiple Lessons
class Lessons(models.Model):
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, null=False) #Foreign Key to Courses to designate Lessons to a Course
    lessonID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for Lesson Identification
    lessonName = models.CharField(max_length=100, null=False) #Not Null field, for Lesson Designation
    lessonDescription = models.TextField(null=False) #Not Null field, for Lesson Description for Users

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"Lesson : {self.lessonName} : Has ID : {self.lessonID} : Of Course : {self.courseID.courseID if self.courseID is not None else 'Not Found'}"

# As Django appears to have issues with Composite Primary Keys,
#  I am choosing to instead enforce searchable uniqueness for queries
#   What this means is that "id" will auto generate
#   And instead the supposed "primary_key" will be enforced unique
#An entity that allows for one Course to have multiple Tags that come from existing Tags entity
class AppliedTags(models.Model):
    courseID = models.ForeignKey(Courses, on_delete=models.PROTECT, null=False) #Foreign Key to Courses to designate Applied Tag to a Course
    tagID = models.ForeignKey(Tags, on_delete=models.PROTECT, null=False) #Foreign Key to Tags to designate Applied Tags to an existing Tag

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['courseID', 'tagID'], name='UniqueApplyTag')
        ]
        
    def __str__(self):
        return f"Course : {self.courseID.courseName if self.courseID is not None else 'Not Found'} : Has Tag : {self.tagID.tagName if self.tagID is not None else 'Not Found'}"

class AppliedTopics(models.Model):
    courseID = models.ForeignKey(Courses, on_delete=models.PROTECT, null=False) #Foreign Key to Courses to designate Applied Tag to a Course
    topicID = models.ForeignKey(Topics, on_delete=models.PROTECT, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['courseID', 'topicID'], name='UniqueApplyTopic')
        ]
        
    def __str__(self):
        return f"Course : {self.courseID.courseName if self.courseID is not None else 'Not Found'} : Has Tag : {self.topicID.topicName if self.topicID is not None else 'Not Found'}"

#An entity that allows for one Lesson to have multiple Uploaded Files or Videos
class Uploaded(models.Model):
    lessonID = models.ForeignKey(Lessons, on_delete=models.CASCADE, null=False) #Foreign Key to Lessons to designate File to a Lesson
    fileID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for File Identification
    #Below is one or the other, one will be null, the other will be full
    videoURL = models.CharField(max_length=100, null=True, blank=True) #For YT Embed if Page contains one
    fileBlob = models.BinaryField(null=True, blank=True) #For File Blob if Page contains one

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"Lesson : {self.lessonID.lessonID if self.lessonID is not None else 'Not Found'} : Has File ID : {self.fileID} : Of Type {'Video' if self.videoURL is not None else 'File'} : {self.videoURL if self.videoURL is not None else self.fileBlob}"
    