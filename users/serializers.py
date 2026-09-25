from rest_framework import serializers
from .models import EventUser, Question, Option

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['text'] # We shouldn't expose scores to the frontend, although it's fine for now, prompt said backend handles it.

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['question_id', 'text', 'question_type', 'options']

class RegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    answers = serializers.DictField(child=serializers.CharField())

class EventUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventUser
        fields = ['user_id', 'name', 'email', 'score', 'answers', 'created_at']
