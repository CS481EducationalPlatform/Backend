from django.db import models

#An entity that allows for User Information to Better Identify Users of the Application
class UserInfo(models.Model):
    UserID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for User Identification
    Email = models.EmailField(unique=True, max_length=320, null=False) #Not Null field, for User Email
    Password = models.CharField(max_length=100, null=False) #Not Null field, for User Password, Needs to be encrypted later
    IsTeacher = models.BooleanField(default=False) #Not Null field, for Teacher Designation, Students first then Teacher

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"User : {self.UserID} : Has Email : {self.Email} : And Is A : {'Student' if self.IsTeacher else 'Teacher'}"

#An entity that allows for Topic Creation before applying to a Course, as this should enable easy addition of Topics
class Topics(models.Model):
    TopicID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for Topic Identification
    TopicName = models.CharField(max_length=100, null=False) #Not Null field, for Topic Designation

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"Topic : {self.TopicName} : Has ID : {self.TopicID}"

#An entity that allows for Tag Creation before applying multiple to a Course, as this allows easy addition of Tags and applying multiple per Course
class Tags(models.Model):
    TagID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for Tag Identification
    TagName = models.CharField(max_length=100, null=False) #Not Null field, for Tag Designation

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"Tag : {self.TagName} : Has ID : {self.TagID}"

#An entity that allows for one User to create multiple Courses, and for Courses to have overlapping names, use an existing Topic, and be approved by Admin
#Deleting a Course results in all Lessons->Pages->Files being deleted as well attached to that CourseID
class Courses(models.Model):
    UserID = models.ForeignKey(UserInfo, on_delete=models.PROTECT,null=False) #Foreign Key to UserInfo to designate Course to a User for Management Purposes
    CourseID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for Course Identification
    CourseName = models.CharField(max_length=100, null=False) #Not Null field, for Course Designation
    CourseDescription = models.TextField(null=False) #Not Null field, for Course Description for Users
    TopicID = models.ForeignKey(Topics, on_delete=models.PROTECT) #Foreign Key to Topics to desingate Course Topic for Searching and Naviation Purposes
    IsApproved = models.BooleanField(default=False) #Not Null field, for Approval of Course Visibility by Administrators

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['UserID', 'CourseName'], name='UniqueCourseNamePerUser')
        ]
        
    def __str__(self):
        return f"Course : {self.CourseName} : Has ID : {self.CourseID} : Of Topic : {self.TopicID.TopicName if self.TopicID is not None else 'Not Found'} : And User : {self.UserID.UserID if self.UserID is not None else 'Not Found'}"

#An entity that allows for one Course to have multiple Lessons
class Lessons(models.Model):
    CourseID = models.ForeignKey(Courses, on_delete=models.CASCADE, null=False) #Foreign Key to Courses to designate Lessons to a Course
    LessonID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for Lesson Identification
    LessonName = models.CharField(max_length=100, null=False) #Not Null field, for Lesson Designation
    LessonDescription = models.TextField(null=False) #Not Null field, for Lesson Description for Users

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"Lesson : {self.LessonName} : Has ID : {self.LessonID} : Of Course : {self.CourseID.CourseID if self.CourseID is not None else 'Not Found'}"

# As Django appears to have issues with Composite Primary Keys,
#  I am choosing to instead enforce searchable uniqueness for queries
#   What this means is that "id" will auto generate
#   And instead the supposed "primary_key" will be enforced unique
#An entity that allows for one Course to have multiple Tags that come from existing Tags entity
class AppliedTags(models.Model):
    CourseID = models.ForeignKey(Courses, on_delete=models.PROTECT, null=False) #Foreign Key to Courses to designate Applied Tag to a Course
    TagID = models.ForeignKey(Tags, on_delete=models.PROTECT, null=False) #Foreign Key to Tags to designate Applied Tags to an existing Tag

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['CourseID', 'TagID'], name='UniqueApplyTag')
        ]
        
    def __str__(self):
        return f"Course : {self.CourseID.CourseName if self.CourseID is not None else 'Not Found'} : Has Tag : {self.TagID.TagName if self.TagID is not None else 'Not Found'}"

#An entity that allows for one Lesson to have multiple Pages or screens to display within that lesson 
# (This entity could be removed if needed and instead have LessonID go into Uploaded directly)
class Pages(models.Model):
    LessonID = models.ForeignKey(Lessons, on_delete=models.CASCADE, null=False) #Foreign Key to Lessons to designate Page to a Lesson
    PageID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for Page Identification
    PageName = models.CharField(max_length=100, null=False) #Not Null field, for Page Designation
    PageDescription = models.TextField(null=False) #Not Null field, for Page Description for Users

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"Page : {self.PageName} : Has ID : {self.PageID} : Of Lesson : {self.LessonID.LessonID if self.LessonID is not None else 'Not Found'}"

#An entity that allows for one Page (Lesson possibly) to have multiple Uploaded Files or Videos
class Uploaded(models.Model):
    PageID = models.ForeignKey(Pages, on_delete=models.CASCADE, null=False) #Foreign Key to Pages to designate File to a Page
    FileID = models.AutoField(primary_key=True) #Auto Increment, Primary Key, for File Identification
    #Below is one or the other, one will be null, the other will be full
    VideoURL = models.CharField(max_length=100, null=True, blank=True) #For YT Embed if Page contains one
    FileBlob = models.BinaryField(null=True, blank=True) #For File Blob if Page contains one

    class Meta:
        constraints = [
            
        ]
        
    def __str__(self):
        return f"Page : {self.PageID.PageID if self.PageID is not None else 'Not Found'} : Has File ID : {self.FileID} : Of Type {'Video' if self.VideoURL is not None else 'File'} : {self.VideoURL if self.VideoURL is not None else self.FileBlob}"