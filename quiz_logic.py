"""
Modul comun pentru logica quiz-ului
Poate fi folosit atat de aplicatia desktop (tkinter) cat si de aplicatia mobile (kivy)
"""
import re


class QuizLogic:
    """Clasă pentru gestionarea logicii quiz-ului"""
    
    def __init__(self, file_path=None):
        self.questions = []
        self.current_question_index = 0
        self.selected_answers = set()
        self.correct_answer_indices = []
        self.correct_count = 0
        self.question_answered = False
        
        if file_path:
            self.load_questions(file_path)
    
    def load_questions(self, file_path):
        """Încarcă întrebările din fișierul text"""
        self.questions = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split by double newlines or question patterns
            parts = re.split(r'\n\s*\n+', content.strip())
            
            for part in parts:
                if not part.strip():
                    continue
                
                lines = [line.strip() for line in part.split('\n') if line.strip()]
                if len(lines) < 2:
                    continue
                
                question_text = lines[0]
                answers = []
                correct_indices = []
                
                for i, line in enumerate(lines[1:], start=0):
                    if line.startswith('*'):
                        answer_text = line[1:].strip()
                        answers.append(answer_text)
                        correct_indices.append(i)
                    else:
                        answers.append(line)
                
                if len(correct_indices) > 0 and len(answers) > 0:
                    self.questions.append({
                        'question': question_text,
                        'answers': answers,
                        'correct': correct_indices
                    })
            
            return len(self.questions) > 0
        except FileNotFoundError:
            self.questions = []
            return False
        except Exception as e:
            self.questions = []
            return False
    
    def get_current_question(self):
        """Returnează întrebarea curentă"""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def toggle_answer(self, answer_index):
        """Bifează/debifează un răspuns"""
        if self.question_answered:
            return
        
        if answer_index in self.selected_answers:
            self.selected_answers.remove(answer_index)
        else:
            self.selected_answers.add(answer_index)
    
    def is_answer_selected(self, answer_index):
        """Verifică dacă un răspuns este selectat"""
        return answer_index in self.selected_answers
    
    def can_check(self):
        """Verifică dacă se poate verifica răspunsul (cel puțin un răspuns selectat)"""
        return len(self.selected_answers) > 0 and not self.question_answered
    
    def check_answer(self):
        """Verifică răspunsurile selectate și returnează rezultatul"""
        if self.question_answered:
            return None
        
        self.question_answered = True
        question = self.get_current_question()
        if not question:
            return None
        
        self.correct_answer_indices = question['correct']
        correct_set = set(self.correct_answer_indices)
        is_correct = (self.selected_answers == correct_set and len(self.selected_answers) > 0)
        
        if is_correct:
            self.correct_count += 1
        
        # Returnează rezultatul pentru fiecare buton
        result = {}
        for idx in range(len(question['answers'])):
            if idx in self.selected_answers:
                if idx in correct_set:
                    result[idx] = 'correct_selected'  # Verde
                else:
                    result[idx] = 'wrong_selected'  # Roșu
            else:
                if idx in correct_set:
                    result[idx] = 'correct_not_selected'  # Portocaliu
                else:
                    result[idx] = 'normal'  # Normal
        
        return result, is_correct
    
    def next_question(self):
        """Trece la următoarea întrebare"""
        self.current_question_index += 1
        self.selected_answers = set()
        self.question_answered = False
        question = self.get_current_question()
        if question:
            self.correct_answer_indices = question['correct']
    
    def is_completed(self):
        """Verifică dacă quiz-ul este completat"""
        return self.current_question_index >= len(self.questions)
    
    def get_stats(self):
        """Returnează statisticile"""
        total = len(self.questions)
        percentage = (self.correct_count / total * 100) if total > 0 else 0
        return {
            'correct': self.correct_count,
            'total': total,
            'percentage': percentage
        }
