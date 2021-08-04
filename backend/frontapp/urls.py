from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("<int:page>/", TemplateView.as_view(template_name="index.html")),
    path("login/", TemplateView.as_view(template_name="index.html")),
    path("item/<int:pk>/", TemplateView.as_view(template_name="index.html")),
]
