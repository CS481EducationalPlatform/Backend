from django.db import migrations, models

def create_basic_data(apps, schema_editor):
    # Get the models you want to populate data for
    UserInfo = apps.get_model('backend_app', 'UserInfo')
    Courses = apps.get_model('backend_app', 'Courses')
    Topics = apps.get_model('backend_app', 'Topics')
    Tags = apps.get_model('backend_app', 'Tags')
    AppliedTags = apps.get_model('backend_app', 'AppliedTags')
    Lessons = apps.get_model('backend_app', 'Lessons')
    Pages = apps.get_model('backend_app', 'Pages')
    Uploaded = apps.get_model('backend_app', 'Uploaded')

    topic1 = Topics.objects.create(
        TopicName="Computer Science"
    )
    
    user1 = UserInfo.objects.create(
        Email="babushkalessons@gmail.com", 
        Password="B@bu5hkaL3$$ons!", 
        IsTeacher=True
    )
    
    course1 = Courses.objects.create(
        UserID=user1,
        CourseName="Demo Course",
        CourseDescription="Course for Project Demonstration",
        TopicID=topic1,
        IsApproved=True
    )

    tag1 = Tags.objects.create(
        TagName="Python"
    )
    tag2 = Tags.objects.create(
        TagName="Coding"
    )

    applyTag1 = AppliedTags.objects.create(
        TagID=tag1, 
        CourseID=course1
    )
    applyTag2 = AppliedTags.objects.create(
        TagID=tag2,
        CourseID=course1
    )

    lesson1 = Lessons.objects.create(
        CourseID=course1,
        LessonName="Demo Lesson",
        LessonDescription="Demo Lesson Description Lorem ipsum odor amet, consectetuer adipiscing elit. Lacus mauris erat iaculis erat felis. Netus fames tincidunt nam at aliquam vestibulum etiam aptent pulvinar. Molestie magnis odio magnis ornare tincidunt nisi. Convallis suspendisse molestie dui pretium, vivamus egestas vitae. Diam congue lacinia condimentum lacinia, eros neque gravida nascetur congue. Risus ad primis non conubia facilisis feugiat."
    )

    page1 = Pages.objects.create(
        LessonID=lesson1,
        PageName="Demo Lesson Page 1",
        PageDescription="Page 1 Description"
    )
    page2 = Pages.objects.create(
        LessonID=lesson1,
        PageName="Demo Lesson Page 2",
        PageDescription="Page 2 Description"
    )

    uploaded1 = Uploaded.objects.create(
        PageID=page1,
        VideoURL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )
    uploaded2 = Uploaded.objects.create(
        PageID=page1,
        VideoURL="https://www.youtube.com/watch?v=R_FQU4KzN7A"
    )

class Migration(migrations.Migration):
    dependencies = [
        ('backend_app', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_basic_data),
    ]
