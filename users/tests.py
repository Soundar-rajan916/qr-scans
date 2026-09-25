from django.test import TestCase
from django.urls import reverse
from .models import EventUser, Question, Option
from .scoring import calculate_score

class UserRegistrationTest(TestCase):
    def setUp(self):
        q1 = Question.objects.create(question_id="q1", text="Exp?", question_type="single")
        Option.objects.create(question=q1, text="Yes", score=5)
        Option.objects.create(question=q1, text="No", score=0)
        
        q2 = Question.objects.create(question_id="q2", text="Cap?", question_type="single")
        Option.objects.create(question=q2, text="$50k", score=10)

    def test_calculate_score(self):
        answers = {"q1": "Yes", "q2": "$50k"}
        total, enriched = calculate_score(answers)
        self.assertEqual(total, 15)
        self.assertEqual(enriched["q1"]["score"], 5)

    def test_registration_api(self):
        data = {
            "name": "John",
            "email": "john@test.com",
            "answers": {
                "q1": "No",
                "q2": "$50k"
            }
        }
        res = self.client.post(reverse('register'), data, content_type="application/json")
        self.assertEqual(res.status_code, 201)
        self.assertTrue('qr_token' in res.data)
        
        user = EventUser.objects.get(email="john@test.com")
        self.assertEqual(user.score, 10)
