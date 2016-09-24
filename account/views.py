from account.models import Student_Info, Student_UUID, Course, Student_Course, Student_Login_Log

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

#from templated_email import send_templated_mail
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage
from django.db.models import Sum,Count,Avg

import uuid
import json
import math
import socket
import uuid
from django.http import JsonResponse
import json
import threading
from random import randint

##################################################################################################################
## AUTHENTICATION VIEWS

# named as authenticate_view as there is a django function authenticate 
def authenticate_view(request):
	if request.method == 'POST':
		print request.method
		#user = authenticate(username='john', password='johnpassword')
		email = request.POST.get("email",'')		
		password = request.POST.get("password",'')

		print email

		if User.objects.filter(email = email).count()>0:
			UserObj = User.objects.filter(email = email)[0]
			username = UserObj.username
			print username
			user = authenticate(username=username, password=password)
			print username+","+password+","+User.objects.get(username=username).password
			if user is not None:
				if user.is_active:
					login(request, user)
					if request.user.groups.filter(name='student').count() > 0 :
						timezone.activate(pytz.timezone("America/Phoenix"))
						activityTimeStamp = localtime(timezone.now())
						# request.session['last_activity'] = str(activityTimeStamp)
						student = Student_Info.objects.get(username = username)
						Student_Login_Log.objects.create(
								student= student,
								activity = 'login',
								startTimestamp = activityTimeStamp,
							)
						return redirect(reverse('student:studentTodaysQuiz'))
					else:
						logout(request)
						context = { "IncorrectUsernamePassword" : True , }
						return render(request, 'account/Login.html', context)
				else:
					context = {}
					return redirect(reverse('account:login_view'))
			else:
				context = { "IncorrectUsernamePassword" : True , }
				return render(request, 'account/Login.html', context)

		else:
			context = { "IncorrectUsernamePassword" : True , }
			return render(request, 'account/Login.html', context)
	else:
		return redirect('account:notAllowed')

def login_view(request):
	if request.user.is_authenticated():
		return redirect(reverse('student:studentTodaysQuiz'))
		# if request.user.groups.filter(name='student').count() == 0 :
		# 	return redirect(reverse('instructor:questionList'))
		# else:
		# 	# request.session['last_activity'] = datetime.now()
		# 	return redirect(reverse('student:studentTodaysQuiz'))
	else:
		context = {}
		return render(request, 'account/Login.html', context)

def logout_view(request):
	# logout calls request.session.flush() internally
	logout(request)
	context = {}
	return render(request, 'account/Login.html', context)

def signUp(request):
	return render(request, 'account/Signup.html', {})

def generateCourseDropdown(request):
	if request.GET.has_key('username'):
		optionDict = {}
		i = 0
		courses = Course.objects.all()
		for course in courses :
			i = i+1
			optionDict["course"+str(i)] = course.courseName + " | " + course.batch
		print optionDict
		#return HttpResponse(json.dumps(optionDict), content_type='application/json')
		return HttpResponse(json.dumps(optionDict))
	else:
		return redirect('notAllowed')

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

def registrationFormProcessing(request):
	if request.POST.has_key('email') :
		firstName = str(request.POST.get('firstName','')).strip().title()
		lastName = str(request.POST.get('lastName','')).strip().title()
		username = firstName + str(randint(0,100000))
		email = request.POST.get('email','')
		courseName = request.POST.get('courses','')
		password1 = request.POST.get('password1','')
		password2 = request.POST.get('password2','')
		u = uuid.uuid4()

		courseName = courseName.split('|')[0].strip()
		course = Course.objects.get(courseName = courseName)

		if Student_Info.objects.filter(email = email).count()==0:
			user = User.objects.create_user(
					username = username,
					first_name = firstName,
					last_name = lastName,
					email =  email,
					password = password1,
					)
			user.groups.add(Group.objects.get(name='student'))
			user.save()

			Student_Info.objects.create(
				username = username,
				first_name = firstName,
				last_name = lastName,
				email =  email,
				password = password1,
				groups = 'student',
				uuid = str(u.hex),
				session_key = '',
				cookie_key = '', 
				)
			student = Student_Info.objects.get(email = email)

			Student_Course.objects.create(
				student = student,
				course = course,
				enrolledDate = datetime.now().date(),
				)

			context = {
				"firstName" : firstName,
				"lastName" : lastName,
				"username" : username
			}

			to_email = []
			to_email.append(email)
			subject = "QUIZIT! Account creation confirmation"
			from_email = 'learnjava.quiz@gmail.com'
			html_content = get_template('account/RegistrationEmail.html').render(Context(context))
			msg = EmailMessage(subject, html_content, to= to_email, from_email=from_email)
			# msg = EmailMultiAlternatives(subject, 'hello', to=to, from_email=from_email)
			# msg.attach_alternative(html_content, "text/html")
			msg.content_subtype = 'html'
			msg.send()

			return render(request, 'account/RegistrationConfirmation.html')
		else :
			return redirect(reverse('account:notAllowed'))
	else :
		return redirect(reverse('account:notAllowed'))

# 
def forgotPassword(request):
	return render(request, 'account/ForgotPassword.html', {})

# Sends a password reset email and notifies the end user
def resetPasswordSendMail(request):
	if request.POST.has_key('resetEmail'):
		email = request.POST.get('resetEmail')

		# if email is entered
		if "@" in email:
			if User.objects.filter(email = email).count() == 0 :
				context = { "IncorrectUsernameEmail" : True, }
				return render(request, 'account/ForgotPassword.html', context)	
		# if username is entered
		# elif User.objects.filter(username=emailUserName).count() > 0 :
		# 	email = User.objects.get(username=emailUserName).email
		else :
			context = { "IncorrectUsernameEmail" : True, }
			return render(request, 'account/ForgotPassword.html', context)
		
		student = Student_Info.objects.get(email = email)
		uuidVar = uuid.uuid4()
		if Student_UUID.objects.filter(student = student).count() == 1:
			Student_UUID.objects.filter(student=student).update(
				uuid = str(uuidVar.hex),
				startTimestamp = datetime.now(),
				uidType = 2,
			)
		else:
			Student_UUID.objects.create(
				student = student,
				uuid = str(uuidVar.hex),
				startTimestamp = datetime.now(),
				uidType = 2,
			)
		# download_thread = threading.Thread(target=function_that_downloads, args=my_args)
		# download_thread.start()
		# Sending the reset link
		to_email = []
		to_email.append(email)
		context = {	"firstName" : student.first_name,
					"username" : student.username,
					"resetURL" : "http://" + request.get_host() + "/account/resetPasswordForm/"+ str(uuidVar.hex) + "/"
				}
		
		subject = "QUIZIT! : Password Reset"
		from_email = 'learnjava.quiz@gmail.com'
		html_content = get_template('account/ResetPasswordMail.html').render(Context(context))
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

		return render(request, 'account/ResetPasswordDirections.html', context)
	else:
		return redirect(reverse('account:notAllowed'))

def resetPasswordForm(request, id= None):
	if Student_UUID.objects.filter(uuid = id):
		student_UUID_Object = Student_UUID.objects.get(uuid = id)
		Hrs24Delta = timezone.now() + timezone.timedelta(hours=24)
		# check if the UID is valid(24 hrs)
		# also check if the uid was set for password reset. Value 2
		if timezone.now() < Hrs24Delta and student_UUID_Object.uidType == 2:
			student = student_UUID_Object.student
			context = {
				"username" : student.username
			}
			return render(request, 'account/ResetPasswordForm.html', context)
		else:
			return redirect(reverse('account:notAllowed'))
		Student_UUID.objects.filter(uuid = id).update()
	else:
		return redirect(reverse('account:notAllowed'))

def resetPasswordFormProcessing(request):
	if request.POST.has_key('username'):
		username = request.POST.get('username','')
		password = request.POST.get('password1','')
		student = Student_Info.objects.get(username = username)
		Student_Info.objects.filter(username = username).update(password = password)
		# update doesnt work for changing password
		user = User.objects.get(username = username)
		user.set_password(password)
		user.save()
		# type 0 means the uid is inactive
		Student_UUID.objects.filter(student = student).update( uidType=0,)
		return render(request, 'account/ResetPasswordConfirmation.html', {} )
	else:
		return redirect(reverse('account:notAllowed'))

def notAllowed(request):
	return render(request, 'account/wrongpage.html', {} )

def helpPage(request):
	return render(request, 'account/studentHelpPage.html', {})