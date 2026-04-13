from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('save-login/', views.save_login, name='save_login'),
]
