"""
Moduł zarządzania ćwiczeniami fizycznymi podczas przerw.

Moduł zawiera bazę ćwiczeń dostosowanych do wykonywania
podczas przerw w pracy przy komputerze.
"""


class ExerciseManager:
    """
    Klasa zarządzająca ćwiczeniami fizycznymi.
    
    Funkcjonalności:
    - Przechowywanie bazy ćwiczeń
    - Zwracanie ćwiczeń dostosowanych do przerw
    - Instrukcje wykonania ćwiczeń
    """
    
    def __init__(self):
        """
        Inicjalizacja managera ćwiczeń.
        Ładuje bazę ćwiczeń.
        """
        self.exercises = self._load_exercises()
    
    def _load_exercises(self):
        """
        Ładuje bazę ćwiczeń fizycznych.
        
        Returns:
            list: Lista ćwiczeń z instrukcjami
        """
        return [
            {
                'id': 1,
                'name': 'Rozciąganie szyi',
                'duration': '2-3 minuty',
                'difficulty': 'łatwe',
                'category': 'Szyja i kark',
                'description': 'Ćwiczenia rozciągające mięśnie szyi i karku, które często są napięte podczas pracy przy komputerze.',
                'instructions': [
                    'Usiądź prosto na krześle',
                    'Powoli przechyl głowę w prawo, trzymając przez 15-20 sekund',
                    'Wróć do pozycji neutralnej',
                    'Powtórz w lewą stronę',
                    'Wykonaj 3-5 powtórzeń w każdą stronę',
                    'Możesz również wykonać delikatne ruchy głową w kółko'
                ],
                'benefits': [
                    'Zmniejsza napięcie mięśni szyi',
                    'Poprawia elastyczność',
                    'Zapobiega bólom głowy'
                ],
                'image': 'neck_stretch.jpg'  # W rzeczywistej aplikacji można dodać obrazy
            },
            {
                'id': 2,
                'name': 'Rozciąganie ramion i barków',
                'duration': '3-4 minuty',
                'difficulty': 'łatwe',
                'category': 'Ramiona',
                'description': 'Ćwiczenia rozluźniające ramiona i barki, które często są napięte podczas pisania.',
                'instructions': [
                    'Stań lub usiądź prosto',
                    'Unieś prawe ramię i zegnij łokieć, sięgając dłonią za głowę',
                    'Lewą ręką delikatnie pociągnij prawy łokieć w dół',
                    'Trzymaj przez 20-30 sekund',
                    'Powtórz z drugim ramieniem',
                    'Wykonaj 3 powtórzenia na każde ramię'
                ],
                'benefits': [
                    'Rozluźnia mięśnie ramion',
                    'Poprawia zakres ruchu',
                    'Zapobiega sztywności barków'
                ],
                'image': 'shoulder_stretch.jpg'
            },
            {
                'id': 3,
                'name': 'Skręty tułowia',
                'duration': '2-3 minuty',
                'difficulty': 'łatwe',
                'category': 'Plecy',
                'description': 'Ćwiczenia rozciągające mięśnie pleców i poprawiające mobilność kręgosłupa.',
                'instructions': [
                    'Usiądź prosto na krześle',
                    'Skrzyżuj ręce na klatce piersiowej',
                    'Powoli skręć tułów w prawo, trzymając przez 15-20 sekund',
                    'Wróć do pozycji neutralnej',
                    'Powtórz w lewą stronę',
                    'Wykonaj 5-8 powtórzeń w każdą stronę'
                ],
                'benefits': [
                    'Rozciąga mięśnie pleców',
                    'Poprawia mobilność kręgosłupa',
                    'Zmniejsza sztywność'
                ],
                'image': 'torso_twist.jpg'
            },
            {
                'id': 4,
                'name': 'Rozciąganie nadgarstków',
                'duration': '2 minuty',
                'difficulty': 'łatwe',
                'category': 'Nadgarstki',
                'description': 'Ćwiczenia zapobiegające zespołowi cieśni nadgarstka i bólom rąk.',
                'instructions': [
                    'Wyciągnij prawą rękę przed siebie, dłonią do góry',
                    'Lewą ręką delikatnie pociągnij palce prawej dłoni w dół',
                    'Trzymaj przez 15-20 sekund',
                    'Powtórz z dłonią skierowaną w dół',
                    'Wykonaj 3 powtórzenia na każdą rękę',
                    'Możesz również wykonać delikatne ruchy nadgarstkami w kółko'
                ],
                'benefits': [
                    'Zapobiega zespołowi cieśni nadgarstka',
                    'Rozluźnia mięśnie przedramion',
                    'Poprawia krążenie krwi'
                ],
                'image': 'wrist_stretch.jpg'
            },
            {
                'id': 5,
                'name': 'Mini spacer',
                'duration': '5 minut',
                'difficulty': 'łatwe',
                'category': 'Ogólne',
                'description': 'Krótki spacer, który pobudza krążenie i rozluźnia mięśnie nóg.',
                'instructions': [
                    'Wstań z krzesła',
                    'Przejdź się po biurze lub pokoju',
                    'Możesz wyjść na krótki spacer na zewnątrz',
                    'Staraj się chodzić przez co najmniej 3-5 minut',
                    'Podczas chodzenia wykonuj głębokie wdechy'
                ],
                'benefits': [
                    'Pobudza krążenie krwi',
                    'Rozluźnia mięśnie nóg',
                    'Poprawia koncentrację',
                    'Zwiększa poziom energii'
                ],
                'image': 'walk.jpg'
            },
            {
                'id': 6,
                'name': 'Ćwiczenia oczu',
                'duration': '2 minuty',
                'difficulty': 'łatwe',
                'category': 'Oczy',
                'description': 'Ćwiczenia zmniejszające zmęczenie oczu spowodowane długotrwałą pracą przy komputerze.',
                'instructions': [
                    'Zamknij oczy na 10 sekund',
                    'Otwórz oczy i spójrz w dal przez 20 sekund',
                    'Wykonaj ruchy oczami w kółko (5 razy w prawo, 5 razy w lewo)',
                    'Mrugaj intensywnie przez 10 sekund',
                    'Zamknij oczy i delikatnie masuj powieki opuszkami palców',
                    'Powtórz całą sekwencję 2-3 razy'
                ],
                'benefits': [
                    'Zmniejsza zmęczenie oczu',
                    'Zapobiega suchości oczu',
                    'Poprawia ostrość widzenia',
                    'Redukuje bóle głowy związane z oczami'
                ],
                'image': 'eye_exercises.jpg'
            },
            {
                'id': 7,
                'name': 'Rozciąganie nóg',
                'duration': '3 minuty',
                'difficulty': 'łatwe',
                'category': 'Nogi',
                'description': 'Ćwiczenia rozciągające mięśnie nóg, które mogą być sztywne po długim siedzeniu.',
                'instructions': [
                    'Stań przy krześle lub biurku dla podparcia',
                    'Zegnij prawe kolano i chwyć stopę ręką',
                    'Delikatnie pociągnij stopę w kierunku pośladków',
                    'Trzymaj przez 20-30 sekund',
                    'Powtórz z drugą nogą',
                    'Wykonaj 3 powtórzenia na każdą nogę'
                ],
                'benefits': [
                    'Rozciąga mięśnie ud',
                    'Poprawia krążenie w nogach',
                    'Zapobiega sztywności'
                ],
                'image': 'leg_stretch.jpg'
            },
            {
                'id': 8,
                'name': 'Głębokie oddychanie',
                'duration': '3-5 minut',
                'difficulty': 'łatwe',
                'category': 'Relaksacja',
                'description': 'Ćwiczenia oddechowe redukujące stres i poprawiające koncentrację.',
                'instructions': [
                    'Usiądź wygodnie z wyprostowanymi plecami',
                    'Zamknij oczy',
                    'Weź głęboki wdech przez nos (licząc do 4)',
                    'Wstrzymaj oddech (licząc do 4)',
                    'Wydychaj powoli przez usta (licząc do 6)',
                    'Powtórz cykl 10-15 razy',
                    'Skup się tylko na oddechu'
                ],
                'benefits': [
                    'Redukuje stres',
                    'Poprawia koncentrację',
                    'Obniża ciśnienie krwi',
                    'Zwiększa poziom energii'
                ],
                'image': 'breathing.jpg'
            }
        ]
    
    def get_exercises(self):
        """
        Zwraca listę wszystkich dostępnych ćwiczeń.
        
        Returns:
            list: Lista wszystkich ćwiczeń
        """
        return self.exercises
    
    def get_exercise(self, exercise_id):
        """
        Zwraca szczegóły konkretnego ćwiczenia.
        
        Args:
            exercise_id: ID ćwiczenia
            
        Returns:
            dict: Szczegóły ćwiczenia lub None, jeśli nie znaleziono
        """
        for exercise in self.exercises:
            if exercise['id'] == exercise_id:
                return exercise
        return None
    
    def get_exercises_by_category(self, category):
        """
        Zwraca ćwiczenia z określonej kategorii.
        
        Args:
            category: Kategoria ćwiczeń
            
        Returns:
            list: Lista ćwiczeń z danej kategorii
        """
        return [ex for ex in self.exercises if ex['category'] == category]
    
    def get_quick_exercises(self, max_duration_minutes=5):
        """
        Zwraca ćwiczenia, które można wykonać w krótkim czasie.
        
        Args:
            max_duration_minutes: Maksymalny czas trwania ćwiczenia w minutach
            
        Returns:
            list: Lista krótkich ćwiczeń
        """
        quick_exercises = []
        for exercise in self.exercises:
            # Parsowanie czasu trwania (np. "2-3 minuty" -> 3)
            duration_str = exercise['duration']
            try:
                max_duration = int(duration_str.split('-')[-1].split()[0])
                if max_duration <= max_duration_minutes:
                    quick_exercises.append(exercise)
            except:
                # Jeśli nie można sparsować, dodaj ćwiczenie
                quick_exercises.append(exercise)
        
        return quick_exercises

