from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.signing import Signer

from .models import EventUser, Question
from .serializers import QuestionSerializer, RegistrationSerializer, EventUserSerializer
from .scoring import calculate_score

signer = Signer()

class QuestionListView(APIView):
    def get(self, request):
        questions = Question.objects.prefetch_related('options').all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            answers_dict = serializer.validated_data['answers']
            
            try:
                total_score, enriched_answers = calculate_score(answers_dict)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            # Create user
            user = EventUser.objects.create(
                name=name,
                email=email,
                answers=enriched_answers,
                score=total_score
            )
            
            # Generate QR token
            token = signer.sign(str(user.user_id))
            
            return Response({
                "message": "Registration successful",
                "user_id": user.user_id,
                "qr_token": token
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(EventUser, user_id=user_id)
        serializer = EventUserSerializer(user)
        return Response(serializer.data)
