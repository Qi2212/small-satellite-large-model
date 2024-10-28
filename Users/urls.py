from django.urls import path
from Users import views

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('login', views.LoginView.as_view()),
    path('logout',views.Logoutview.as_view())
]