from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Service

# Create your views here.
class ServiceListView(ListView):
    model = Service
    template_name = "services/list.html"
    context_object_name = "services"
    paginate_by = 9  # มี pagination ด้วย

class ServiceDetailView(DetailView):
    model = Service
    template_name = "services/detail.html"
    context_object_name = "service"
