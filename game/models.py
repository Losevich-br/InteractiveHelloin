import secrets
import string
from django.conf import settings
from django.db import models

def make_join_code():
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

class Participant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participant")
    nickname = models.CharField("Никнейм", max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.nickname

class Event(models.Model):
    title = models.CharField("Название", max_length=120)
    join_code = models.CharField("Код подключения", max_length=6, unique=True, default=make_join_code)
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_events")
    participants = models.ManyToManyField(Participant, blank=True, related_name="events")
    is_active = models.BooleanField("Приём участников открыт", default=True)
    is_finished = models.BooleanField("Завершено", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Activity(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="activities")
    title = models.CharField("Название интерактива", max_length=120)
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["created_at"]
    def __str__(self): return self.title

class ScoreEntry(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="scores")
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="score_entries")
    points = models.PositiveIntegerField("Очки")
    awarded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="awarded_scores")
    awarded_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-awarded_at"]
