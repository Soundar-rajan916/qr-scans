from django.contrib import admin
from .models import EventUser, Question, Option

@admin.register(EventUser)
class EventUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'score', 'created_at', 'user_id')
    search_fields = ('name', 'email', 'user_id')
    readonly_fields = ('user_id', 'score', 'answers', 'created_at')

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'text', 'question_type')
    inlines = [OptionInline]
