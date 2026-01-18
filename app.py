"""
Główna aplikacja Flask do monitorowania równowagi między życiem zawodowym a prywatnym.

Aplikacja pomaga informatykom:
- Monitorować czas pracy przy komputerze
- Przypominać o przerwach
- Proponować ćwiczenia fizyczne
- Weryfikować postawę siedzącą
- Otrzymywać sugestie ergonomiczne

Autor: Projekt edukacyjny
Data: 2024
"""

from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime, timedelta
from work_monitor import WorkMonitor
from posture_analyzer import PostureAnalyzer
from exercises import ExerciseManager

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maksymalny rozmiar pliku: 16MB
app.config['SECRET_KEY'] = 'your-secret-key-here'  # W produkcji użyj zmiennej środowiskowej

# Utworzenie folderu na przesłane zdjęcia, jeśli nie istnieje
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicjalizacja modułów
work_monitor = WorkMonitor()
posture_analyzer = PostureAnalyzer()
exercise_manager = ExerciseManager()


@app.route('/')
def index():
    """
    Główna strona aplikacji.
    
    Returns:
        render_template: Szablon HTML strony głównej
    """
    return render_template('index.html')


@app.route('/api/work-time', methods=['GET'])
def get_work_time():
    """
    Endpoint API zwracający aktualny czas pracy.
    
    Returns:
        jsonify: JSON z informacjami o czasie pracy
    """
    work_time = work_monitor.get_current_work_time()
    break_suggested = work_monitor.should_take_break()
    
    return jsonify({
        'work_time_seconds': work_time,
        'work_time_formatted': format_time(work_time),
        'break_suggested': break_suggested,
        'break_message': 'Czas na przerwę!' if break_suggested else None
    })


@app.route('/api/start-work', methods=['POST'])
def start_work():
    """
    Endpoint do rozpoczęcia sesji pracy.
    
    Returns:
        jsonify: Potwierdzenie rozpoczęcia pracy
    """
    work_monitor.start_session()
    return jsonify({'status': 'success', 'message': 'Sesja pracy rozpoczęta'})


@app.route('/api/stop-work', methods=['POST'])
def stop_work():
    """
    Endpoint do zakończenia sesji pracy.
    
    Returns:
        jsonify: Potwierdzenie zakończenia pracy
    """
    work_monitor.stop_session()
    return jsonify({'status': 'success', 'message': 'Sesja pracy zakończona'})


@app.route('/api/break-taken', methods=['POST'])
def break_taken():
    """
    Endpoint do oznaczenia przerwy jako wykonanej.
    
    Returns:
        jsonify: Potwierdzenie wykonania przerwy
    """
    work_monitor.record_break()
    return jsonify({'status': 'success', 'message': 'Przerwa zarejestrowana'})


@app.route('/api/exercises', methods=['GET'])
def get_exercises():
    """
    Endpoint zwracający listę dostępnych ćwiczeń.
    
    Returns:
        jsonify: Lista ćwiczeń w formacie JSON
    """
    exercises = exercise_manager.get_exercises()
    return jsonify({'exercises': exercises})


@app.route('/api/exercise/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    """
    Endpoint zwracający szczegóły konkretnego ćwiczenia.
    
    Args:
        exercise_id: ID ćwiczenia
        
    Returns:
        jsonify: Szczegóły ćwiczenia lub błąd 404
    """
    exercise = exercise_manager.get_exercise(exercise_id)
    if exercise:
        return jsonify(exercise)
    return jsonify({'error': 'Ćwiczenie nie znalezione'}), 404


@app.route('/api/posture/upload', methods=['POST'])
def upload_posture_image():
    """
    Endpoint do przesyłania zdjęcia stanowiska pracy do analizy postawy.
    
    Returns:
        jsonify: Wyniki analizy postawy z sugestiami
    """
    if 'image' not in request.files:
        return jsonify({'error': 'Brak pliku obrazu'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400
    
    if file and allowed_file(file.filename):
        # Zapisanie pliku
        filename = f"posture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analiza postawy
        analysis = posture_analyzer.analyze_posture(filepath)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'analysis': analysis
        })
    
    return jsonify({'error': 'Nieprawidłowy format pliku'}), 400


@app.route('/api/posture/suggestions', methods=['GET'])
def get_posture_suggestions():
    """
    Endpoint zwracający ogólne sugestie dotyczące ergonomii stanowiska pracy.
    
    Returns:
        jsonify: Lista sugestii ergonomicznych
    """
    suggestions = posture_analyzer.get_ergonomic_suggestions()
    return jsonify({'suggestions': suggestions})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Endpoint zwracający statystyki pracy.
    
    Returns:
        jsonify: Statystyki dzienne i tygodniowe
    """
    stats = work_monitor.get_daily_stats()
    return jsonify(stats)


@app.route('/api/timer', methods=['GET'])
def get_timer():
    """
    Endpoint zwracający stan timera Pomodoro.
    
    Returns:
        jsonify: Stan timera
    """
    remaining = work_monitor.get_timer_remaining()
    return jsonify({
        'remaining_seconds': remaining,
        'remaining_formatted': work_monitor.format_timer_time(remaining),
        'running': work_monitor.timer_running,
        'paused': work_monitor.timer_paused,
        'timer_type': work_monitor.timer_type  # 'pomodoro' lub 'break'
    })


@app.route('/api/timer/pomodoro', methods=['POST'])
def start_pomodoro():
    """
    Endpoint do rozpoczęcia timera Pomodoro.
    
    Returns:
        jsonify: Potwierdzenie
    """
    work_monitor.start_pomodoro()
    return jsonify({'status': 'success', 'message': 'Timer Pomodoro rozpoczęty'})


@app.route('/api/timer/break', methods=['POST'])
def start_break():
    """
    Endpoint do rozpoczęcia timera przerwy.
    
    Returns:
        jsonify: Potwierdzenie
    """
    work_monitor.start_break()
    return jsonify({'status': 'success', 'message': 'Timer przerwy rozpoczęty'})


@app.route('/api/timer/pause', methods=['POST'])
def pause_timer():
    """
    Endpoint do pauzowania timera.
    
    Returns:
        jsonify: Potwierdzenie
    """
    work_monitor.pause_timer()
    return jsonify({'status': 'success', 'message': 'Timer zatrzymany'})


@app.route('/api/timer/resume', methods=['POST'])
def resume_timer():
    """
    Endpoint do wznowienia timera.
    
    Returns:
        jsonify: Potwierdzenie
    """
    work_monitor.resume_timer()
    return jsonify({'status': 'success', 'message': 'Timer wznowiony'})


@app.route('/api/timer/stop', methods=['POST'])
def stop_timer():
    """
    Endpoint do zatrzymania timera.
    
    Returns:
        jsonify: Potwierdzenie
    """
    work_monitor.stop_timer()
    return jsonify({'status': 'success', 'message': 'Timer zatrzymany'})


def allowed_file(filename):
    """
    Sprawdza, czy plik ma dozwolone rozszerzenie.
    
    Args:
        filename: Nazwa pliku
        
    Returns:
        bool: True jeśli plik jest dozwolony
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def format_time(seconds):
    """
    Formatuje czas w sekundach na czytelny format HH:MM:SS.
    
    Args:
        seconds: Czas w sekundach
        
    Returns:
        str: Sformatowany czas
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


if __name__ == '__main__':
    # Uruchomienie aplikacji w trybie debug (tylko do rozwoju)
    # Port 5001 zamiast 5000, ponieważ port 5000 jest często zajęty przez AirPlay na macOS
    app.run(debug=True, host='127.0.0.1', port=5001)

