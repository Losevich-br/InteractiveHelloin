from django.contrib import admin
from django.urls import path
from game import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("join/", views.join_event, name="join"),
    path("stats/", views.participant_stats, name="stats"),
    path("profile/nickname/", views.change_nickname, name="change_nickname"),
    path("host/", views.host_dashboard, name="host"),
    path("host/create-event/", views.create_event, name="create_event"),
    path("host/event/<int:event_id>/", views.event_detail, name="event_detail"),
    path("host/event/<int:event_id>/activity/", views.create_activity, name="create_activity"),
    path("host/activity/<int:activity_id>/award/", views.award_points, name="award_points"),
    path("host/event/<int:event_id>/finish/", views.finish_event, name="finish_event"),
]
