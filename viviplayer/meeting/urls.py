from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.meetingList),
    path('invite/', views.meetingCreateInvite, name="invite"),
    path('<int:meetingName>/join/', views.meetingJoin),
    path('<int:meetingName>/', views.meetingIndex),
    path('<int:meetingName>/end', views.meetingEnd),
    path('<int:meetingName>/leave', views.meetingLeave)
]