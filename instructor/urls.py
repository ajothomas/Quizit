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
from instructor import views
from django.core.urlresolvers import reverse

app_name = 'instructor'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.login_view, name='login_view'),
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^authenticate/$', views.authenticate_view, name='authenticate_view'),
    url(r'^forgotPassword/$', views.forgotPassword, name='forgotPassword'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^signUp/$', views.signUp, name='signUp'),
    url(r'^verifyEmail/$', views.verifyEmail, name='verifyEmail'),
    url(r'^registrationFormProcessing/$', views.registrationFormProcessing, name='registrationFormProcessing'),
    url(r'^resetPasswordSendMail/$', views.resetPasswordSendMail, name='resetPasswordSendMail'),
    url(r'^resetPasswordForm/(?P<id>[a-z0-9]+)/$', views.resetPasswordForm, name='resetPasswordForm'),
    url(r'^resetPasswordFormProcessing/$', views.resetPasswordFormProcessing, name='resetPasswordFormProcessing'),

    url(r'^viewCourses/$', views.viewCourses, name='viewCourses'),
    url(r'^createCourse/$', views.createCourse, name='createCourse'),
    url(r'^createCourseProcessing/$', views.createCourseProcessing, name='createCourseProcessing'),
    url(r'^selectCourse/$', views.selectCourse, name='selectCourse'),
	url(r'^instructorDashboard/$', views.instructorDashboard, name='instructorDashboard'),
	url(r'^generateCourseTopicDropdown/$', views.generateCourseTopicDropdown, name='generateCourseTopicDropdown'),
    url(r'^checkNewTopic/$', views.checkNewTopic, name='checkNewTopic'),
    url(r'^questionForm/$', views.questionForm, name='questionForm'),
	url(r'^questionList/$', views.questionList, name='questionList'),
    url(r'^instructorCalendar/$', views.instructorCalendar, name='instructorCalendar'),
    
	url(r'^questionProcessing/$', views.questionProcessing, name='questionProcessing'),
	url(r'^questionUpdate/$', views.questionUpdate, name='questionUpdate'),
	url(r'^questionView/(?P<id>[0-9]+)/$', views.questionView, name='questionView'),
    url(r'^questionEdit/(?P<id>[0-9]+)/$', views.questionEdit, name='questionEdit'),
    url(r'^checkDuplicateDate/$', views.checkDuplicateDate, name='checkDuplicateDate'),
    
	url(r'^sendmail/$', views.sendMail_view, name='sendMail_view'),
    url(r'^populateRecommendation/',views.populateRecommendation,name='populateRecommendation'),
    url(r'^deleteQuiz/$',views.deleteQuiz,name='deleteQuiz'),
]