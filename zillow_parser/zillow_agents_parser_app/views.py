from django.http import HttpResponse, JsonResponse
from .models import Agent


def home(request):
    return HttpResponse("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Zillow Agents Parser</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 80px auto;
                    padding: 20px;
                    background: #f5f7fa;
                    color: #263238;
                }
                .panel {
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 2px 12px #0001;
                }
                a { color: #1769aa; }
            </style>
        </head>
        <body>
            <div class="panel">
                <h1>Zillow Agents Parser</h1>
                <p>Your Django application is running successfully.</p>
                <p><a href="/admin/">Open Django Administration</a></p>
                <p><a href="/health/">Check application health</a></p>
            </div>
        </body>
        </html>
    """, content_type="text/html")


def health(request):
    return JsonResponse({
        "status": "ok",
        "agents_count": Agent.objects.count()
    })