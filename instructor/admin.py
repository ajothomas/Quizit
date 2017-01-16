from django.contrib import admin
from instructor.models import MCQ_Question
import csv
from django.http import HttpResponse
from django.conf import settings
from datetime import date
from django.db import models

#################################################################################################
# Student Info

class MCQ_QuestionAdmin(admin.ModelAdmin):
	
	def has_add_permission(self, request):
		return False

	def get_actions(self, request):
		actions = super(MCQ_QuestionAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	actions = ['download_csv']
	list_display = ['id', 'question', 'datetime']
	def download_csv(self, request, queryset):
		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'wb')
		writer = csv.writer(f)
		writer.writerow(['id', 'question', 'datetime'])

		for s in queryset:
			writer.writerow([s.id, s.question, s.datetime])

		f.close()

		f = open(settings.BASE_DIR+"/static/"+"some.csv", 'r')
		response = HttpResponse(f, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=MCQ_Question-'+str(date.today())+'.csv'
		return response

	# my_nullable_string = models.CharField(max_length=15, null=True, blank=True)

	# def save(self, *args, **kwargs):
	# 	if not self.my_nullable_string:
	# 		self.my_nullable_string = None
	# 	super(MCQ_Question, self).save(*args, **kwargs)

admin.site.register(MCQ_Question, MCQ_QuestionAdmin)