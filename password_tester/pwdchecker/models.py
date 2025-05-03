from django.db import models

# Create your models here.

class DisallowedWord(models.Model):
    word = models.CharField(max_length=128, unique=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.word
