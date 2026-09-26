import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from users.models import Question, Option
from users.questions import QUESTIONS

def import_data():
    if Question.objects.exists():
        print("Questions already exist. Skipping import.")
        return

    print("Importing questions...")
    for q_data in QUESTIONS:
        question = Question.objects.create(
            question_id=q_data['id'],
            text=q_data['text'],
            question_type=q_data['type']
        )
        for opt_data in q_data['options']:
            Option.objects.create(
                question=question,
                text=opt_data['text'],
                score=opt_data['score']
            )
    print("Questions imported successfully!")

if __name__ == '__main__':
    import_data()
