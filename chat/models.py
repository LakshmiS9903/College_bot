from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField()  # Duration in years
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price in lakhs
    prerequisites = models.TextField()
    instructors = models.JSONField()  # List of instructors
    modules = models.JSONField()  # List of modules
    pdf_url = models.FileField(upload_to='syllabi/', null=True, blank=True)  # Path to PDF

    def __str__(self):
        return self.title

class ChatHistory(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question} - A: {self.answer}"