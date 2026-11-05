from django.db import models

class Agent(models.Model):
    # General card data
    zillow_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, default="")
    brokerage = models.CharField(max_length=255, blank=True, default="")
    profile_url = models.URLField(max_length=1000, unique=True)
    rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    reviews = models.PositiveIntegerField(null=True, blank=True)
    top_agent = models.BooleanField(default=False)
    team = models.BooleanField(default=False)
    sales_12m = models.PositiveIntegerField(default=0)

    # Extended profile data
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    broker_phone = models.CharField(max_length=64, blank=True, null=True)
    business_phone = models.CharField(max_length=64, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=64, blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.URLField(max_length=1000, blank=True, null=True)
    screen_name = models.CharField(max_length=255, blank=True, null=True)
    experience_years = models.CharField(max_length=64, blank=True, null=True)

    # All property transactions stay in this same table row.
    sales_history = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "agents"
        ordering = ["name"]

    def __str__(self):
        return self.name or self.profile_url
