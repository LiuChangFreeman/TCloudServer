from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from Main import views
from Main import filemanager
from Main import permission
from NasServer import settings
urlpatterns = [
    url(r'^$', views.index),
    url(r'index', views.index),
    url(r'manage', views.manage),
    url(r'permission', permission.permission),
    url(r'login', views.login),
    url(r'logout', views.logout),
    url(r'register', views.register),
    url(r'delete', views.logoff),
    url(r'changepassword', views.changepassword),
    url(r'root', views.rootchangepassword),
    url(r'main', views.main),
    url(r'upload$', filemanager.upload),
    url(r'uploadfolder', filemanager.uploadfolder),
    url(r'download', filemanager.download),
    url(r'multiple', filemanager.multiple),
]
