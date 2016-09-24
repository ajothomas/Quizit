from __future__ import unicode_literals
from instructor.models import MCQ_Question, Recommendations
from account.models import Student_Info, Student_UUID, Course, Course_Topics, Instructor_Info, Instructor_UUID, Instructor_Course, Student_Course
from student.models import Student_Marks, Student_Answers, Student_Explanations, Student_Answers_ActivityLog
from django.db.models import Avg, Max, Min, Sum

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
from random import randint

from django.db.models import Sum,Count,Avg
import math
import socket
import uuid
from django.http import JsonResponse
import json
import nltk
import pysolr
from collections import OrderedDict

##################################################################################################################
## LOGIN and AUTHENTICATION VIEWS


def authenticate_view(request):
	if request.method == 'POST':
		email = request.POST.get("email",'')		
		password = request.POST.get("password",'')

		if User.objects.filter(email = email).count()>0:
			UserObj = User.objects.filter(email = email)[0]
			username = UserObj.username
			print username +":"+password
			user = authenticate(username=username, password=password)
			print user
			if user is not None:
				print "Hi2"
				if user.is_active:
					login(request, user)
					if request.user.groups.filter(name='admin').count() != 0 :
						return redirect(reverse('instructor:viewCourses'))
					else:
						context = { "IncorrectUsernamePassword" : True , }
						return render(request, 'instructor/account/Login.html', context)
				else:
					context = {}
					return redirect(reverse('instructor:login_view'))
			else:
				context = { "IncorrectUsernamePassword" : True , }
				return render(request, 'instructor/account/Login.html', context)

		else:
			context = { "IncorrectUsernamePassword" : True , }
			return render(request, 'instructor/account/Login.html', context)
	else:
		return redirect('account:notAllowed')

def login_view(request):
	if request.user.is_authenticated():
		if request.user.groups.filter(name='student').count() == 0 :
			return redirect(reverse('instructor:viewCourses'))
		else:
			context = { "IncorrectUsernamePassword" : True , }
			return render(request, 'instructor/account/Login.html', context)
	else:
		context = {}
		return render(request, 'instructor/account/Login.html', context)

def logout_view(request):
	logout(request)
	context = {}
	return render(request, 'instructor/account/Login.html', context)

def verifyUsername(request):
	if request.GET.has_key('username'):
		username = request.GET.get('username',' ')
		if User.objects.filter(username = username) :
			return HttpResponse("1")
		else:
			return HttpResponse("0")
	else:
		return redirect('notAllowed')

def verifyEmail(request):
	if request.GET.has_key('email'):
		email = request.GET.get('email',' ')
		if User.objects.filter(email = email) :
			return HttpResponse("1")
		else:
			return HttpResponse("0")
	else:
		return redirect('notAllowed')

def forgotPassword(request):
	return render(request, 'instructor/account/ForgotPassword.html', {})

# Sends a password reset email and notifies the end user
def resetPasswordSendMail(request):
	if request.POST.has_key('resetEmail'):
		email = request.POST.get('resetEmail')

		# if email is entered
		if "@" in email:
			if Instructor_Info.objects.filter(email = email).count() == 0 :
				context = { "IncorrectUsernameEmail" : True, }
				return render(request, 'instructor/account/ForgotPassword.html', context)	
		# if username is entered
		# elif User.objects.filter(username=emailUserName).count() > 0 :
		# 	email = User.objects.get(username=emailUserName).email
		else :
			context = { "IncorrectUsernameEmail" : True, }
			return render(request, 'instructor/account/ForgotPassword.html', context)
		
		instructor = Instructor_Info.objects.get(email = email)
		uuidVar = uuid.uuid4()
		if Instructor_UUID.objects.filter(instructor = instructor).count() == 1:
			Instructor_UUID.objects.filter(instructor = instructor).update(
				uuid = str(uuidVar.hex),
				startTimestamp = datetime.now(),
				uidType = 2,
			)
		else:
			Instructor_UUID.objects.create(
				instructor = instructor,
				uuid = str(uuidVar.hex),
				startTimestamp = datetime.now(),
				uidType = 2,
			)

		# Sending the reset link
		to_email = []
		to_email.append(email)
		context = {	"firstName" : instructor.first_name,
					"username" : instructor.username,
					"resetURL" : "http://" + request.get_host() + "/instructor/resetPasswordForm/"+ str(uuidVar.hex) + "/"
				}
		
		subject = "QUIZIT! : Password Reset"
		from_email = 'learnjava.quiz@gmail.com'
		html_content = get_template('instructor/account/ResetPasswordMail.html').render(Context(context))
		msg = EmailMessage(subject, html_content, to= to_email, from_email=from_email)
		# msg = EmailMultiAlternatives(subject, 'hello', to=to, from_email=from_email)
		# msg.attach_alternative(html_content, "text/html")
		msg.content_subtype = 'html'
		msg.send()

		# Confirmation mail page
		if email.find("gmail") != -1:
		    emailProvider = "https://www.gmail.com/"
		elif email.find("aol") != -1:
		    emailProvider = "https://www.mail.aol.com/"
		elif "yahoo" in email:
		    emailProvider = "https://mail.yahoo.com/"
		elif "asu.edu" in email:
		    emailProvider = "https://www.gmail.com/"
		elif "outlook" in email:
		    emailProvider = "https://www.live.com/"
		elif "live" in email:
		    emailProvider = "https://www.live.com/"
		elif "mail" in email:
		    emailProvider = "https://www.mail.com/"
		elif "zoho" in email:
		    emailProvider = "https://www.zoho.com/mail/login.html"
		print

		context = { "email" : email ,
					"emailProvider" : emailProvider ,
					}

		return render(request, 'instructor/account/ResetPasswordDirections.html', context)
	else:
		return redirect(reverse('instructor:notAllowed'))

def resetPasswordForm(request, id= None):
	if Instructor_UUID.objects.filter(uuid = id):
		instructor_UUID_Object = Instructor_UUID.objects.get(uuid = id)
		Hrs24Delta = timezone.now() + timezone.timedelta(hours=24)
		# check if the UID is valid(24 hrs)
		# also check if the uid was set for password reset. Value 2
		if timezone.now() < Hrs24Delta and instructor_UUID_Object.uidType == 2:
			instructor = instructor_UUID_Object.instructor
			context = {
				"username" : instructor.username
			}
			return render(request, 'instructor/account/ResetPasswordForm.html', context)
		else:
			return redirect(reverse('instructor:notAllowed'))
	else:
		return redirect(reverse('instructor:notAllowed'))

def resetPasswordFormProcessing(request):
	if request.POST.has_key('username'):
		username = request.POST.get('username','')
		password = request.POST.get('password1','')
		instructor = Instructor_Info.objects.get(username = username)
		Instructor_Info.objects.filter(username = username).update(password = password)
		# update doesnt work for changing password
		user = User.objects.get(username = username)
		user.set_password(password)
		user.save()
		# type 0 means the uid is inactive
		Instructor_UUID.objects.filter(instructor = instructor).update( uidType=0,)
		return render(request, 'instructor/account/ResetPasswordConfirmation.html', {} )
	else:
		return redirect(reverse('instructor:notAllowed'))


def signUp(request):
	return render(request, 'instructor/account/Signup.html', {})

def registrationFormProcessing(request):
	if request.POST.has_key('email') :
		firstName = str(request.POST.get('firstName','')).strip().title()
		lastName = str(request.POST.get('lastName','')).strip().title()
		username = firstName + str(randint(0,100000))
		email = request.POST.get('email','')
		password1 = request.POST.get('password1','')
		password2 = request.POST.get('password2','')
		u = uuid.uuid4()

		if Instructor_Info.objects.filter(email = email).count()==0:
			user = User.objects.create_user(
					username = username,
					first_name = firstName,
					last_name = lastName,
					email =  email,
					password = password1,
					)

			user.groups.add(Group.objects.get(name='admin'))
			user.save()

			Instructor_Info.objects.create(
				username = username,
				first_name = firstName,
				last_name = lastName,
				email =  email,
				password = password1,
				uuid = str(u.hex),
			)
			instructor = Instructor_Info.objects.get(email = email)

			context = {
				"firstName" : firstName,
				"lastName" : lastName,
				"username" : username,
				"email" : email,
			}

			to_email = []
			to_email.append(email)
			subject = "QUIZIT! Account creation confirmation"
			from_email = 'learnjava.quiz@gmail.com'
			html_content = get_template('instructor/account/RegistrationEmail.html').render(Context(context))
			msg = EmailMessage(subject, html_content, to= to_email, from_email=from_email)
			msg.content_subtype = 'html'
			msg.send()

			return render(request, 'instructor/account/RegistrationConfirmation.html')
		else :
			return redirect(reverse('notAllowed'))
	else :
		return redirect(reverse('account:notAllowed'))

@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def createCourseProcessing(request):
	print "Hello1"
	if request.method == 'POST':
		print "Hello"
		username = request.POST.get("username",'')
		courseName = request.POST.get("courseName",'')
		startDate = request.POST.get("startDate",'')
		endDate = request.POST.get("endDate",'')
		batch = request.POST.get("batch",'')
		instructor = Instructor_Info.objects.get(username = username)

		course = Course.objects.create(
				courseName = courseName,
				batch = batch,
				startDate = datetime.strptime(startDate,"%m/%d/%Y"),
				endDate = datetime.strptime(endDate, "%m/%d/%Y"),
			)

		Instructor_Course.objects.create( 
			course = course ,
			instructor = instructor ,
		)
		return HttpResponse("Hello")
	else:
		return redirect('account:notAllowed')

@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def viewCourses(request):
	if request.user.is_authenticated():
		username = request.user.username
		first_name = request.user.first_name
		
		instructor = Instructor_Info.objects.get(username = username)
		instructorCourses = Instructor_Course.objects.filter(instructor = instructor )
		print instructorCourses
		context = {
			"username" : username ,
			"first_name" : first_name,
			"instructorCourses" : instructorCourses,
		}
		return render(request, 'instructor/viewCourses.html', context)
	else:
		return redirect(reverse('instructor:login_view'))

@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def createCourse(request):
	if request.user.is_authenticated():
		username = request.user.username
		first_name = request.user.first_name
		
		context = {
			"username" : username ,
			"first_name" : first_name,
		}
		return render(request, 'instructor/createCourse.html', context)
	else:
		return redirect(reverse('instructor:login_view'))

@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def selectCourse(request):
	if request.method == 'POST':
		courseID = request.POST.get('courseID','')
		request.session['courseID'] = courseID
		return HttpResponse("Hello")

#Instructor Dashbboard/Landing
@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def instructorDashboard(request):
	if request.user.is_authenticated():
		if 'courseID' in request.session :
			username = request.user.username
			first_name = request.user.first_name
			course = Course.objects.get(id = int(request.session['courseID']))

			students = Student_Course.objects.filter(course = course)
			questions = MCQ_Question.objects.filter(course = course)
			# questionsTillToday = MCQ_Question.objects.filter(course = course)
			topics = Course_Topics.objects.filter(course = course)
			activities = Student_Answers_ActivityLog.objects.filter(question__course = course)
			studentAnswers = Student_Answers.objects.filter(question__course = course)
			studentNotes = Student_Explanations.objects.filter(question__course = course)
			attemptsDict = Student_Answers.objects.filter(question__course = course).aggregate( Sum('numAttempts'), Sum('numCorrectAttempts'))
			attemptsTopicList = Student_Answers.objects.filter(question__course = course).values('question__courseTopic').annotate( Sum('numAttempts'), Sum('numCorrectAttempts'))
			
			print attemptsTopicList
			attemptsTopicDict = OrderedDict()
			for item in attemptsTopicList:
				tempDict = OrderedDict()
				tempDict["courseTopic"] = item['question__courseTopic']
				tempDict["numAttempts"] = item['numAttempts__sum']
				tempDict["numCorrectAttempts"] = item['numCorrectAttempts__sum']
				if item['numAttempts__sum'] == 0:
					tempDict["percSuccess"] = "0%"
				else:
					tempDict["percSuccess"] = "%d%%"%(float(item['numCorrectAttempts__sum'])/item['numAttempts__sum']*100)
				attemptsTopicDict[item['question__courseTopic']] = tempDict
			
			print attemptsTopicDict

			allMetrics = {
				"numAllStudents" : students.count(),
				"numAllQuestions" : questions.count(),
				"numAllTopics" : topics.count(),
				"numAllAttempts" : attemptsDict['numAttempts__sum'],
				"numAllCorrectAttempts" : attemptsDict['numCorrectAttempts__sum'],

				#"attemptsTopicList" : attemptsTopicList,
				"attemptsTopicDict": attemptsTopicDict,
			}

			context = {
				'username' : username,
				'first_name' : first_name,				
			}

			context.update(allMetrics)
			return render(request, 'instructor/instructorDashboard.html', context)
		else :
			return redirect(reverse('instructor:viewCourses'))
	else:
		context = {}
		return redirect(reverse('account:login_view'))

# Renders the list of questions
@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def questionList(request):
	if request.user.is_authenticated():
		if 'courseID' in request.session :
			username = request.user.username
			first_name = request.user.first_name
			course = Course.objects.get(id = int(request.session['courseID']))
			queryset = MCQ_Question.objects.filter(course = course).order_by('-datetime')
			print queryset
			#queryset = MCQ_Question.objects.all()
			context = {
				"questionlist" : queryset ,
				"username" : username ,
				"first_name" : first_name,
			}
			# return HttpResponse("Hello world !")
			return render(request, 'instructor/questionList.html', context)
		else:
			return redirect(reverse('instructor:viewCourses'))
	else:
		context = {}
		return redirect(reverse('instructor:login_view'))

# Renders the list of questions
@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def instructorCalendar(request):
	if request.user.is_authenticated():
		if 'courseID' in request.session :
			username = request.user.username
			first_name = request.user.first_name
			course = Course.objects.get(id = int(request.session['courseID']))
			courseQuestions = MCQ_Question.objects.filter(course = course)
			
			# setting the timezone
			timezone.activate(pytz.timezone("America/Phoenix"))
			localtime(timezone.now()).date()

			# creating a python dictionary which will be read as a JSON object by javascript
			eventData = {"dates":[]}

			for question in courseQuestions:

				studentAnswers = Student_Answers.objects.filter(question__course = course).filter(question = question)

				numCorrectAttempts = 0
				numAttempts = 0
				numStudents = 0

				for studentAnswer in studentAnswers :
					numCorrectAttempts = numCorrectAttempts + studentAnswer.numCorrectAttempts
					numAttempts = numAttempts + studentAnswer.numAttempts
					if studentAnswer.numAttempts > 0:
						numStudents = numStudents + 1
				
				# numStudents = studentAnswers.count()

				if numAttempts == 0:
					cssName = ""
				elif float(numCorrectAttempts)/float(numAttempts) >= 0.9:
					cssName = "dateGreen"
				elif float(numCorrectAttempts)/float(numAttempts) > 0.7:
					cssName = "dateOrange"
				else:
					cssName = "dateRed"

				# Creating edit flag based on the date of quiz wrt to today's date
				date = json.dumps(question.datetime.isoformat())
				if question.datetime > localtime(timezone.now()).date():
					editFlag = 1
				else :
					editFlag = 0

				datesObj = {
					"date" : date,
					"questionText" : question.question,
					"questionID" : question.id,
					"editFlag" : editFlag,
					"cssName" : cssName,
					"numCorrectAttempts" : numCorrectAttempts,
					"numAttempts" : numAttempts,
					"numStudents" : numStudents,
				}

				print datesObj

				eventData["dates"].append(datesObj);

			context = {
				"username" : username ,
				"first_name" : first_name,
				"courseName" : course.courseName.title(), 
				"eventData" : json.dumps(eventData),
			}

			# return HttpResponse("Hello world !")
			return render(request, 'instructor/instructorCalendar.html', context)
		else:
			return redirect(reverse('instructor:viewCourses'))
	else:
		context = {}
		return redirect(reverse('instructor:login_view'))


@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def generateCourseTopicDropdown(request):
	if request.user.is_authenticated():
		if request.GET.has_key('username'):
			if 'courseID' in request.session :
				optionDict = {}
				i = 0
				# make course selection dynamic
				course = Course.objects.get(id = int(request.session['courseID']))
				# getting all course topics for the course
				courseTopics = course.course_topics_set.all().order_by('topicName')
				#courseTopics = courseTopics.order_by('topicName')
				
				print courseTopics
				for courseTopic in courseTopics :
					i = i+1
					optionDict["courseTopic"+str(i)] = courseTopic.topicName

				# sorts the dictionary and returns a list. Dictionaries are not sortable in Python
				optionDict = sorted(optionDict.items(), key=lambda (k,v): v)

				#return HttpResponse(json.dumps(optionDict), content_type='application/json')
				return HttpResponse(json.dumps(optionDict))
			else:
				return redirect(reverse('instructor:viewCourses'))
		else:
			return redirect('instructor:wrongpage')
	else:
		return redirect(reverse('account:login_view'))

@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def checkNewTopic(request):
	if request.user.is_authenticated():
		if request.GET.has_key('username'):
			newTopicName = request.GET.get('newTopicName','')
			course = Course.objects.get(id = int(request.session['courseID']))
			# if similar topics were found
			if Course_Topics.objects.filter(course = course).filter(topicName__icontains = newTopicName).count()>0:
				topics = Course_Topics.objects.filter(course = course).filter(topicName__icontains = newTopicName)
				topicString = ""
				for topic in topics:
					topicString = topicString + "," + topic.topicName
					topicString = topicString[1:]
				print topicString
				jsonData = [topicString, 0]

			# not found
			else:
				jsonData = ['',2]
			return HttpResponse(json.dumps(jsonData))
		else:
			return redirect('instructor:wrongpage')
	else:
		return redirect(reverse('account:login_view'))

# Sending a plain text email
def sendMail_view(request):
	if request.user.is_authenticated():
		queryset = MCQ_Question.objects.filter(datetime__year=datetime.now().year, datetime__month=datetime.now().month, datetime__day=datetime.now().day)
		quiz = queryset[0]
		print quiz.question
		print quiz.answer

		toEmail = []
		# select enrolled students
		#users = Student_Info.objects.filter(groups = 'student')
		#print users
		users = Student_Info.objects.filter(username='ajothomas')
		for currUser in users:
			currEmail = []
			currEmail.append(currUser.email)

			studentMark = Student_Marks.objects.filter(student = currUser)[0]
			specialMessage = ""
			if studentMark.currStreak <= -2:
				currStreak = studentMark.currStreak * -1
				specialMessage = 'You are currently on a streak of ' + str(currStreak) + ' successive incorrect answers. You will lose 2 additional marks with every wrong answer. We recommend you to work on your weak areas by reviewing the recommended readings section. Please check the website'
			else :
				currStreak = studentMark.currStreak * 1
				specialMessage = 'You are currently on a streak of ' + str(currStreak) + ' successive correct answers. You will gain 2 additional marks as bonus with every correct answer. We want you to maintain your streak and recommend you to first review the readings curated for you. Please check the website'
			
			currUuid = currUser.uuid
			context = {
				"username" : currUser.first_name,
				"date" : datetime.now().date(),
				"question" : quiz.question,
				"choiceAURL" : ''.join(['http://localhost:1234/instructor/answer/',currUuid,'/',str(quiz.id),'/A/']) ,
				"choiceBURL" : ''.join(['http://localhost:1234/instructor/answer/',currUuid,'/',str(quiz.id),'/B/']) ,
				"choiceCURL" : ''.join(['http://localhost:1234/instructor/answer/',currUuid,'/',str(quiz.id),'/C/']) ,
				"choiceDURL" : ''.join(['http://localhost:1234/instructor/answer/',currUuid,'/',str(quiz.id),'/D/']) ,
				"choiceA" : quiz.choiceA,
				"choiceB" : quiz.choiceB,
				"choiceC" : quiz.choiceC,
				"choiceD" : quiz.choiceD,
				"specialMessage" : specialMessage,
			}
			subject = "QUIZIT! Quiz of the day : "+str(datetime.now().date())
			
			to = currEmail
			print to
			from_email = 'learnjava.quiz@gmail.com'
			html_content = get_template('instructor/sendQuestionEmail.html').render(Context(context))
			msg = EmailMessage(subject, html_content, to=to, from_email=from_email)
			# msg = EmailMultiAlternatives(subject, 'hello', to=to, from_email=from_email)
			# msg.attach_alternative(html_content, "text/html")
			msg.content_subtype = 'html'
			msg.send()
		print "Outside loop"
		return HttpResponse('email_two')
	else:
		context = {}
		return redirect(reverse('account:login_view'))

# Renders a MCQ Question Form
@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def questionForm(request):
	if request.user.is_authenticated():
		username = request.user.username
		first_name = request.user.first_name
		course = Course.objects.get(id = int(request.session['courseID']))
		context = {
			"username" : username ,
			"first_name" : first_name ,
			"courseID" : course.id
		}
		return render(request, 'instructor/questionForm.html', context)
	else:
		context = {}
		return redirect(reverse('account:login_view'))

# Renders a prefilled MCQ form
@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def questionEdit(request, id=None):
	#print MCQ_Question.objects.get(id=id).datetime
	if request.user.is_authenticated():
		username = request.user.username
		first_name = request.user.first_name
		context = {
			"question" : MCQ_Question.objects.get(id=id) ,
			"username" : username ,
			"first_name" : first_name ,
		}
		return render(request, 'instructor/questionEdit.html', context)
	else:
		context = {}
		return redirect(reverse('account:login_view'))

# Renders a prefilled MCQ form
@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def questionView(request, id=None):
	#print MCQ_Question.objects.get(id=id).datetime
	if request.user.is_authenticated():
		username = request.user.username
		first_name = request.user.first_name
		question = MCQ_Question.objects.get(id=id)
		course = Course.objects.get(id = int(request.session['courseID']))

		studentAnswers = Student_Answers.objects.filter(question__course = course).filter(question = question)
		numCorrectAttempts = 0
		numAttempts = 0
		numStudents = 0
		for studentAnswer in studentAnswers :
			numCorrectAttempts = numCorrectAttempts + studentAnswer.numCorrectAttempts
			numAttempts = numAttempts + studentAnswer.numAttempts
			if studentAnswer.numAttempts > 0:
				numStudents = numStudents + 1

		numNotes = Student_Explanations.objects.filter(question = question).count()

		notes = None
		notesFlag = False

		if Student_Explanations.objects.filter(question = question).count()>0:
			notes = Student_Explanations.objects.filter(question = question)
			notesFlag = True

		context = {
			"questionText" : MCQ_Question.objects.get(id=id).question ,
			"question" : question ,
			"username" : username ,
			"first_name" : first_name ,
			"numAttempts" : numAttempts,
			"numCorrectAttempts" : numCorrectAttempts,
			"numStudents" : numStudents,
			"numNotes" : numNotes,
			"notes" : notes,
			"notesFlag" : notesFlag,
		}
		return render(request, 'instructor/questionView.html', context)
	else:
		context = {}
		return redirect(reverse('account:login_view'))


@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def questionUpdate(request):
	if request.method == 'POST':

		course = Course.objects.get(id = int(request.session['courseID']))

		id = request.POST.get('id')
		question = request.POST.get('question')
		newTopicFlag = request.POST.get('newTopicFlag')
		courseTopic = request.POST.get('courseTopic')
		numChoices = request.POST.get('numChoices')
		choiceA = request.POST.get('choice1')
		choiceB = request.POST.get('choice2')
		choiceC = request.POST.get('choice3')
		choiceD = request.POST.get('choice4')
		choiceE = request.POST.get('choice5');
		choiceF = request.POST.get('choice6');
		answer = request.POST.get('answer')
		level = request.POST.get('level')
		datetime_var = request.POST.get('datetime')
		print "Inside Question Update";
		print "Date time : "+datetime_var;

		MCQ_Question.objects.filter(id=id).update(
			question = question,
			courseTopic = courseTopic,
			numChoices = numChoices,
			choiceA = choiceA,
			choiceB = choiceB,
			choiceC = choiceC,
			choiceD = choiceD,
			choiceE = choiceE,
			choiceF = choiceF,
			answer = answer,
			level = level,
			datetime = datetime.strptime(datetime_var, "%m/%d/%Y")
			)

		if int(newTopicFlag) == 1 :
			Course_Topics.objects.create(
				course = course,
				topicName = courseTopic,
				);

	return HttpResponse('')

#Processing Text to filter out certain characters for keyword extraction
def processText(text):
	return text.replace("."," ").replace(","," ").replace("="," ").replace(";"," ").replace("("," ").replace(")"," ").replace(":"," ").replace("*"," ").replace("}"," ").replace("{"," ").replace("/"," ").replace("<"," ").replace(">"," ").replace("]"," ").replace("["," ")

#Hits Solr and provides recommendations for each questionProcessing
# def getRecommendations(question, courseTopic):
# 	queryString = courseTopic
# 	keyWords = set()
# 	tokens = nltk.pos_tag(nltk.word_tokenize(processText(question)))
# 	for token in tokens:
# 		if token[1].find('NN') != -1:
# 			keyWords.add(nltk.PorterStemmer().stem_word(token[0]))
# 	for keyWord in keyWords:
# 		queryString = queryString + ' OR ' + keyWord
# 	solr = pysolr.Solr("http://localhost:8010/solr/java_materials", timeout=10)
# 	return solr.search(queryString)

# Processes the ajax call to store the MCQ form data in MCQ_Question models
@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def questionProcessing(request):
	if request.method == 'POST':
		
		questionText = request.POST.get('question')
		courseTopic = request.POST.get('courseTopic')
		newTopicFlag = request.POST.get('newTopicFlag')
		numChoices = request.POST.get('numChoices')
		choiceA = request.POST.get('choice1');
		choiceB = request.POST.get('choice2');
		choiceC = request.POST.get('choice3');
		choiceD = request.POST.get('choice4');
		choiceE = request.POST.get('choice5');
		choiceF = request.POST.get('choice6');
		# the answer is stored as choice1, choice2, choice3 and so on...
		answer = request.POST.get('answer')
		level = request.POST.get('level')
		datetime_var = request.POST.get('datetime')

		course = Course.objects.get(id = int(request.session['courseID']))

		question = MCQ_Question.objects.create(
			question = questionText,
			course = course,
			courseTopic = courseTopic,
			choiceA = choiceA,
			choiceB = choiceB,
			choiceC = choiceC,
			choiceD = choiceD,
			choiceE = choiceE,
			choiceF = choiceF,
			numChoices = numChoices,
			answer = answer,
			level = level,
			datetime = datetime.strptime(datetime_var, "%m/%d/%Y")
			)

		studentCourses = Student_Course.objects.filter( course = course )
		for studentCourse in studentCourses:
			student = studentCourse.student
			Student_Answers.objects.create(
				student = student,
				question = question,
				)

		# recommendations = getRecommendations(question, courseTopic)

		# counter = 0

		# for recommendation in recommendations:
		# 	#print recommendation['id']
		# 	fileName = '../quizit/index/'+recommendation['id']
		# 	fileHandle = open(fileName,"r")
		# 	fileContent = fileHandle.read()
		# 	Recommendations.objects.create(
		# 	question = MCQ_Question.objects.filter(question = question)[0],
		# 	text = fileContent,
		# 	fileName = fileName,
		# 	rank = counter+1,
		# 	averageRatings = 100 - (counter*10)
		# 	)
		# 	#print fileName
		# 	counter = counter + 1
		
		if int(newTopicFlag) == 1 :
			Course_Topics.objects.create(
				course = course,
				topicName = courseTopic,
				);

	return HttpResponse('')

def checkDuplicateDate(request):
	if request.method == 'POST':
		selectedDate = request.POST.get('selectedDate','')
		selectedDateFormatted = datetime.strptime(selectedDate, "%m/%d/%Y")
		course = Course.objects.get(id = int(request.session['courseID']))
		if MCQ_Question.objects.filter(course = course).filter(datetime = selectedDateFormatted).count()>0:
			print MCQ_Question.objects.filter(course = course).filter(datetime = selectedDateFormatted).count()
			return HttpResponse('1')
		else:
			return HttpResponse('0')
	else :
		return redirect(reverse('account:wrongpage'))			

# Processes the ajax call to store the MCQ form data in MCQ_Question models
@user_passes_test(lambda u: u.groups.filter(name='admin').count() != 0, login_url='/instructor/wrongpage/')
def deleteQuiz(request):
	if request.user.is_authenticated():
		if request.method == 'POST':
			questionID = request.POST.get("questionID","")
			MCQ_Question.objects.filter( id= int(questionID) ).delete()
			return HttpResponse("Done")
		else: 
			return redirect(reverse('account:wrongpage'))	
	else:
		context = {}
		return redirect(reverse('account:login_view'))

# to index and populate the initial set of recommendations
def populateRecommendation(request):
	questionSet = MCQ_Question.objects.all()
	for question in questionSet:
		queryString = question.courseTopic
		keyWords = set()
		tokens = nltk.pos_tag(nltk.word_tokenize(processText(question.question)))
		for token in tokens:
			if token[1].find('NN') != -1:
				keyWords.add(nltk.PorterStemmer().stem_word(token[0]))
		for keyWord in keyWords:
			queryString = queryString + ' OR ' + keyWord

		solr = pysolr.Solr("http://localhost:8010/solr/java_materials", timeout=10)
		recommendations = solr.search(queryString)
		counter = 0
		for recommendation in recommendations:
			fileName = '../quizit/index/'+recommendation['id']
			fileHandle = open(fileName,"r")
			fileContent = fileHandle.read()
			Recommendations.objects.create(
				question = question,text = fileContent
				,fileName = recommendation['id']
				,rank = counter+1
				,averageRatings = 100 - (counter*10)
				)
			counter = counter + 1
	return HttpResponse('Done')

def notAllowed(request):
	return render(request, 'instructor/wrongpage.html', {} )