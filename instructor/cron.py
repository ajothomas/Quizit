from instructor.models import MCQ_Question, Recommendations
from account.models import Student_Info, Student_UUID, Course, Course_Topics, Instructor_Info, Instructor_Course, Student_Course
from student.models import Student_Marks, Student_Answers
from datetime import datetime, timedelta
from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage
from django.core import serializers

def sendMail_view():
	users = Student_Info.objects.filter(username='ajothomas')
	print "Hello world: Crontab"

	for currUser in users:
		currEmail = []
		currEmail.append(currUser.email)

		
		uuidVar = uuid.uuid4()
		if Student_UUID.objects.filter(student = currUser).count() == 1:
			Student_UUID.objects.filter(student = currUser).update(
				uuid = str(uuidVar.hex),
				startTimestamp = datetime.now(),
				uidType = 1,
			)
		else:
			Student_UUID.objects.create(
				student = student,
				uuid = str(uuidVar.hex),
				startTimestamp = datetime.now(),
				uidType = 1,
			)
		currUuid = str(uuidVar.hex)

		question = MCQ_Question.objects.all()[0]
		choiceList = list(string.uppercase[:int(question.numChoices)])
		
		context = {
				"username" : currUser.first_name,
				"date" : datetime.now().date(),
				"question" : quiz.question
		}

		for choice in choiceList:
			context.update(
				"choice"+choice+"URL" : "http://" + request.get_host() + "/instructor/answer/" + currUuid + "/" +str(quiz.id) + "/"+ choice + "/",
				"choice"+choice : getattr(quiz, "choice"+choice),
			)

		#"choiceAURL" : "http://" + request.get_host() + "/instructor/answer/" + currUuid + '/'+str(quiz.id)+'/A/',
		
		subject = "QUIZIT! Quiz of the day : "+str(datetime.now().date())
			
		to = currEmail
		from_email = 'learnjava.quiz@gmail.com'
		html_content = get_template('instructor/sendQuestionEmail.html').render(Context(context))
		msg = EmailMessage(subject, html_content, to=to, from_email=from_email)
		# msg = EmailMultiAlternatives(subject, 'hello', to=to, from_email=from_email)
		# msg.attach_alternative(html_content, "text/html")
		msg.content_subtype = 'html'
		msg.send()