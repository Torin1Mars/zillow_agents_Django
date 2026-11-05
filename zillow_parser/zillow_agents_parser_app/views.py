from django.http import JsonResponse
from .models import Agent

def health(request):
    return JsonResponse({"status": "ok", "agents_count": Agent.objects.count()})
