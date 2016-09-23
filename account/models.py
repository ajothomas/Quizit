from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group, Permission
from datetime import datetime 

class Course(models.Model):
	courseName = models.CharField(max_length=500)
	batch = models.CharField(max_length=500)
	startDate = models.DateField()
	endDate = models.DateField()
	def __unicode__(self):
		return self.courseName + " | " + self.batch

class Course_Topics(models.Model):
	topicName = models.CharField(max_length = 500)
	course = models.ForeignKey(Course, on_delete = models.CASCADE)
	def __unicode__(self):
		return self.topicName + " | " + self.course.courseName
	class Meta:
		ordering = ["topicName"]

class Instructor_Info(models.Model):
	username = models.CharField(max_length=200)
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	email = models.CharField(max_length=200)
	password = models.CharField(max_length=200)
	groups = models.CharField(max_length=200, default='instructor')
	uuid = models.CharField(max_length=200)
	def __unicode__(self):
		return self.username

class Instructor_Course(models.Model):
	instructor = models.ForeignKey(Instructor_Info, on_delete = models.CASCADE)
	course = models.ForeignKey(Course, on_delete = models.CASCADE)	
	def __unicode__(self):
		return self.instructor.username + " | " + self.course.courseName

class Instructor_UUID(models.Model):
	instructor = models.ForeignKey( Instructor_Info, on_delete=models.CASCADE)
	uuid = models.CharField(max_length=500)
	startTimestamp = models.DateTimeField(default=datetime.now, blank=True)
	uidType = models.IntegerField(default = 1)
	# type :: 2:password reset, 0:disabled
	def __unicode__(self):
		return self.instructor.username

class Student_Info(models.Model):
	username = models.CharField(max_length=200)
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	email = models.CharField(max_length=200)
	password = models.CharField(max_length=200)
	groups = models.CharField(max_length=200, default='student')
	uuid = models.CharField(max_length=200)
	session_key = models.CharField(max_length=500)
	cookie_key = models.CharField(max_length=500)
	def __unicode__(self):
		return self.username

class Student_UUID(models.Model):
	student = models.ForeignKey( Student_Info, on_delete=models.CASCADE)
	uuid = models.CharField(max_length=500)
	startTimestamp = models.DateTimeField(default=datetime.now, blank=True)
	uidType = models.IntegerField(default = 1)
	# type :: 1:new question, 2:password reset, 0:disabled
	def __unicode__(self):
		return self.student.username

class Student_Course(models.Model):
	student = models.ForeignKey(Student_Info, on_delete = models.CASCADE)
	course = models.ForeignKey(Course, on_delete = models.CASCADE)
	enrolledDate = models.DateField()
	def __unicode__(self):
		return self.student.username + " | " + self.course.courseName

class Student_Login_Log(models.Model):
	student = models.ForeignKey(Student_Info)
	activity = models.CharField(max_length=200) # login, logout
	startTimestamp = models.DateTimeField(default=datetime.now, blank=True)
	endTimestamp = models.DateTimeField(null=True, blank=True)