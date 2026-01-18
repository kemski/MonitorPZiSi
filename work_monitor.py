"""
Moduł monitorowania czasu pracy przy komputerze.

Moduł śledzi czas spędzony przy komputerze, sugeruje przerwy
i przechowuje statystyki pracy.
"""

import time
from datetime import datetime, timedelta
import psutil
import json
import os


class WorkMonitor:
    """
    Klasa odpowiedzialna za monitorowanie czasu pracy przy komputerze.
    
    Funkcjonalności:
    - Śledzenie czasu pracy
    - Sugerowanie przerw
    - Przechowywanie statystyk
    """
    
    def __init__(self, break_interval_minutes=50):
        """
        Inicjalizacja monitora pracy.
        
        Args:
            break_interval_minutes: Interwał w minutach, po którym sugerowana jest przerwa (domyślnie 50)
        """
        self.break_interval = break_interval_minutes * 60  # Konwersja na sekundy
        self.session_start_time = None
        self.is_working = False
        self.total_work_time_today = 0
        self.last_break_time = None
        self.stats_file = 'work_stats.json'
        
        # Pomodoro timer
        self.pomodoro_time = 25 * 60  # 25 minut w sekundach
        self.break_time = 5 * 60  # 5 minut w sekundach
        self.timer_start_time = None
        self.timer_duration = 0  # Czas trwania timera w sekundach
        self.timer_running = False
        self.timer_paused = False
        self.timer_paused_at = 0  # Czas, w którym timer został zatrzymany
        self.timer_elapsed = 0  # Czas, który już upłynął przed pauzą
        self.timer_type = None  # 'pomodoro' lub 'break'
        
        # Załadowanie statystyk z poprzednich sesji
        self.load_stats()
    
    def start_session(self):
        """
        Rozpoczęcie sesji pracy.
        Zapisuje czas rozpoczęcia i oznacza sesję jako aktywną.
        """
        self.session_start_time = time.time()
        self.is_working = True
        self.last_break_time = None
        print(f"Sesja pracy rozpoczęta o {datetime.now().strftime('%H:%M:%S')}")
    
    def stop_session(self):
        """
        Zakończenie sesji pracy.
        Zapisuje czas pracy i aktualizuje statystyki.
        """
        if self.is_working and self.session_start_time:
            session_duration = time.time() - self.session_start_time
            self.total_work_time_today += session_duration
            self.save_stats()
            print(f"Sesja pracy zakończona. Czas pracy: {self.format_time(session_duration)}")
        
        self.is_working = False
        self.session_start_time = None
    
    def get_current_work_time(self):
        """
        Pobiera aktualny czas pracy w bieżącej sesji.
        
        Returns:
            int: Czas pracy w sekundach
        """
        if not self.is_working or not self.session_start_time:
            return 0
        
        current_session_time = time.time() - self.session_start_time
        return int(current_session_time + self.total_work_time_today)
    
    def should_take_break(self):
        """
        Sprawdza, czy powinna być sugerowana przerwa.
        
        Returns:
            bool: True jeśli czas na przerwę
        """
        if not self.is_working or not self.session_start_time:
            return False
        
        current_session_time = time.time() - self.session_start_time
        
        # Sprawdź, czy minął interwał od ostatniej przerwy lub rozpoczęcia sesji
        if self.last_break_time:
            time_since_break = time.time() - self.last_break_time
            return time_since_break >= self.break_interval
        else:
            return current_session_time >= self.break_interval
    
    def record_break(self):
        """
        Rejestruje wykonanie przerwy.
        Resetuje timer do następnej sugestii przerwy.
        """
        self.last_break_time = time.time()
        print(f"Przerwa zarejestrowana o {datetime.now().strftime('%H:%M:%S')}")
    
    def get_daily_stats(self):
        """
        Pobiera statystyki dzienne pracy.
        
        Returns:
            dict: Słownik ze statystykami (czas pracy, liczba przerw, itp.)
        """
        current_time = self.get_current_work_time()
        
        return {
            'total_work_time_seconds': current_time,
            'total_work_time_formatted': self.format_time(current_time),
            'is_working': self.is_working,
            'break_suggested': self.should_take_break(),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def format_time(self, seconds):
        """
        Formatuje czas w sekundach na czytelny format.
        
        Args:
            seconds: Czas w sekundach
            
        Returns:
            str: Sformatowany czas (HH:MM:SS)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def save_stats(self):
        """
        Zapisuje statystyki do pliku JSON.
        """
        stats = {
            'total_work_time_today': self.total_work_time_today,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"Błąd podczas zapisywania statystyk: {e}")
    
    def load_stats(self):
        """
        Ładuje statystyki z pliku JSON.
        """
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
                    # Sprawdź, czy statystyki są z dzisiaj
                    last_updated = datetime.fromisoformat(stats.get('last_updated', '2000-01-01'))
                    if last_updated.date() == datetime.now().date():
                        self.total_work_time_today = stats.get('total_work_time_today', 0)
                    else:
                        # Nowy dzień - reset statystyk
                        self.total_work_time_today = 0
            except Exception as e:
                print(f"Błąd podczas ładowania statystyk: {e}")
                self.total_work_time_today = 0
        else:
            self.total_work_time_today = 0
    
    def is_computer_active(self):
        """
        Sprawdza, czy komputer jest aktywny (użytkownik pracuje).
        Używa prostego heurystyki: sprawdza aktywność procesora.
        
        Returns:
            bool: True jeśli komputer wydaje się aktywny
        """
        # Prosty heurystyka: jeśli CPU jest używany powyżej 5%, uznajemy za aktywność
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return cpu_percent > 5.0
    
    def start_pomodoro(self):
        """
        Rozpoczyna timer Pomodoro (25 minut).
        """
        self.timer_duration = self.pomodoro_time
        self.timer_start_time = time.time()
        self.timer_running = True
        self.timer_paused = False
        self.timer_elapsed = 0
        self.timer_paused_at = 0
        self.timer_type = 'pomodoro'
    
    def start_break(self):
        """
        Rozpoczyna timer przerwy (5 minut).
        """
        self.timer_duration = self.break_time
        self.timer_start_time = time.time()
        self.timer_running = True
        self.timer_paused = False
        self.timer_elapsed = 0
        self.timer_paused_at = 0
        self.timer_type = 'break'
    
    def pause_timer(self):
        """
        Pauzuje timer.
        """
        if self.timer_running and not self.timer_paused:
            self.timer_paused_at = time.time()
            self.timer_elapsed += self.timer_paused_at - self.timer_start_time
            self.timer_paused = True
    
    def resume_timer(self):
        """
        Wznawia timer.
        """
        if self.timer_paused:
            self.timer_start_time = time.time()
            self.timer_paused = False
    
    def stop_timer(self):
        """
        Zatrzymuje timer.
        """
        self.timer_running = False
        self.timer_paused = False
        self.timer_start_time = None
        self.timer_elapsed = 0
        self.timer_paused_at = 0
        self.timer_type = None
    
    def get_timer_remaining(self):
        """
        Pobiera pozostały czas timera w sekundach.
        
        Returns:
            int: Pozostały czas w sekundach (0 jeśli timer się skończył)
        """
        if not self.timer_running:
            return 0
        
        if self.timer_paused:
            remaining = self.timer_duration - self.timer_elapsed
        else:
            elapsed = self.timer_elapsed + (time.time() - self.timer_start_time)
            remaining = self.timer_duration - elapsed
        
        return max(0, int(remaining))
    
    def format_timer_time(self, seconds):
        """
        Formatuje czas timera na format MM:SS.
        
        Args:
            seconds: Czas w sekundach
            
        Returns:
            str: Sformatowany czas (MM:SS)
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

