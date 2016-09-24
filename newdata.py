from django.contrib.auth.models import User, Group
from account.models import Course, Course_Topics, Instructor_Info, Instructor_Course, Student_Info, Student_Course
from instructor.models import MCQ_Question, Recommendations
from student.models import Student_Answers, Student_Marks
import uuid
import datetime
import random
########################################################################################################################

course = Course.objects.get(courseName = 'CSE110 Principles of Programming')

u = uuid.uuid4()
instructor = Instructor_Info.objects.create(
	username = 'navabi',
	first_name = 'navabi',
	last_name = 'navabi',
	email = 'navabi@asu.edu',
	password = 'navabipassword',
	groups = 'admin',
	uuid = str(u.hex),
	)

user = User.objects.create_user(
	username = 'navabi',
	first_name = 'navabi',
	last_name = 'navabi',
	email =  'navabi@asu.edu',
	password = 'navabipassword',
	)
user.groups.add(Group.objects.get(name='admin'))
user.save()


Instructor_Course.objects.create(course = course,instructor = instructor)

Instructor_Info.objects.filter(email='navabi@asu.edu').delete()
User.objects.filter(email='navabi@asu.edu').delete()

ajo.thomas@outlook.com

Instructor_Info.objects.filter(email='ajo.thomas@outlook.com').delete()
User.objects.filter(email='ajo.thomas@outlook.com').delete()

Student_Info.objects.filter(email = 'ajo.thomas@outlook.com').delete()

########################################################################################################################

course = Course.objects.get(courseName = 'CSE110 Principles of Programming')

u = uuid.uuid4()
instructor = Instructor_Info.objects.create(
	username = 'ihsiao1',
	first_name = 'Sharon',
	last_name = 'Hsiao',
	email = 'ihsiao1@asu.edu',
	password = 'sharonpassword',
	groups = 'admin',
	uuid = str(u.hex),
	)

user = User.objects.create_user(
				username = 'ihsiao1',
				first_name = 'Sharon',
				last_name = 'Hsiao',
				email =  'ihsiao1@asu.edu',
				password = 'sharonpassword',
				)
user.groups.add(Group.objects.get(name='admin'))
user.save()


Instructor_Course.objects.create(
	course = course,
	instructor = instructor,
	)

########################################################################################################################

course = Course.objects.get(courseName = 'CSE110 Principles of Programming')

u = uuid.uuid4()
instructor = Instructor_Info.objects.create(
	username = 'Mohammed62085',
	first_name = 'Mohammed',
	last_name = 'Alzaid',
	email = 'malzaid1@asu.edu',
	password = 'alzaidpassword',
	groups = 'admin',
	uuid = str(u.hex),
	)

instructor = Instructor_Info.objects.get(email = 'malzaid1@asu.edu')
instructor.username = 'Mohammed62085'
instructor.save()
student = Student_Info.objects.get(email = 'malzaid1@asu.edu')
user = User.objects.get(email = 'malzaid1@asu.edu')
user.set_password('alzaidpassword');
user.groups.add(Group.objects.get(name='admin'))
user.save()


Instructor_Course.objects.create(
	course = course,
	instructor = instructor,
	)