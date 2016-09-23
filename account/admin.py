from django.contrib import admin
from account.models import Student_Info, Instructor_Info, Course, Course_Topics, Student_Course, Instructor_Course
import csv
from django.http import HttpResponse
from django.conf import settings
from datetime import date

#################################################################################################
# Student Info

class Student_InfoAdmin(admin.ModelAdmin):
	
	def has_add_permission(self, request):
		return False

	def get_actions(self, request):
		actions = super(Student_InfoAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	actions = ['download_csv']
	list_display = ['id', 'first_name', 'last_name']
	def download_csv(self, request, queryset):
		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'wb')
		writer = csv.writer(f)
		writer.writerow(['id', 'first_name', 'last_name'])

		for s in queryset:
			writer.writerow([s.id, s.first_name, s.last_name])

		f.close()

		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'r')
		response = HttpResponse(f, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=Student-Info-'+str(date.today())+'.csv'
		return response

admin.site.register(Student_Info, Student_InfoAdmin)

#################################################################################################
# Student Course Mapping

class Student_CourseAdmin(admin.ModelAdmin):
	def has_add_permission(self, request):
		return False

	def get_actions(self, request):
		actions = super(Student_CourseAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	list_filter = ('course', )

	actions = ['download_csv']
	list_display = ['student', 'course']
	def download_csv(self, request, queryset):
		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'wb')
		writer = csv.writer(f)
		writer.writerow(['student', 'course',])

		for s in queryset:
			writer.writerow([s.student.id, s.course.id])

		f.close()

		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'r')
		response = HttpResponse(f, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=Student-Course-'+str(date.today())+'.csv'
		return response
admin.site.register(Student_Course, Student_CourseAdmin)

#################################################################################################
# Instructor Info

class Instructor_InfoAdmin(admin.ModelAdmin):
	def has_add_permission(self, request):
		return False

	def get_actions(self, request):
		actions = super(Instructor_InfoAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	actions = ['download_csv']
	list_display = ['id', 'first_name', 'last_name']
	def download_csv(self, request, queryset):
		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'wb')
		writer = csv.writer(f)
		writer.writerow(['id', 'first_name', 'last_name'])

		for s in queryset:
			writer.writerow([s.id, s.first_name, s.last_name])

		f.close()

		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'r')
		response = HttpResponse(f, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=Instructor-Info-'+str(date.today())+'.csv'
		return response

admin.site.register(Instructor_Info, Instructor_InfoAdmin)

#################################################################################################
# Instructor Course

class Instructor_CourseAdmin(admin.ModelAdmin):
	def has_add_permission(self, request):
		return False

	def get_actions(self, request):
		actions = super(Instructor_CourseAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	list_filter = ('course', )

	actions = ['download_csv']
	list_display = ['instructor', 'course']
	def download_csv(self, request, queryset):
		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'wb')
		writer = csv.writer(f)
		writer.writerow(['instructor', 'course',])

		for s in queryset:
			writer.writerow([s.instructor.id, s.course.id])

		f.close()

		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'r')
		response = HttpResponse(f, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=Instructor-Course-'+str(date.today())+'.csv'
		return response

admin.site.register(Instructor_Course, Instructor_CourseAdmin)

#################################################################################################
# Course

class CourseAdmin(admin.ModelAdmin):
	def has_add_permission(self, request):
		return False

	def get_actions(self, request):
		actions = super(CourseAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	actions = ['download_csv']
	list_display = ['id', 'courseName', 'batch']
	def download_csv(self, request, queryset):
		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'wb')
		writer = csv.writer(f)
		writer.writerow(['id', 'courseName', 'batch'])

		for s in queryset:
			writer.writerow([s.id, s.courseName, s.batch])

		f.close()

		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'r')
		response = HttpResponse(f, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=Courses-'+str(date.today())+'.csv'
		return response

admin.site.register(Course, CourseAdmin)

#################################################################################################
# Course_Topics

class Course_TopicsAdmin(admin.ModelAdmin):
	
	list_filter = ('course', )
	def has_add_permission(self, request):
		return False

	def get_actions(self, request):
		actions = super(Course_TopicsAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	actions = ['download_csv']
	list_display = ['topicName', 'course']
	def download_csv(self, request, queryset):
		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'wb')
		writer = csv.writer(f)
		writer.writerow(['topicName', 'course'])

		for s in queryset:
			writer.writerow([s.topicName, s.course.id])

		f.close()

		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'r')
		response = HttpResponse(f, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=Course-Topic-'+str(date.today())+'.csv'
		return response

admin.site.register(Course_Topics, Course_TopicsAdmin)

#################################################################################################
