from django.urls import path
from Users import views as register_views
from . import views
urlpatterns = [
    path('register', register_views.RegisterView.as_view()),
]