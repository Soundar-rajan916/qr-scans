from django.core.management.base import BaseCommand
from users.models import Question, Option
from users.questions import QUESTIONS

class Command(BaseCommand):
    help = 'Seeds the questions and options for the franchise vetting questionnaire'

    def handle(self, *args, **kwargs):
        for q_data in QUESTIONS:
            question, created = Question.objects.get_or_create(
                question_id=q_data['id'],
                defaults={
                    'text': q_data['text'],
                    'question_type': q_data['type']
                }
            )
            
            if not created:
                question.text = q_data['text']
                question.question_type = q_data['type']
                question.save()

            for opt_data in q_data['options']:
                Option.objects.get_or_create(
                    question=question,
                    text=opt_data['text'],
                    defaults={'score': opt_data['score']}
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded questions and options.'))
