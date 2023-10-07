from django.urls import path
from . import views

urlpatterns=[
    path('',views.LoginPage,name='login'),
    path('logout/',views.LogoutPage,name='logout'),
    path('signup/',views.SignupPage,name='signup'),
    path('News24/',views.index,name='index'),
    path('News24/<int:id>',views.index,name='index'),
]