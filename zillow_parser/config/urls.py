from django.contrib import admin
from django.urls import path
from zillow_agents_parser_app import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("admin/", admin.site.urls),
]

