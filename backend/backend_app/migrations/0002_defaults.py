from django.db import migrations, models

def create_basic_data(apps, schema_editor):
    # Get the models you want to populate data for
    UserInfo = apps.get_model('backend_app', 'UserInfo')
    Courses = apps.get_model('backend_app', 'Courses')
    Topics = apps.get_model('backend_app', 'Topics')
    Tags = apps.get_model('backend_app', 'Tags')
    AppliedTags = apps.get_model('backend_app', 'AppliedTags')
    Lessons = apps.get_model('backend_app', 'Lessons')
    Uploaded = apps.get_model('backend_app', 'Uploaded')
    AppliedTopics = apps.get_model('backend_app', 'AppliedTopics')

    topic1 = Topics.objects.create(
        topicName="Computer Science"
    )
    
    user1 = UserInfo.objects.create(
        email="babushkalessons@gmail.com", 
        password="B@bu5hkaL3$$ons!", 
        isTeacher=True
    )
    
    course1 = Courses.objects.create(
        userID=user1,
        courseName="Demo Course",
        courseDescription="Course for Project Demonstration",
        isApproved=True,
        rating=4.5
    )

    tag1 = Tags.objects.create(
        tagName="Python"
    )
    tag2 = Tags.objects.create(
        tagName="Coding"
    )

    applyTag1 = AppliedTags.objects.create(
        tagID=tag1, 
        courseID=course1
    )
    applyTag2 = AppliedTags.objects.create(
        tagID=tag2,
        courseID=course1
    )

    applyTopic1 = AppliedTopics.objects.create(
        topicID=topic1,
        courseID=course1
    )

    lesson1 = Lessons.objects.create(
        courseID=course1,
        lessonName="Demo Lesson",
        lessonDescription="Demo Lesson Description Lorem ipsum odor amet, consectetuer adipiscing elit. Lacus mauris erat iaculis erat felis. Netus fames tincidunt nam at aliquam vestibulum etiam aptent pulvinar. Molestie magnis odio magnis ornare tincidunt nisi. Convallis suspendisse molestie dui pretium, vivamus egestas vitae. Diam congue lacinia condimentum lacinia, eros neque gravida nascetur congue. Risus ad primis non conubia facilisis feugiat."
    )
    lesson2 = Lessons.objects.create(
        courseID=course1,
        lessonName="Demo Lesson 2",
        lessonDescription="Demo Lesson 2 Description"
    )

    uploaded1 = Uploaded.objects.create(
        lessonID=lesson1,
        videoURL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )
    uploaded2 = Uploaded.objects.create(
        lessonID=lesson1,
        videoURL="https://www.youtube.com/watch?v=R_FQU4KzN7A"
    )

class Migration(migrations.Migration):
    dependencies = [
        ('backend_app', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_basic_data),
    ]