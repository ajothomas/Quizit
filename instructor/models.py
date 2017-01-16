from __future__ import unicode_literals
from django.utils.encoding import smart_unicode, smart_text

from django.db import models
from account import models as account_models

# Create your models here.

class MCQ_Question(models.Model):
	question = models.CharField(max_length=500)
	course = models.ForeignKey(account_models.Course, on_delete = models.CASCADE)
	courseTopic = models.CharField(max_length=200,default='')
	choiceA = models.CharField(max_length=1000,default ='',blank=True, null=True)
	choiceB = models.CharField(max_length=1000,default ='',blank=True, null=True)
	choiceC = models.CharField(max_length=1000,default ='',blank=True, null=True)
	choiceD = models.CharField(max_length=1000,default ='',blank=True, null=True)
	choiceE = models.CharField(max_length=1000,default ='',blank=True, null=True)
	choiceF = models.CharField(max_length=1000,default ='',blank=True, null=True)
	numChoices = models.IntegerField(default = 4)
	answer = models.CharField(max_length=10)
	level = models.CharField(max_length=10, default ='Easy')
	datetime = models.DateField(auto_now=False, auto_now_add=False)
	sentFlag = models.BooleanField(default = False)
	totStudents = models.IntegerField(default = 0)
	totAnswers = models.IntegerField(default = 0)
	totCorrectAnswers = models.IntegerField(default = 0)

	class Meta:
		ordering = ['datetime']

	def __unicode__(self):
		return smart_unicode(self.question)


class Recommendations(models.Model):
	question = models.ForeignKey(MCQ_Question, on_delete=models.CASCADE)
	text = models.TextField()
	fileName = models.CharField(max_length=200, default = 'path')
	rank = models.IntegerField(default = 0)
	upVotes = models.IntegerField(default = 0)
	downVotes = models.IntegerField(default = 0)
	totalVotes = models.IntegerField(default = 0)
	averageRatings = models.IntegerField(default = 0)

	def __unicode__(self):
		return smart_unicode(self.text)