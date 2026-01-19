"""
Aplicatie mobila Kivy pentru quiz
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.metrics import dp
import os
from quiz_logic import QuizLogic


class FileSelectScreen(Screen):
    """Ecran pentru selectarea fișierului"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Titlu
        title = Label(
            text='Selecteaza fisierul cu intrebari',
            size_hint_y=None,
            height=dp(60),
            font_size=dp(24),
            bold=True
        )
        self.layout.add_widget(title)
        
        # Container pentru file chooser
        file_container = BoxLayout(orientation='vertical', size_hint_y=0.7)
        
        # File chooser
        self.filechooser = FileChooserListView(
            path=os.getcwd(),
            filters=['*.txt']
        )
        file_container.add_widget(self.filechooser)
        self.layout.add_widget(file_container)
        
        # Buton de selectare
        btn_container = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        select_btn = Button(
            text='Selecteaza fisierul',
            size_hint_x=0.5,
            font_size=dp(18),
            background_color=(0.2, 0.6, 0.9, 1)
        )
        select_btn.bind(on_press=self.select_file)
        btn_container.add_widget(select_btn)
        
        cancel_btn = Button(
            text='Anuleaza',
            size_hint_x=0.5,
            font_size=dp(18),
            background_color=(0.7, 0.7, 0.7, 1)
        )
        cancel_btn.bind(on_press=self.cancel)
        btn_container.add_widget(cancel_btn)
        
        self.layout.add_widget(btn_container)
        self.add_widget(self.layout)
    
    def select_file(self, instance):
        """Selectează fișierul ales"""
        if self.filechooser.selection:
            file_path = self.filechooser.selection[0]
            if os.path.isfile(file_path) and file_path.endswith('.txt'):
                # Încarcă întrebările
                app = App.get_running_app()
                app.quiz_logic = QuizLogic()
                success = app.quiz_logic.load_questions(file_path)
                
                if success and len(app.quiz_logic.questions) > 0:
                    # Trece la ecranul de quiz
                    app.sm.current = 'quiz'
                    app.quiz_screen.start_quiz()
                else:
                    self.show_error("Nu s-au gasit intrebari in fisier sau fisierul nu este valid!")
            else:
                self.show_error("Te rog selecteaza un fisier .txt valid!")
        else:
            self.show_error("Te rog selecteaza un fisier!")
    
    def cancel(self, instance):
        """Anulează și închide aplicația"""
        App.get_running_app().stop()
    
    def show_error(self, message):
        """Afișează un mesaj de eroare"""
        popup = Popup(
            title='Eroare',
            content=Label(text=message, text_size=(dp(300), None)),
            size_hint=(0.8, 0.4)
        )
        popup.open()


class QuizScreen(Screen):
    """Ecran principal pentru quiz"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.answer_buttons = []
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header cu contor
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.counter_label = Label(
            text='',
            size_hint_x=0.7,
            font_size=dp(16),
            halign='left',
            text_size=(None, None)
        )
        header.add_widget(self.counter_label)
        self.main_layout.add_widget(header)
        
        # Întrebarea
        self.question_label = Label(
            text='',
            size_hint_y=None,
            height=dp(100),
            font_size=dp(18),
            bold=True,
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        self.question_label.bind(texture_size=self.question_label.setter('size'))
        self.main_layout.add_widget(self.question_label)
        
        # ScrollView pentru răspunsuri
        scroll = ScrollView()
        self.answers_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(10),
            padding=dp(5)
        )
        self.answers_layout.bind(minimum_height=self.answers_layout.setter('height'))
        scroll.add_widget(self.answers_layout)
        self.main_layout.add_widget(scroll)
        
        # Butoane de acțiune
        btn_container = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        self.check_btn = Button(
            text='Verifica raspuns',
            size_hint_x=0.5,
            font_size=dp(16),
            background_color=(0.13, 0.59, 0.95, 1),
            disabled=True
        )
        self.check_btn.bind(on_press=self.check_answer)
        btn_container.add_widget(self.check_btn)
        
        self.next_btn = Button(
            text='Urmatoarea',
            size_hint_x=0.5,
            font_size=dp(16),
            background_color=(0.3, 0.69, 0.31, 1),
            disabled=True
        )
        self.next_btn.bind(on_press=self.next_question)
        btn_container.add_widget(self.next_btn)
        
        self.main_layout.add_widget(btn_container)
        self.add_widget(self.main_layout)
    
    def start_quiz(self):
        """Începe quiz-ul"""
        self.display_question()
    
    def display_question(self):
        """Afișează întrebarea curentă"""
        app = App.get_running_app()
        quiz = app.quiz_logic
        
        if quiz.is_completed():
            app.sm.current = 'completion'
            app.completion_screen.show_stats()
            return
        
        question = quiz.get_current_question()
        if not question:
            return
        
        # Actualizează contorul
        self.counter_label.text = f"Intrebare {quiz.current_question_index + 1} din {len(quiz.questions)}"
        
        # Actualizează întrebarea
        self.question_label.text = question['question']
        
        # Șterge butoanele vechi
        self.answers_layout.clear_widgets()
        self.answer_buttons = []
        
        # Creează butoanele pentru răspunsuri
        for i, answer in enumerate(question['answers']):
            btn = Button(
                text=answer,
                size_hint_y=None,
                height=dp(70),
                font_size=dp(14),
                text_size=(None, None),
                halign='left',
                valign='center',
                background_color=(0.88, 0.88, 0.88, 1),
                color=(0.2, 0.2, 0.2, 1)
            )
            btn.bind(on_press=lambda instance, idx=i: self.select_answer(idx))
            btn.bind(texture_size=btn.setter('text_size'))
            self.answers_layout.add_widget(btn)
            self.answer_buttons.append(btn)
        
        # Resetează butoanele
        self.check_btn.disabled = True
        self.next_btn.disabled = True
    
    def select_answer(self, answer_index):
        """Selectează/deselectează un răspuns"""
        app = App.get_running_app()
        quiz = app.quiz_logic
        
        quiz.toggle_answer(answer_index)
        
        # Actualizează culoarea butonului
        btn = self.answer_buttons[answer_index]
        if quiz.is_answer_selected(answer_index):
            btn.background_color = (0.73, 0.87, 0.98, 1)  # Albastru deschis
        else:
            btn.background_color = (0.88, 0.88, 0.88, 1)  # Gri
        
        # Activează butonul de verificare
        self.check_btn.disabled = not quiz.can_check()
    
    def check_answer(self, instance):
        """Verifică răspunsurile"""
        app = App.get_running_app()
        quiz = app.quiz_logic
        
        result, is_correct = quiz.check_answer()
        
        if result is None:
            return
        
        # Colorează butoanele
        for idx, status in result.items():
            btn = self.answer_buttons[idx]
            btn.disabled = True
            
            if status == 'correct_selected':
                btn.background_color = (0.3, 0.69, 0.31, 1)  # Verde
                btn.color = (1, 1, 1, 1)
            elif status == 'wrong_selected':
                btn.background_color = (0.96, 0.26, 0.21, 1)  # Roșu
                btn.color = (1, 1, 1, 1)
            elif status == 'correct_not_selected':
                btn.background_color = (1, 0.6, 0, 1)  # Portocaliu
                btn.color = (1, 1, 1, 1)
        
        # Activează butonul următoare
        self.check_btn.disabled = True
        self.next_btn.disabled = False
    
    def next_question(self, instance):
        """Trece la următoarea întrebare"""
        app = App.get_running_app()
        app.quiz_logic.next_question()
        self.display_question()


class CompletionScreen(Screen):
    """Ecran de finalizare cu statistici"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(30))
        
        self.title_label = Label(
            text='Felicitari!',
            font_size=dp(28),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        self.layout.add_widget(self.title_label)
        
        self.subtitle_label = Label(
            text='Ai terminat toate intrebarile!',
            font_size=dp(22),
            size_hint_y=None,
            height=dp(50)
        )
        self.layout.add_widget(self.subtitle_label)
        
        self.stats_container = BoxLayout(orientation='vertical', spacing=dp(20))
        self.layout.add_widget(self.stats_container)
        
        # Buton pentru restart
        self.restart_btn = Button(
            text='Incepe din nou',
            size_hint_y=None,
            height=dp(60),
            font_size=dp(18),
            background_color=(0.3, 0.69, 0.31, 1)
        )
        self.restart_btn.bind(on_press=self.restart)
        self.layout.add_widget(self.restart_btn)
        
        self.add_widget(self.layout)
    
    def show_stats(self):
        """Afișează statisticile"""
        app = App.get_running_app()
        stats = app.quiz_logic.get_stats()
        
        # Șterge statisticile vechi
        self.stats_container.clear_widgets()
        
        # Adaugă statisticile noi
        score_label = Label(
            text=f'Raspunsuri corecte: {stats["correct"]} din {stats["total"]}',
            font_size=dp(22),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.stats_container.add_widget(score_label)
        
        percentage_label = Label(
            text=f'Procentaj: {stats["percentage"]:.1f}%',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40)
        )
        self.stats_container.add_widget(percentage_label)
    
    def restart(self, instance):
        """Reîncepe quiz-ul"""
        app = App.get_running_app()
        app.sm.current = 'file_select'


class QuizApp(App):
    """Aplicația principală"""
    
    def build(self):
        self.quiz_logic = None
        self.sm = ScreenManager()
        
        # Adaugă ecranele
        self.file_select_screen = FileSelectScreen(name='file_select')
        self.quiz_screen = QuizScreen(name='quiz')
        self.completion_screen = CompletionScreen(name='completion')
        
        self.sm.add_widget(self.file_select_screen)
        self.sm.add_widget(self.quiz_screen)
        self.sm.add_widget(self.completion_screen)
        
        return self.sm


if __name__ == '__main__':
    QuizApp().run()
