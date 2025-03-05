from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator, MaxValueValidator

# --- USER RELATED MODELS ---

"""
UserInfo model represents a user in the system
- userID: Primary Key for the user, automatically generated as an auto-incrementing field
- username: the user's choosen username, cannot be null
- password: the user's password, hashed before being stored. Cannot be null
- email: the user's email address, must be unqiue and cannot be null
"""
class UserInfo(models.Model):
    userID = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, null=False)
    password = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True, max_length=320, null=False)  

    def save(self, *args, **kwargs):
        # Hash the password before saving
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            
        ]

    # prints info of the UserInfo instance for the class
    def __str__(self):
        return f"userID : {self.userID} : username : {self.username} : email : {self.email}"

"""
Used to associate a user (from the UserInfo model) with the role of an instructor
- instructorID: Primary Key for the instructor, automatically generated as an auto-incrementing field
- userID: Foreign Key linking the instructor to a user from the UserInfo model. On deletion of the user, the instructor is also deleted.
"""
class Instructor(models.Model):
    instructorID = models.AutoField(primary_key=True)  
    userID = models.ForeignKey(UserInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f"instructorID : {self.instructorID} : userID : {self.userID.userID} : username : {self.userID.username}"

# --- COURSE RELATED MODELS ---

"""
Used to categorize/ group/ organize courses based on a specific subject
- topicID: Primary key for topics, automatically generated as an auto-incrementing field
- topicName: The name of the topic, must be unique and cannot be null
"""
class Topics(models.Model):
    topicID = models.AutoField(primary_key=True)
    topicName = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return f"topicID : {self.topicID} : topicName : {self.topicName}"

"""
Courses model represents the information about a course
- instructorID: Foreign Key linking to the Instructor model
- courseID: Primary key for the course, automatically generated as an auto-incrementing field
- courseName: The name of the course, cannot be null
- courseDecription: The description of the course, cannot be null
- isPublished: A boolean field indicating whether the course is published
"""
class Courses(models.Model):
    instructorID = models.ForeignKey(Instructor, on_delete=models.CASCADE, null=False)  
    courseID = models.AutoField(primary_key=True)  
    courseName = models.CharField(max_length=100, null=False)  
    courseDescription = models.TextField(null=False)  
    isPublished = models.BooleanField(default=False)  

    def __str__(self):
        return f"courseID : {self.courseID} : courseName : {self.courseName} : instructorID : {self.instructorID.instructorID} : isPublished : {self.isPublished}"

"""
Lessons model can be associated with a course or created independently
- courseID: Foreign Key linking to the Courses model (nullable, allowing lessons to exist without a course)
- lessonID: Primary key for the lesson, automatically generated as an auto-incrementing field
- lessonName: The name of the lesson, cannot be null
- lessonDescription: A description of the lesson, cannot be null
"""
class Lessons(models.Model):
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True, blank=True)  
    lessonID = models.AutoField(primary_key=True)
    lessonName = models.CharField(max_length=100, null=False) 
    lessonDescription = models.TextField(null=False) 

    def __str__(self):
        return f"lessonName : {self.lessonName} : lessonID : {self.lessonID} : courseID : {self.courseID.courseID if self.courseID is not None else 'Not Found'}"

"""
Rating models represents a rating given to a course by a user
- courseID: Foreign Key linking to the Courses model, indicating which course is being rated
- rating: An integer field for the rating, valid ratings are between 1 and 5
"""
class Rating(models.Model):
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"Course : {self.courseID.courseName} : Rating : {self.rating}"

# --- TAG RELATED MODELS ---

"""
Tags models represents a tag that can be applied to topics, courses, and lessons (for searchable)
- tagID: Primary Key for the tag, automatically generated as an auto-incrementing field
- tagName: The name of the tag, must be unique and cannot be null
"""
class Tags(models.Model):
    tagID = models.AutoField(primary_key=True)
    tagName = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return f"Tag : {self.tagName}"

"""
TopicTag models represents the many-to-many relationship between topics and tags
- topicTagID: Primary Key, automatically generated as an auto-incrementing field
- topicID: Foreign Key linking to the Topics model
- tagID: Foreign Key linking to the Tags model
- unqiue_together: Ensures that each topics can only be associated with a specific tag once
"""
class TopicTag(models.Model):
    topicTagID = models.AutoField(primary_key=True)  
    topicID = models.ForeignKey(Topics, on_delete=models.CASCADE)
    tagID = models.ForeignKey(Tags, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('topicID', 'tagID')

    def __str__(self):
        return f"topicTagID : {self.topicTagID} : Topic : {self.topicID.topicName} : Tag : {self.tagID.tagName}"

"""
CourseTag model represents the many-to-many relationship between courses and tags
- courseTagID: Primary Key, automatically generated as an auto-incrementing field
- courseID: Foreign Key linking to the Courses model
- tagID: Foreign Key linking to the Tags model
- unique_together: Ensures that each course can only be assoicated with a specific tag once
"""
class CourseTag(models.Model):
    courseTagID = models.AutoField(primary_key=True)  
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE)
    tagID = models.ForeignKey(Tags, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('courseID', 'tagID')  

    def __str__(self):
        return f"courseTagID : {self.courseTagID} : Course : {self.courseID.courseName} : Tag : {self.tagID.tagName}"

"""
LessonTag model represents the many-to-many relationship between lessons and tags
- lessonTagID: Primary Key, automatically generated as an auto-incrementing field
- lessonID: Foreign Key linking to the Lessons model
- tagID: Foreign Key linking to the Tags model
- unqiue_together: Ensures that each lesson can only be associated with a specific tag once
"""
class LessonTag(models.Model):
    lessonTagID = models.AutoField(primary_key=True)  
    lessonID = models.ForeignKey(Lessons, on_delete=models.CASCADE)
    tagID = models.ForeignKey(Tags, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('lessonID', 'tagID')

    def __str__(self):
        return f"lessonTagID : {self.lessonTagID} : Lesson : {self.lessonID.lessonName} : Tag : {self.tagID.tagName}"

# --- UPLOAD RELATED MODELS ---

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
    