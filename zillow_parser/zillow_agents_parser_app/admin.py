from django.contrib import admin
from .models import Agent

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("name", "brokerage", "city", "state", "rating", "reviews", "sales_12m", "updated_at")
    search_fields = ("name", "profile_url", "brokerage", "city", "state", "zipcode")
    list_filter = ("top_agent", "team", "state")
    readonly_fields = ("created_at", "updated_at")
