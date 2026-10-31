from django.contrib import admin
from .models import Activity, Event, Participant, ScoreEntry

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "join_code", "host", "is_active", "is_finished")
    search_fields = ("title", "join_code")

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "created_at")

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("nickname", "user", "created_at")
    search_fields = ("nickname", "user__username")

@admin.register(ScoreEntry)
class ScoreEntryAdmin(admin.ModelAdmin):
    list_display = ("participant", "activity", "points", "awarded_by", "awarded_at")
