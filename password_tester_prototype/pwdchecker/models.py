from django.db import models

# This file defines the database models for the `pwdchecker` app.
# Models represent the structure of the database tables.

class DisallowedWord(models.Model):
    # Represents a word or phrase that is disallowed in passwords.
    word = models.CharField(max_length=128, unique=True)  # The disallowed word (must be unique).
    added_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the word was added.

    def __str__(self):
        # Returns the word as its string representation.
        return self.word
