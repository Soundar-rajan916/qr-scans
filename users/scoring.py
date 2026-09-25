from .models import Question

def calculate_score(answers_dict):
    """
    answers_dict: {"q1": "Yes", "q2": "$50k–100k"}
    Returns a tuple (total_score, enriched_answers)
    enriched_answers will be stored in EventUser.answers
    """
    total_score = 0
    enriched_answers = {}
    
    questions = {q.question_id: q for q in Question.objects.prefetch_related('options')}
    
    for q_id, answer_text in answers_dict.items():
        if q_id not in questions:
            raise ValueError(f"Invalid question ID: {q_id}")
            
        question = questions[q_id]
        options = {opt.text: opt for opt in question.options.all()}
        
        if answer_text not in options:
            raise ValueError(f"Invalid answer '{answer_text}' for question '{q_id}'")
            
        option = options[answer_text]
        
        total_score += option.score
        
        enriched_answers[q_id] = {
            "question": question.text,
            "answer": option.text,
            "score": option.score
        }
        
    return total_score, enriched_answers
