"""account URL Configuration

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
"""account URL Configuration

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
from account import views
from django.core.urlresolvers import reverse

app_name = 'account'

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.login_view, name='login_view' ),
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^forgotPassword/$', views.forgotPassword, name='forgotPassword'),
    url(r'^resetPasswordSendMail/$', views.resetPasswordSendMail, name='resetPasswordSendMail'),
    url(r'^resetPasswordForm/(?P<id>[a-z0-9]+)/$', views.resetPasswordForm, name='resetPasswordForm'),
    url(r'^resetPasswordFormProcessing/$', views.resetPasswordFormProcessing, name='resetPasswordFormProcessing'),
    url(r'^signUp/$', views.signUp, name='signUp'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^verifyUsername/$', views.verifyUsername, name='verifyUsername'),
    url(r'^verifyEmail/$', views.verifyEmail, name='verifyEmail'),
    url(r'^generateCourseDropdown/$', views.generateCourseDropdown, name = 'generateCourseDropdown'),
    url(r'^registrationFormProcessing/$', views.registrationFormProcessing, name='registrationFormProcessing'),
    url(r'^notAllowed/$', views.notAllowed, name='notAllowed'),
    url(r'^authenticate/$', views.authenticate_view, name='authenticate_view'),
    url(r'^help/$', views.helpPage, name='helpPage'),
]

