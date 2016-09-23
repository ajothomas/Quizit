"""quizit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
from student import views
from django.core.urlresolvers import reverse

app_name = 'student'
urlpatterns = [	
	url(r'^$', views.viewCourses, name='viewCourses'),
	url(r'^viewCourses/$', views.viewCourses, name='viewCourses'),
	url(r'^selectCourse/$', views.selectCourse, name='selectCourse'),
	url(r'^studentLanding/$', views.studentLanding, name='studentLanding'),
	url(r'^studentTodaysQuiz/$', views.studentTodaysQuiz, name='studentTodaysQuiz'),
	url(r'^help/$', views.helpPage, name='helpPage'),

	url(r'^answer/(?P<id>[a-z0-9]+)/(?P<qid>[0-9]+)/(?P<choice>[A-Z]+)/$', views.storeAnswer, name='storeAnswer'),
	url(r'^todaysQuizProcessing/$', views.todaysQuizProcessing, name = 'todaysQuizProcessing'),
	url(r'^questionRetryProcessing/$', views.questionRetryProcessing, name = 'questionRetryProcessing'),
	#url(r'^updateAllStudentMarks/$', views.updateAllStudentMarks, name='updateAllStudentMarks'),
	#url(r'^updateQuestionData/$', views.updateQuestionData, name='updateQuestionData'),
	#url(r'^updateAllRanksAndBadges/$', views.updateAllRanksAndBadges, name='updateAllRanksAndBadges'),
	url(r'^studentQuestionList/$', views.studentQuestionList, name='studentQuestionList'),
	url(r'^studentQuestionCalendar/$', views.studentQuestionCalendar, name='studentQuestionCalendar'),

	url(r'^studentQuestionView/(?P<sid>[0-9]+)/(?P<qid>[0-9]+)/(?P<topAlertFlag>[0-9]+)/(?P<backLocation>[0-9]+)$', views.studentQuestionView, name='studentQuestionView'),
	url(r'^studentQuestionRetry/(?P<sid>[0-9]+)/(?P<qid>[0-9]+)/(?P<topAlertFlag>[0-9]+)/(?P<backLocation>[0-9]+)$', views.studentQuestionRetry, name='studentQuestionRetry'),
	url(r'^saveExplanation/$', views.saveExplanation, name='saveExplanation'),
	url(r'^updateRecommendations/',views.updateRecommendations,name='updateRecommendations'),
	url(r'^weaktopics/',views.weakTopics,name='weakTopics'),
	url(r'^socialVisualization/',views.socialVisualization,name='socialVisualization'),
	url(r'^wrongpage/$', views.wrongpage, name='wrongpage'),
]