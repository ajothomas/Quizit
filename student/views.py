from __future__ import unicode_literals
from instructor.models import MCQ_Question, Recommendations
from account.models import Student_Info, Student_UUID, Course, Course_Topics, Instructor_Info, Instructor_Course, Student_Course
from student.models import Student_Marks, Student_Answers, Student_Recommendations, Student_Explanations, Student_Answers_ActivityLog, Student_Answer_Log

from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import localtime
import pytz

from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.conf import settings

from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage
from django.core import serializers

from django.db.models import Sum,Count,Avg
import math
import socket
import uuid
import string
import random
from django.http import JsonResponse
import json
import nltk
import pysolr

##################################################################################################################
## STUDENT VIEWS

@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def viewCourses(request):
	if request.user.is_authenticated():
		username = request.user.username
		first_name = request.user.first_name
		
		student = Student_Info.objects.get(username = username)
		studentCourses = Student_Course.objects.filter(student = student )
		# print studentCourses
		context = {
			"username" : username ,
			"first_name" : first_name,
			"studentCourses" : studentCourses,
		}
		return render(request, 'student/viewCourses.html', context)

	else :
		return redirect(reverse('account:login_view'))

@user_passes_test(lambda u: u.groups.filter(name='student').count() > 0, login_url='/student/wrongpage/')
def selectCourse(request):
	if request.method == 'POST':
		courseId = request.POST.get('courseId','')
		request.session['courseId'] = courseId
		return HttpResponse("Some response")

@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def studentLanding(request):
	if request.user.is_authenticated():
		username = request.user.username
		# username = request.user.email
		# userObj = User.objects.filter(email = email)[0]
		# first_name = userObj.first_name
		# update all data
		# #res = updateAllRanksAndBadges(request)

		# studentMark = Student_Marks.objects.filter(student = Student_Info.objects.filter(username = username)[0])[0]
		# allStudentMarks = Student_Marks.objects.order_by('rank')
		# percCorrAns = (studentMark.numCorrAns*100)/studentMark.numQues
		# if studentMark.currStreak > 0:
		# 	pStreak = studentMark.currStreak
		# 	nStreak = 0
		# if studentMark.currStreak < 0:
		# 	pStreak = 0
		# 	nStreak = -studentMark.currStreak

		# context = {
		# 	"username" : username,
		#	"first_name" : first_name,
		# 	"rank" : studentMark.rank,
		# 	"badge" : studentMark.badge,
		# 	"totMarks" : studentMark.totMarks,
		# 	"numQues" : studentMark.numQues,
		# 	"percCorrAns" : percCorrAns,
		# 	"bonus": studentMark.bonus,
		# 	"streak05" : studentMark.streak05,
		# 	"streak10" : studentMark.streak10,
		# 	"streak20" : studentMark.streak20,
		# 	"pStreak" : pStreak,
		# 	"nStreak" : nStreak,
		# 	"allStudentMarks" : allStudentMarks,
		# }
		#return render(request, 'student/studentLanding.html', context)
		return HttpResponse("Hello")
	else:
		return redirect(reverse('account:login_view'))

@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/quizit/wrongpage/')
def studentQuestionRetry(request, sid = None, qid = None, topAlertFlag = None, backLocation = None):
	if request.user.is_authenticated():
		username = request.user.username
		email = request.user.email
		userObj = User.objects.filter(email = email)[0]
		first_name = userObj.first_name
		question = MCQ_Question.objects.filter(id = qid)[0]
		student = Student_Info.objects.filter(id = sid)[0]
		studentAnswer = None
		correctFlag = None

		# creating a list of upper case characters equal to the number of choices
		choiceList = list(string.uppercase[:int(question.numChoices)])
		choiceListOriginal = list(string.uppercase[:int(question.numChoices)])
		random.shuffle(choiceList)
		
		shuffledQuestion = {}

		for x in range(int(question.numChoices)):
			shuffledQuestion['choice'+choiceListOriginal[x]] = getattr(question,'choice'+choiceList[x])
			
		shuffledQuestion['answer'] = choiceList[choiceListOriginal.index(question.answer[6])]

		answer = question.answer[6]

		studentExplanations = None
		studentExplanationFlag = False
		otherStudentExplanationFlag = False
		otherStudentExplanations = None 
		
		# logging user action
		timezone.activate(pytz.timezone("America/Phoenix"))
		activityTimeStamp = localtime(timezone.now())
		
		if int(backLocation) == 1:
			source = 'List'
		else:
			source = 'Calendar'

		activity = Student_Answers_ActivityLog.objects.create(
			student = student,
			question = question,
			activity = 'Retry',
			source = source,
			activityTimeStamp = activityTimeStamp,
		)

		#  if the student has already answered the question
		if Student_Answers.objects.filter(question = question).filter(student=student).count()>0:
			studentAnswer = Student_Answers.objects.filter(question = question).filter(student = student)[0]
			
			numAttempts = studentAnswer.numAttempts
			Student_Answers.objects.filter(question = question).filter(student = student).update(
				numAttempts = numAttempts+1,
			)
			correctFlag = studentAnswer.correctFlag

		# if the question was not answered
		else:
			Student_Answers.objects.create(
				student = student,
				question = question,
				numAttempts = 1,
			)

		if Student_Explanations.objects.filter(question = question).filter(student=student).count()>0:
			studentExplanations = Student_Explanations.objects.filter(question = question).filter(student = student)
			studentExplanationFlag = True

		if Student_Explanations.objects.filter(question = question).exclude(student=student).count()>0:
			otherStudentExplanations = Student_Explanations.objects.filter(question = question).exclude(student = student)
			otherStudentExplanationFlag = True

		context = {
			# top alert
			"topAlertFlag" : topAlertFlag,

			#student
			"student" : student,
			"username" : username,
			"first_name" : first_name,
			"question" : question,
			"shuffledQuestion" : shuffledQuestion,
			"choiceList" : choiceList,
			"studentExplanations" : studentExplanations,
			"studentExplanationFlag" : studentExplanationFlag,
			"otherStudentExplanations" : otherStudentExplanations,
			"otherStudentExplanationFlag" : otherStudentExplanationFlag,
			"studentAnswer" : studentAnswer,
			"answer" : answer,
			"correctFlag" : correctFlag,

			"backLocation" : backLocation,
			"activityID" : activity.id 
		}
		return render(request, 'student/studentQuestionRetry.html', context)
	else:
		return redirect(reverse('account:login_view'))

@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def saveExplanation(request):
	if request.user.is_authenticated():
		if request.POST.has_key('explanationText'):
			username = request.POST.get('username','')
			questionId = request.POST.get('questionid','')			
			explanationText = request.POST.get('explanationText','')

			timezone.activate(pytz.timezone("America/Phoenix"))
			postTimeStamp = localtime(timezone.now())
			# print postTimeStamp
			student = Student_Info.objects.get(username = username)
			question = MCQ_Question.objects.get(id = int(questionId))
			
			Student_Explanations.objects.create(
				student = student,
				question = question,
				explanationText = explanationText,
				postTimeStamp = postTimeStamp,
				)

			return HttpResponse("dummy return value")
	else:
		return redirect(reverse('account:login_view'))

@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/quizit/wrongpage/')
def studentQuestionView(request, sid = None, qid = None, topAlertFlag = None, backLocation = None):
	if request.user.is_authenticated():
		if 'courseId' in request.session :
			username = request.user.username
			email = request.user.email
			userObj = User.objects.filter(email = email)[0]
			first_name = userObj.first_name
			course = Course.objects.get(id = int(request.session['courseId']))
			question = MCQ_Question.objects.filter(id = qid)[0]
			student = Student_Info.objects.filter(id = sid)[0]
			studentAnswer = None
			
			# logging user action
			timezone.activate(pytz.timezone("America/Phoenix"))
			activityTimeStamp = localtime(timezone.now())
			
			if int(backLocation) == 1:
				source = 'List'
			else:
				source = 'Calendar'

			activity = Student_Answers_ActivityLog.objects.create(
				student = student,
				question = question,
				activity = 'Review',
				source = source,
				activityTimeStamp = activityTimeStamp,
			)

			# creating a list of upper case characters equal to the number of choices
			choiceList = list(string.uppercase[:int(question.numChoices)])
			choiceListOriginal = list(string.uppercase[:int(question.numChoices)])
			random.shuffle(choiceList)
			
			shuffledQuestion = {}
			for x in range(int(question.numChoices)):
				shuffledQuestion['choice'+choiceListOriginal[x]] = getattr(question,'choice'+choiceList[x])
			
			shuffledQuestion['answer'] = choiceListOriginal[choiceList.index(question.answer[6])]

			answer = question.answer[6]
			correctFlag = None
			shuffledAnswerSequence = ""
			studentExplanations = None
			studentExplanationFlag = False
			otherStudentExplanationFlag = False
			otherStudentExplanations = None 
			
			#  if the student has already answered the question
			if Student_Answers.objects.filter(question = question).filter(student=student).count()>0:
				studentAnswer = Student_Answers.objects.filter(question = question).filter(student = student)[0]
				correctFlag = studentAnswer.correctFlag,
				answerSequenceSplit = studentAnswer.answerSequence.split('|')

				for ans in answerSequenceSplit:
					if ans != "":
						shuffledAnswerSequence = shuffledAnswerSequence + "|" + choiceListOriginal[choiceList.index(ans)]

				# First character is '|'
				shuffledAnswerSequence = shuffledAnswerSequence[1:]
			
			# explanations or comments by user
			if Student_Explanations.objects.filter(question = question).filter(student=student).count()>0:
				studentExplanations = Student_Explanations.objects.filter(question = question).filter(student = student)
				studentExplanationFlag = True

			# explanations or comments by other users
			if Student_Explanations.objects.filter(question = question).exclude(student=student).count()>0:
				otherStudentExplanations = Student_Explanations.objects.filter(question = question).exclude(student = student)
				otherStudentExplanationFlag = True
			
			context = {
				# top alert
				"topAlertFlag" : topAlertFlag,

				#student
				"quizFlag": 1,
				"student" : student,
				"username" : username,
				"courseName" : course.courseName.title(), 
				"first_name" : first_name,
				"question" : question,
				"shuffledQuestion" : shuffledQuestion,
				"shuffledAnswerSequence" : shuffledAnswerSequence,
				"choiceList" : json.dumps(choiceList),
				"studentAnswer" : studentAnswer,
				"answer" : answer,
				
				"correctFlag" : correctFlag,

				"studentExplanations" : studentExplanations,
				"studentExplanationFlag" : studentExplanationFlag,
				"otherStudentExplanations" : otherStudentExplanations,
				"otherStudentExplanationFlag" : otherStudentExplanationFlag,

				"backLocation" : backLocation,
				"activityID" : activity.id
			}
			return render(request, 'student/studentQuestionView.html', context)
		else :
			return redirect(reverse('student:viewCourses'))
	else:
		return redirect(reverse('account:login_view'))

# This module is run every time a recommended reading is upvoted or downvoted by a student
def updateRecommendations(request):
	if request.method == 'POST':
		questionId = request.POST.get('questionId')
		studentId = request.POST.get('studentId')
		recommendationId = request.POST.get('recommendationId')
		voteFlag = request.POST.get('voteFlag')

		student = Student_Info.objects.get(id = studentId)
		question = MCQ_Question.objects.get(id = questionId)
		recommendation = Recommendations.objects.filter(question = question).filter(id = recommendationId)[0]
		
		if Student_Recommendations.objects.filter(student = student).filter(question = question).filter(recommendation=recommendation).count()==0:
			Student_Recommendations.objects.create(
				student = student,
				question = question,
				recommendation = recommendation,
				voteFlag = voteFlag
				)

		upvoteValue = downvoteValue = 0
		
		if int(voteFlag) == 1:
			upvoteValue = 1
		else:
			downvoteValue = 1
		
		newUpvotes = recommendation.upVotes + upvoteValue
		newDownvotes = recommendation.downVotes + downvoteValue
		newAverageRatings = recommendation.averageRatings + (upvoteValue*3) + (downvoteValue*-3)
		newTotalVotes = recommendation.totalVotes + upvoteValue + downvoteValue

		Recommendations.objects.filter(question = question).filter(id = recommendationId).update(upVotes = newUpvotes, downVotes = newDownvotes, averageRatings = newAverageRatings, totalVotes = newTotalVotes)

	return HttpResponse('')
@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def studentQuestionCalendar(request):
	if request.user.is_authenticated():
		if 'courseId' in request.session :
			username = request.user.username
			email = request.user.email
			userObj = User.objects.filter(email = email)[0]
			first_name = userObj.first_name
			course = Course.objects.get(id = int(request.session['courseId']))

			courseQuestions = MCQ_Question.objects.filter(course = course)
			studentAnswers = Student_Answers.objects.filter(student = Student_Info.objects.filter(username = username)[0]).filter(question__course = course).filter( question__datetime__lte = localtime(timezone.now()).date() )
			
			# creating a python dictionary which will be read as a JSON object by javascript
			eventData = {"dates":[]}

			for question in courseQuestions:
				
				# python date object cannot be json serialized. this is the workaround for that
				date = json.dumps(question.datetime.isoformat())
				if Student_Answers.objects.filter(student = Student_Info.objects.filter(username = username)[0]).filter(question = question) :
					answerFlag = 1
					studentAnswer = Student_Answers.objects.filter(student = Student_Info.objects.filter(username = username)[0]).filter(question = question)[0]
					studentID = Student_Info.objects.filter(username = username)[0].id
					numAttempts = studentAnswer.numAttempts
					numCorrectAttempts = studentAnswer.numCorrectAttempts
					if numAttempts == 0:
						cssName = ""
					elif float(numCorrectAttempts)/float(numAttempts) >= 0.9:
						cssName = "dateGreen"
					elif float(numCorrectAttempts)/float(numAttempts) > 0.7:
						cssName = "dateOrange"
					else:
						cssName = "dateRed"
				else:
					answerFlag = 0
					studentAnswer = None
					studentID = Student_Info.objects.filter(username = username)[0].id
					numAttempts = 0
					numCorrectAttempts = 0
					cssName = ""

				datesObj = {
					"date" : date,
					"questionText" : question.question,
					"questionID" : question.id,
					"studentID" : studentID,
					"answerFlag" : answerFlag,
					"numAttempts" : numAttempts,
					"numCorrectAttempts" : numCorrectAttempts,
					"cssName" : cssName,
				}
				eventData["dates"].append(datesObj);

			context = {
				"username" : username,
				"first_name" : first_name,
				"courseName" : course.courseName.title(), 
				"studentAnswers" : studentAnswers,
				"eventData" : json.dumps(eventData),
			}
			return render(request, 'student/studentQuestionCalendar.html', context)
		else :
			return redirect(reverse('student:viewCourses'))
	else:
		return redirect(reverse('account:login_view'))


# This module lists all the questions
@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def studentQuestionList(request):
	if request.user.is_authenticated():
		if 'courseId' in request.session :
			username = request.user.username
			email = request.user.email
			userObj = User.objects.filter(email = email)[0]
			first_name = userObj.first_name
			course = Course.objects.get(id = int(request.session['courseId']))
			courseQuestions = MCQ_Question.objects.filter(course = course)	
			
			# setting the timezone
			timezone.activate(pytz.timezone("America/Phoenix"))
			localtime(timezone.now()).date()

			# getting all student answers before today's date
			studentAnswers = Student_Answers.objects.filter(student = Student_Info.objects.filter(username = username)[0]).filter(question__course = course).filter( question__datetime__lte = localtime(timezone.now()).date() )
			
			# creating a python dictionary which will be read as a JSON object by javascript

			context = {
				"username" : username,
				"first_name" : first_name,
				"courseName" : course.courseName.title(), 
				"studentAnswers" : studentAnswers,
			}

			return render(request, 'student/studentQuestionList.html', context)
		else :
			return redirect(reverse('student:viewCourses'))
	else:
		return redirect(reverse('account:login_view'))

def updateQuestionData(request):
	totStudents = Student_Info.objects.all().count()
	allQuestions = MCQ_Question.objects.filter(datetime__lte=datetime.now().date()).order_by('datetime')
	for question in allQuestions:
		studentAnswers = Student_Answers.objects.filter(question = question)
		totCorrectAnswers = 0
		totAnswers = studentAnswers.count()
		for answer in studentAnswers:
			totCorrectAnswers += answer.correctFlag
		MCQ_Question.objects.filter( id = question.id).update(
			totStudents = totStudents,
			totAnswers = totAnswers,
			totCorrectAnswers = totCorrectAnswers
			)

	return HttpResponse('Question data updated')

@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def studentTodaysQuiz(request):
	if request.user.is_authenticated():
		if 'courseId' in request.session :
			username = request.user.username
			email = request.user.email
			userObj = User.objects.filter(email = email)[0]
			first_name = userObj.first_name
			course = Course.objects.get(id = int(request.session['courseId']))
			shuffledAnswerSequence = ""
			
			student = Student_Info.objects.get(username = username)
			
			studentAnswer = None
			answer = None
			activity = None

			studentExplanations = None
			studentExplanationFlag = False
			otherStudentExplanationFlag = False
			otherStudentExplanations = None 
			
			# Check if there is a quiz scheduled for the day
			timezone.activate(pytz.timezone("America/Phoenix"))
			localtime(timezone.now()).date()

			#if MCQ_Question.objects.filter(datetime__year=datetime.now().year, datetime__month=datetime.now().month, datetime__day=datetime.now().day).count()>0:
			if MCQ_Question.objects.filter(course = course).filter(datetime = localtime(timezone.now()).date()).count()>0:
				question = MCQ_Question.objects.filter(course = course).filter(datetime = localtime(timezone.now()).date())[0]
				studentAnswer = None
				
				# logging user action
				activityTimeStamp = localtime(timezone.now())
				
				activity = Student_Answers_ActivityLog.objects.create(
					student = student,
					question = question,
					activity = 'Review',
					source = 'Todaysquiz',
					activityTimeStamp = activityTimeStamp,
				)

				# creating a list of upper case characters equal to the number of choices
				choiceList = list(string.uppercase[:int(question.numChoices)])
				choiceListOriginal = list(string.uppercase[:int(question.numChoices)])
				random.shuffle(choiceList)
				print "Choice List : "
				print choiceListOriginal
				print "Choice List Shuffled : "
				print choiceList

				shuffledQuestion = {}
				for x in range(int(question.numChoices)):
					shuffledQuestion['choice'+choiceListOriginal[x]] = getattr(question,'choice'+choiceList[x])
				
				shuffledQuestion['answer'] = choiceListOriginal[choiceList.index(question.answer[6])]
				print question.answer[6]
				print choiceListOriginal[choiceList.index(question.answer[6])]
				answer = question.answer[6]
				correctFlag = None
				shuffledAnswerSequence = ""
				studentExplanations = None
				studentExplanationFlag = False
				otherStudentExplanationFlag = False
				otherStudentExplanations = None 
			
				#  if the student has already answered the question
				if Student_Answers.objects.filter(question = question).filter(student=student).count()>0:
					studentAnswer = Student_Answers.objects.filter(question = question).filter(student = student)[0]
					correctFlag = studentAnswer.correctFlag,
					answerSequenceSplit = studentAnswer.answerSequence.split('|')

					for ans in answerSequenceSplit:
						if ans != "":
							shuffledAnswerSequence = shuffledAnswerSequence + "|" + choiceListOriginal[choiceList.index(ans)]

					# First character is '|'
					shuffledAnswerSequence = shuffledAnswerSequence[1:]
					print shuffledAnswerSequence
					print  studentAnswer.answerSequence

				# explanations or comments by user
				if Student_Explanations.objects.filter(question = question).filter(student=student).count()>0:
					studentExplanations = Student_Explanations.objects.filter(question = question).filter(student = student)
					studentExplanationFlag = True

				# explanations or comments by other users
				if Student_Explanations.objects.filter(question = question).exclude(student=student).count()>0:
					otherStudentExplanations = Student_Explanations.objects.filter(question = question).exclude(student = student)
					otherStudentExplanationFlag = True
				
				context = {
					# top alert
					"topAlertFlag" : 99999,

					#student
					"quizFlag": 1,
					"student" : student,
					"username" : username,
					"courseName" : course.courseName.title(), 
					"first_name" : first_name,
					"question" : question,
					"shuffledQuestion" : shuffledQuestion,
					"shuffledAnswerSequence" : shuffledAnswerSequence,
					"choiceList" : json.dumps(choiceList),
					"studentAnswer" : studentAnswer,
					"answer" : answer,
					
					"correctFlag" : correctFlag,

					"studentExplanations" : studentExplanations,
					"studentExplanationFlag" : studentExplanationFlag,
					"otherStudentExplanations" : otherStudentExplanations,
					"otherStudentExplanationFlag" : otherStudentExplanationFlag,

					"backLocation" : 2,
					"activityID" : activity.id
				}
				
			else:
				context = {
						"student" : student,
						"username" : username,
						"first_name" : first_name,
						"courseName" : course.courseName.title(), 
						"choiceList" : json.dumps(['X']),
						"question" : None,
						"quizFlag": 0,
						"activityID" : 0,
						}

			## FOR THE CALENDAR
			courseQuestions = MCQ_Question.objects.filter(course = course).filter(datetime__lte = localtime(timezone.now()).date() )
			studentAnswers = Student_Answers.objects.filter(student = Student_Info.objects.filter(username = username)[0]).filter(question__course = course).filter( question__datetime__lte = localtime(timezone.now()).date() )
			
			# creating a python dictionary which will be read as a JSON object by javascript
			eventData = {"dates":[]}

			for question in courseQuestions:
				
				# python date object cannot be json serialized. this is the workaround for that
				date = json.dumps(question.datetime.isoformat())
				if Student_Answers.objects.filter(student = Student_Info.objects.filter(username = username)[0]).filter(question = question) :
					answerFlag = 1
					studentAnswer = Student_Answers.objects.filter(student = Student_Info.objects.filter(username = username)[0]).filter(question = question)[0]
					studentID = Student_Info.objects.filter(username = username)[0].id
					numAttempts = studentAnswer.numAttempts
					numCorrectAttempts = studentAnswer.numCorrectAttempts
					if numAttempts == 0:
						cssName = ""
					elif float(numCorrectAttempts)/float(numAttempts) >= 0.9:
						cssName = "dateGreen"
					elif float(numCorrectAttempts)/float(numAttempts) > 0.7:
						cssName = "dateOrange"
					else:
						cssName = "dateRed"
				else:
					answerFlag = 0
					studentAnswer = None
					studentID = Student_Info.objects.filter(username = username)[0].id
					numAttempts = 0
					numCorrectAttempts = 0
					cssName = ""

				datesObj = {
					"date" : date,
					"questionText" : question.question,
					"questionID" : question.id,
					"studentID" : studentID,
					"answerFlag" : answerFlag,
					"numAttempts" : numAttempts,
					"numCorrectAttempts" : numCorrectAttempts,
					"cssName" : cssName,
				}
				eventData["dates"].append(datesObj);
			
			calendarData = {
				"studentAnswers" : studentAnswers,
				"eventData" : json.dumps(eventData),
			};
			
			context.update(calendarData);

			if Student_Explanations.objects.filter(question = question).filter(student=student).count()>0:
				studentExplanations = Student_Explanations.objects.filter(question = question).filter(student = student)
				studentExplanationFlag = True

			if Student_Explanations.objects.filter(question = question).exclude(student=student).count()>0:
				otherStudentExplanations = Student_Explanations.objects.filter(question = question).exclude(student = student)
				otherStudentExplanationFlag = True

			explanations = {
				"studentExplanations" : studentExplanations,
				"studentExplanationFlag" : studentExplanationFlag,
				"otherStudentExplanations" : otherStudentExplanations,
				"otherStudentExplanationFlag" : otherStudentExplanationFlag,
			}

			context.update(explanations);

			return render(request, 'student/studentTodaysQuiz.html', context)
		else : 
			return redirect(reverse('student:viewCourses'))
	else:
		return redirect(reverse('account:login_view'))

# Stores student answers from the today's quiz page
@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def todaysQuizProcessing(request):
	if request.user.is_authenticated():
		if 'courseId' in request.session :
			if request.POST.has_key('selectedOption') and request.POST.has_key('username'):
				selectedOption = request.POST.get('selectedOption','')
				username = request.POST.get('username','')
				questionid = request.POST.get('questionid','')
				choiceList = request.POST.getlist('choiceList[]','')
				activityID = request.POST.get('activityID','')
				question = MCQ_Question.objects.get(id = int(questionid))
				student = Student_Info.objects.get(username = username)
				activity = Student_Answers_ActivityLog.objects.get(id = activityID)

				# answer is stored as choice2. 2 is B. so add 64 and convert into ascii and string.
				answer = question.answer[6]
				choiceListOriginal = list(string.uppercase[:int(question.numChoices)])
				print selectedOption
				print "choiceListOriginal : "
				print choiceListOriginal
				print "choiceList : "
				print choiceList
				actualSelectedOption = choiceList[choiceListOriginal.index(selectedOption)]

				# if the question was answered previously
				if Student_Answers.objects.filter(question = question).filter(student=student).count()>0:
					studentAnswer = Student_Answers.objects.filter(question = question).filter(student = student)[0]
					
					answerSequence = studentAnswer.answerSequence + "|" + actualSelectedOption
					numAttempts = studentAnswer.numAttempts + 1
					numCorrectAttempts = studentAnswer.numCorrectAttempts
					correctFlag = 0

					# check if answer is correct					
					if actualSelectedOption == answer:
						correctFlag = 1
						numCorrectAttempts = numCorrectAttempts + 1	
						# updating the activity log
						Student_Answers_ActivityLog.objects.filter(id = activityID).update(
							answerFlag = 1
						)

						# recording the answer in the log
						Student_Answer_Log.objects.create(
								student = student,
								question = question,
								activityFK = activity,
								answer = actualSelectedOption,
								answerFlag = 1
							)
					else: 
						# updating the activity log
						Student_Answers_ActivityLog.objects.filter(id = activityID).update(
							answerFlag = 2
						)
						# recording the answer in the log
						Student_Answer_Log.objects.create(
								student = student,
								question = question,
								activityFK = activity,
								answer = actualSelectedOption,
								answerFlag = 2
							)
					
					Student_Answers.objects.filter(student=student).filter(question = question).update(
						selAnswer = actualSelectedOption,
						correctFlag = correctFlag,
						numAttempts = numAttempts,
						numCorrectAttempts = numCorrectAttempts,
						answerSequence = answerSequence,
					);

				# if the question is being answered for the first time		
				else:
					answerSequence = actualSelectedOption
					numAttempts = 1
					numCorrectAttempts = 0
					correctFlag = 0
					
					# check if answer is correct			
					if actualSelectedOption == answer:
						correctFlag = 1
						numCorrectAttempts = numCorrectAttempts + 1	
						Student_Answers_ActivityLog.objects.filter(id = activityID).update(
							answerFlag = 1
						)
					else:
						Student_Answers_ActivityLog.objects.filter(id = activityID).update(
							answerFlag = 2
						)

					
					Student_Answers.objects.create(
						student = student,
						question = question,
						selAnswer = actualSelectedOption,
						correctFlag = correctFlag,
						numAttempts = numAttempts,
						numCorrectAttempts = numCorrectAttempts,
						answerSequence = answerSequence,	
					);

				shuffledAnswerSequence = ""
				answerSequenceSplit = answerSequence.split('|')

				for ans in answerSequenceSplit:
					if ans != "":
						shuffledAnswerSequence = shuffledAnswerSequence + "|" + choiceListOriginal[choiceList.index(ans)]

				shuffledAnswer = choiceListOriginal[choiceList.index(answer)]

				postReturnData = { 
					"shuffledAnswerSequence" : shuffledAnswerSequence,
					"choiceList": choiceList,
					"shuffledAnswer" : shuffledAnswer,
					"numAttempts" : numAttempts,
					}
				return HttpResponse(json.dumps(postReturnData))
			else:
				return render(request, 'student/wrongpage.html', context)
		else :
			return redirect(reverse('student:viewCourses'))

	else:
		context = {}
		return render(request, 'student/login.html', context)

# Stores student answers from the today's quiz page
@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def questionRetryProcessing(request):
	if request.user.is_authenticated():
		if 'courseId' in request.session :
			if request.POST.has_key('selectedOption') and request.POST.has_key('username'):
				# print "hello world"
				selectedOption = request.POST.get('selectedOption','')
				choiceList = request.POST.getlist('choiceList[]')
				username = request.POST.get('username','')
				questionid = request.POST.get('questionid','')
				activityID = request.POST.get('activityID','')

				question = MCQ_Question.objects.get(id = int(questionid))
				student = Student_Info.objects.get(username = username)
				activity = Student_Answers_ActivityLog.objects.get(id = activityID)

				# answer is stored as choice2. 2 is B. so add 64 and convert into ascii and string.
				answer = question.answer[6]
				correctFlag = 0
				numCorrectAttempts = 0

				if Student_Answers.objects.filter(question = question).filter(student = student).count()>0:
					studentAnswer = Student_Answers.objects.filter(question = question).filter(student = student)[0]
					numAttempts = studentAnswer.numAttempts # + 1
					numCorrectAttempts = studentAnswer.numCorrectAttempts
				else:
					pass
					#numAttempts = 1
				
				print "Hello world"

				choiceListOriginal = list(string.uppercase[:int(question.numChoices)])
				actualSelectedOption = choiceList[choiceListOriginal.index(selectedOption)]

				# checking if answer is correct
				if actualSelectedOption == answer:
					numCorrectAttempts = numCorrectAttempts  + 1	
					correctFlag = 1
					Student_Answers_ActivityLog.objects.filter(id = activityID).update(
						answerFlag = 1
						)
					# recording the answer in the log
					Student_Answer_Log.objects.create(
							student = student,
							question = question,
							activityFK = activity,
							answer = actualSelectedOption,
							answerFlag = 1
						)

				else :
					Student_Answers_ActivityLog.objects.filter(id = activityID).update(
						answerFlag = 1
						)

					# recording the answer in the log
					Student_Answer_Log.objects.create(
							student = student,
							question = question,
							activityFK = activity,
							answer = actualSelectedOption,
							answerFlag = 2
						)

				Student_Answers.objects.filter(student=student).filter(question = question).update(
					selAnswer = selectedOption,
					numAttempts = numAttempts,
					numCorrectAttempts = numCorrectAttempts,
				);

				postReturnData = { 
					"correctFlag" : correctFlag,
					"numAttempts" : numAttempts,
					}

				return HttpResponse(json.dumps(postReturnData))
			else:
				return render(request, 'student/wrongpage.html', context)
		else :
			return redirect(reverse('student:viewCourses'))
	else :
		context = {}
		return render(request, 'student/login.html', context)

# Stores student answers from the email
@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def storeAnswer(request, id = None, qid = None, choice = None):
	if request.user.is_authenticated():
		if Student_Info.objects.filter(uuid = id).count()>0 and MCQ_Question.objects.filter(id = int(qid)).count()>0:
			student = Student_Info.objects.filter(uuid = str(id))[0]
			ques = MCQ_Question.objects.filter(id = int(qid))[0]

			#print socket.gethostbyname(request.META['SERVER_NAME'])
			# If an answer is already present
			if student.username != request.user.username :
				context = {
				"username" : request.user.username,
				"first_name": request.user.first_name,
				"displayid": 0,
				"message": "A different user is logged in. Please logout and try again.",
				}
				return render(request, 'student/studentStoreAnswer.html', context)
			if Student_Answers.objects.filter(student_id=student.id).filter(question_id =ques.id).count()>0 :
				context = {
				"username" : request.user.username,
				"first_name": request.user.first_name,
				"displayid": 1,
				"message": "You have already answered the question.",
				}
				return studentQuestionView(request, sid = student.id, qid = ques.id, topAlertFlag = 3)
				#return render(request, 'student/studentStoreAnswer.html', context)
				#return HttpResponse("You have already answered the question")
			# Time expired
			elif datetime.now().date() > ques.datetime:
				context = {
				"username" : request.user.username,
				"first_name": request.user.first_name,
				"displayid": 2,
				"message": "The time to take the quiz has elapsed!",
				}
				return render(request, 'student/studentStoreAnswer.html', context)
				#return HttpResponse("You are too late !!")
			# Correct answer
			elif ques.answer == ' '.join(['Choice',choice]):
				Student_Answers.objects.create( student=student, question=ques, selAnswer=choice, correctFlag = 1)
				context = {
				"username" : request.user.username,
				"first_name": request.user.first_name,
				"displayid": 3,
				"message": "Your answer is correct!",
				}
				temp = updateStudentMarks(request, student)
				# return render(request, 'student/studentStoreAnswer.html', context)
				# return HttpResponse("Your answer is correct")
				return studentQuestionView(request, sid = student.id, qid = ques.id, topAlertFlag = 1)
			# Incorrect answer
			else :
				Student_Answers.objects.create( student=student, question=ques, selAnswer=choice, correctFlag = 0)
				context = {
				"username" : request.user.username,
				"first_name": request.user.first_name,
				"displayid": 4,
				"message": "Your answer is incorrect!",
				}
				temp = updateStudentMarks(request, student)
				return studentQuestionView(request, sid = student.id, qid = ques.id, topAlertFlag = 0)
				# studentQuestionView(request, sid = None, qid = None, topAlertFlag = None):
				#return render(request, 'student/studentStoreAnswer.html', context)
				# return HttpResponse("Your answer is incorrect")
		else:
			context = {
			"username" : request.user.username,
			"first_name": request.user.first_name,
			"displayid": 5,
			"message": "Question has been deleted by the instructor",
			}
			return render(request, 'student/studentStoreAnswer.html', context)
			#return HttpResponse("Question has been deleted by the instructor")
	else:
		context = {}
		return render(request, 'student/login.html', context)

def retrieveStrongTopics(username):
	student = Student_Info.objects.filter(username = username)[0]
	studentAnswer = Student_Answers.objects.filter(student = student)
	answeredStatistics = studentAnswer.values('question__courseTopic').annotate(correctAnswers = Sum('correctFlag'),attempted = Count('id'))
		#print answeredStatistics
	for answer in answeredStatistics:
		percentage = float(answer['correctAnswers']) / float(answer['attempted']) * 100
		answer['percentage'] =percentage
	strongTopics = sorted(answeredStatistics,key = lambda topic: (topic['percentage']),reverse=True)
	strongTopic1 = strongTopics[0]['question__courseTopic']
	strongTopic2 = strongTopics[1]['question__courseTopic']
	strongTopic3 = strongTopics[2]['question__courseTopic']
	
	topicList = [{"name": strongTopic1, "size" : len(strongTopic1)}, {"name": strongTopic2, "size" : len(strongTopic2)},{"name": strongTopic3, "size" : len(strongTopic3)}]
	
	return topicList

@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def socialVisualization(request):
	if request.user.is_authenticated():
		username = request.user.username
		first_name = request.user.first_name
		finalOutput = {}

		student_info_master = Student_Marks.objects.filter(badge='Master')
		student_info_pro = Student_Marks.objects.filter(badge='Pro')
		student_info_amateur = Student_Marks.objects.filter(badge='Amateur')		
		student_info_novice = Student_Marks.objects.filter(badge='Novice')
		
		master_count = int(student_info_master.count())
		pro_count = int(student_info_pro.count())
		amateur_count = int(student_info_amateur.count())
		novice_count = int(student_info_novice.count())
		
		masterList = list()
		proList = list()
		amateurList = list()
		noviceList = list()

		for masters in student_info_master:
			masterList.append({"name" : str(masters.student.username),"size" : int(masters.marks),"children" : retrieveStrongTopics(masters.student.username)})
		for pros in student_info_pro:
			proList.append({"name" : str(pros.student.username),"size" : int(pros.marks),"children" : retrieveStrongTopics(pros.student.username)})
		for amateurs in student_info_amateur:
			amateurList.append({"name" : str(amateurs.student.username), "size" : int(amateurs.marks),"children" : retrieveStrongTopics(amateurs.student.username)})
		for novices in student_info_novice:
			noviceList.append({"name" : str(novices.student.username), "size" : int(novices.marks),"children" : retrieveStrongTopics(novices.student.username)})	

		masterDictionary = {"name" : "Master","children":masterList,"size" : master_count}
		proDictionary = {"name" : "Pro", "children" : proList, "size" : pro_count}
		amateurDictionary = {"name" : "Amateur", "children" : amateurList, "size" : amateur_count}
		noviceDictionary = {"name" : "Novice", "children": noviceList, "size" : novice_count}

		studentList=  list()
		studentList.append(masterDictionary)
		studentList.append(proDictionary)
		studentList.append(amateurDictionary)
		studentList.append(noviceDictionary)

		finalOutput = {"name" : "Visualization","children": studentList}
		
		
		# print str(finalOutput)

		context = {
			"username" : username,
			"first_name" : first_name,
			"data" : json.dumps(finalOutput)
		}

	return render(request, 'student/socialVisualization.html', context)

@user_passes_test(lambda u: u.groups.filter(name='student').count()>0, login_url='/student/wrongpage/')
def weakTopics(request):
	if request.user.is_authenticated():
		if 'courseId' in request.session :
			username = request.user.username
			first_name = request.user.first_name
			student = Student_Info.objects.filter(username = username)[0]
			course = Course.objects.get(id = int(request.session['courseId']))

			studentAnswer = Student_Answers.objects.filter(student = student).filter(question__course = course)

			#Code to get weakest topic
			#studentAnswer.values('question__courseTopic').annotate(Sum('correctFlag'),Count('id'))
			answeredStatistics = studentAnswer.values('question__courseTopic').annotate(correctAnswers = Sum('correctFlag'),attempted = Count('id'))
			#print answeredStatistics
			for answer in answeredStatistics:
				percentage = float(answer['correctAnswers']) / float(answer['attempted']) * 100
				# print percentage
				answer['percentage'] =percentage
			weakTopics = sorted(answeredStatistics,key = lambda topic: (topic['percentage']))
			weakTopic1 = weakTopics[0]['question__courseTopic']
			weakTopic2 = weakTopics[1]['question__courseTopic']
			weakTopic3 = weakTopics[2]['question__courseTopic']
			weakTopicPercentage1 = weakTopics[0]['percentage']
			weakTopicPercentage2 = weakTopics[1]['percentage']
			weakTopicPercentage3 = weakTopics[2]['percentage']
			recommendations = Recommendations.objects.filter(question__courseTopic__in=[weakTopic1,weakTopic2,weakTopic3]).order_by('-averageRatings')
			#print recommendations[0].averageRatings
			context = {
			 "username" : username,
			 "first_name" : first_name,
			 "courseName" : course.courseName.title(),
			 "rec1" : recommendations[0],
			 "rec2" : recommendations[1],
			 "rec3" : recommendations[2],
			 "rec4" : recommendations[3],
			 "rec5" : recommendations[4],
			 "weakTopic1" : weakTopic1,
			 "weakTopic2" : weakTopic2,
			 "weakTopic3" : weakTopic3,
			 "weakTopicPercentage1" : weakTopicPercentage1,
			 "weakTopicPercentage2" : weakTopicPercentage2,
			 "weakTopicPercentage3" : weakTopicPercentage3,
			}
			return render(request, 'student/weakestTopic.html', context)
	else:
		context = {}
		return render(request, 'student/login.html', context)

def wrongpage(request):
	if request.user.is_authenticated():
		return render(request, 'student/wrongpage.html', {})
	else:
		context = {}
		return render(request, 'account/Login.html', context)

def helpPage(request):
	if request.user.is_authenticated():
		username = request.user.username
		email = request.user.email
		userObj = User.objects.filter(email = email)[0]
		first_name = userObj.first_name

		context = {
							"username" : username,
							"first_name" : first_name,
				 }
		return render(request, 'student/studentHelpPage.html', context)
	else:
		return render(request, 'student/studentHelpPage.html', {})