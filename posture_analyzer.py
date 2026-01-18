"""
Moduł analizy postawy siedzącej przy komputerze.

Moduł analizuje przesłane zdjęcia stanowiska pracy używając OpenCV
do wykrywania linii, kątów i kształtów, a następnie sugeruje poprawki ergonomiczne.
"""

import cv2
import numpy as np
from PIL import Image
import os
import math


class PostureAnalyzer:
    """
    Klasa odpowiedzialna za analizę postawy siedzącej.
    
    Funkcjonalności:
    - Analiza przesłanych zdjęć stanowiska
    - Wykrywanie kątów i linii ciała
    - Wykrywanie nieprawidłowej postawy
    - Sugestie poprawy ergonomii
    """
    
    def __init__(self):
        """
        Inicjalizacja analizatora postawy.
        """
        self.ergonomic_suggestions = self._load_ergonomic_suggestions()
    
    def analyze_posture(self, image_path):
        """
        Analizuje przesłane zdjęcie stanowiska pracy.
        Wykrywa linie i kąty, aby ocenić postawę.
        
        Args:
            image_path: Ścieżka do przesłanego zdjęcia
            
        Returns:
            dict: Wyniki analizy z sugestiami poprawy
        """
        try:
            # Wczytanie obrazu
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'status': 'error',
                    'message': 'Nie można wczytać obrazu'
                }
            
            # Analiza obrazu z wykrywaniem linii i kątów
            analysis = self._analyze_posture_angles(image)
            
            # Określenie, czy postawa jest prawidłowa
            is_correct = self._evaluate_posture(analysis)
            
            # Generowanie sugestii
            suggestions = self._generate_suggestions(analysis, is_correct)
            
            return {
                'status': 'success',
                'is_correct_posture': is_correct,
                'analysis': analysis,
                'suggestions': suggestions,
                'message': 'Postawa prawidłowa' if is_correct else 'Wykryto problemy z postawą'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Błąd podczas analizy: {str(e)}'
            }
    
    def _analyze_posture_angles(self, image):
        """
        Analizuje obraz pod kątem wykrywania linii, kątów i kształtów ciała.
        
        Args:
            image: Obraz OpenCV
            
        Returns:
            dict: Wyniki analizy z wykrytymi kątami i kształtami
        """
        height, width = image.shape[:2]
        
        # Konwersja do skali szarości
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Zastosowanie rozmycia Gaussa, aby zmniejszyć szum
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Wykrywanie krawędzi używając Canny z lepszymi parametrami
        edges = cv2.Canny(blurred, 30, 100)
        
        # Wykrywanie linii używając transformacji Hough
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                minLineLength=30, maxLineGap=15)
        
        # Analiza kątów linii
        angles = []
        vertical_lines = []
        horizontal_lines = []
        diagonal_lines = []  # Linie ukośne (pochylone plecy)
        diagonal_forward_lines = []  # Linie ukośne wskazujące na pochylenie do przodu
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Obliczenie kąta linii
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                # Normalizacja kąta
                if angle > 90:
                    angle = angle - 180
                elif angle < -90:
                    angle = angle + 180
                angles.append(angle)
                
                # Klasyfikacja linii
                abs_angle = abs(angle)
                if abs_angle < 20 or abs_angle > 160:  # Prawie pozioma
                    horizontal_lines.append((x1, y1, x2, y2))
                elif 70 < abs_angle < 110:  # Prawie pionowa
                    vertical_lines.append((x1, y1, x2, y2))
                else:  # Ukośna
                    diagonal_lines.append((x1, y1, x2, y2))
                    # Wykrywanie linii ukośnych wskazujących na pochylenie do przodu (głowa/plecy)
                    # Kąty w zakresie 20-70° lub -20 do -70° wskazują na pochylenie
                    if (20 < abs_angle < 70) or (110 < abs_angle < 160):
                        diagonal_forward_lines.append((x1, y1, x2, y2))
        
        # Analiza jasności
        brightness = np.mean(gray)
        
        # Wykrywanie konturów dla analizy kształtów
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analiza kształtu konturów - wykrywanie zaokrąglonych vs prostych kształtów
        curved_shapes = 0
        straight_shapes = 0
        c_shape_detected = False
        
        for contour in contours:
            if len(contour) > 10:  # Większe kontury są bardziej znaczące
                # Aproksymacja konturu
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Sprawdzenie, czy kontur ma kształt C (zaokrąglony)
                if len(approx) < 8:
                    curved_shapes += 1
                    # Sprawdzenie, czy kontur jest wystarczająco duży i zaokrąglony
                    area = cv2.contourArea(contour)
                    if area > (height * width * 0.01):  # Co najmniej 1% obrazu
                        # Sprawdzenie, czy kontur jest bardziej zaokrąglony niż prosty
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        if hull_area > 0:
                            solidity = area / hull_area
                            if solidity < 0.7:  # Niska solidność = bardziej zaokrąglony kształt
                                c_shape_detected = True
        
        # Analiza kątów
        right_angles = sum(1 for angle in angles if 80 < abs(angle) < 100)
        angles_near_90 = sum(1 for angle in angles if 80 < abs(angle) < 100)
        angles_near_0 = sum(1 for angle in angles if abs(angle) < 20 or abs(angle) > 160)
        
        # Średni kąt linii
        avg_angle = np.mean([abs(a) for a in angles]) if angles else 0
        
        # Analiza proporcji linii
        total_lines = len(lines) if lines is not None else 0
        vertical_ratio = len(vertical_lines) / total_lines if total_lines > 0 else 0
        horizontal_ratio = len(horizontal_lines) / total_lines if total_lines > 0 else 0
        diagonal_ratio = len(diagonal_lines) / total_lines if total_lines > 0 else 0
        diagonal_forward_ratio = len(diagonal_forward_lines) / total_lines if total_lines > 0 else 0
        
        # Analiza gęstości krawędzi w różnych regionach obrazu
        top_region = edges[0:height//3, :]
        middle_region = edges[height//3:2*height//3, :]
        bottom_region = edges[2*height//3:, :]
        
        top_density = np.sum(top_region > 0) / (top_region.shape[0] * top_region.shape[1]) if top_region.size > 0 else 0
        middle_density = np.sum(middle_region > 0) / (middle_region.shape[0] * middle_region.shape[1]) if middle_region.size > 0 else 0
        bottom_density = np.sum(bottom_region > 0) / (bottom_region.shape[0] * bottom_region.shape[1]) if bottom_region.size > 0 else 0
        
        # Analiza rozkładu linii w regionach (pochylone plecy mają więcej linii ukośnych w środkowym regionie)
        middle_lines = 0
        middle_diagonal = 0
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                mid_y = (y1 + y2) / 2
                if height//3 < mid_y < 2*height//3:  # Linia w środkowym regionie
                    middle_lines += 1
                    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                    if angle > 90:
                        angle = angle - 180
                    elif angle < -90:
                        angle = angle + 180
                    if not (70 < abs(angle) < 110) and not (abs(angle) < 20 or abs(angle) > 160):
                        middle_diagonal += 1
        
        middle_diagonal_ratio = middle_diagonal / middle_lines if middle_lines > 0 else 0
        
        return {
            'image_width': width,
            'image_height': height,
            'brightness': brightness,
            'edge_density': np.sum(edges > 0) / (height * width),
            'line_count': total_lines,
            'vertical_lines': len(vertical_lines),
            'horizontal_lines': len(horizontal_lines),
            'diagonal_lines': len(diagonal_lines),
            'diagonal_forward_lines': len(diagonal_forward_lines),
            'vertical_ratio': vertical_ratio,
            'horizontal_ratio': horizontal_ratio,
            'diagonal_ratio': diagonal_ratio,
            'diagonal_forward_ratio': diagonal_forward_ratio,
            'right_angles_detected': right_angles,
            'angles_near_90': angles_near_90,
            'angles_near_0': angles_near_0,
            'average_angle': avg_angle,
            'contour_count': len(contours),
            'curved_shapes': curved_shapes,
            'straight_shapes': straight_shapes,
            'c_shape_detected': c_shape_detected,
            'top_density': top_density,
            'middle_density': middle_density,
            'bottom_density': bottom_density,
            'middle_diagonal_ratio': middle_diagonal_ratio,
            'aspect_ratio': width / height if height > 0 else 0
        }
    
    def _evaluate_posture(self, analysis):
        """
        Ocenia, czy postawa jest prawidłowa na podstawie analizy kątów i linii.
        KONSERWATYWNE PODEJŚCIE - domyślnie zakłada nieprawidłową postawę.
        
        Args:
            analysis: Wyniki analizy obrazu
            
        Returns:
            bool: True jeśli postawa wydaje się prawidłowa
        """
        # Sprawdzenie, czy obraz został poprawnie przeanalizowany
        if analysis['line_count'] < 5:
            return False  # Za mało informacji
        
        # KONSERWATYWNE PODEJŚCIE - wymagamy wyraźnych oznak dobrej postawy
        # Domyślnie zakładamy nieprawidłową postawę
        
        # KRYTERIA DYSKWALIFIKUJĄCE (jeśli spełnione, postawa jest na pewno nieprawidłowa)
        
        # 1. Wykryto kształt C (pochylone plecy)
        if analysis['c_shape_detected']:
            return False
        
        # 2. Zbyt wiele linii ukośnych wskazujących na pochylenie do przodu
        if analysis['diagonal_forward_ratio'] > 0.4:
            return False
        
        # 3. Zbyt wiele linii ukośnych w ogóle
        if analysis['diagonal_ratio'] > 0.5:
            return False
        
        # 4. Za mało linii pionowych (plecy nie są proste)
        if analysis['vertical_ratio'] < 0.15:
            return False
        
        # 5. Wiele linii ukośnych w środkowym regionie (pochylone plecy)
        if analysis['middle_diagonal_ratio'] > 0.5:
            return False
        
        # Punktacja dla oceny postawy - tylko pozytywne wskaźniki
        score = 0
        
        # 1. Analiza linii pionowych (plecy powinny być proste)
        if analysis['vertical_ratio'] > 0.35:  # Wysoki próg - co najmniej 35%
            score += 4
        elif analysis['vertical_ratio'] > 0.25:
            score += 2
        
        # 2. Mało linii ukośnych (brak pochylenia)
        if analysis['diagonal_ratio'] < 0.25:
            score += 3
        elif analysis['diagonal_ratio'] < 0.35:
            score += 1
        
        # 3. Mało linii ukośnych wskazujących na pochylenie do przodu
        if analysis['diagonal_forward_ratio'] < 0.2:
            score += 2
        
        # 4. Analiza kątów prostych (kolana, łokcie powinny być pod kątem 90°)
        if analysis['line_count'] > 15:
            if analysis['angles_near_90'] >= 4:
                score += 2
            elif analysis['angles_near_90'] >= 2:
                score += 1
        
        # 5. Analiza kształtów - prawidłowa postawa ma więcej prostych kształtów
        total_shapes = analysis['curved_shapes'] + analysis['straight_shapes']
        if total_shapes > 5:
            straight_ratio = analysis['straight_shapes'] / total_shapes
            if straight_ratio > 0.5:  # Więcej prostych kształtów
                score += 2
        
        # 6. Mało linii ukośnych w środkowym regionie
        if analysis['middle_diagonal_ratio'] < 0.3:
            score += 2
        
        # 7. Analiza średniego kąta - powinien być bliski 0° lub 90°
        avg_abs = analysis['average_angle']
        if avg_abs > 0:
            if avg_abs < 25 or (65 < avg_abs < 115):  # Blisko 0° lub 90°
                score += 1
            elif 30 < avg_abs < 60:  # Średni kąt wskazuje na pochylenie
                score -= 2  # Kara za pochylenie
        
        # WYMAGAMY WYSOKIEJ PUNKTACJI - minimum 8 punktów z maksymalnie 16
        # To jest bardzo restrykcyjne, ale zapewnia, że tylko wyraźnie dobra postawa przejdzie
        is_correct = score >= 8
        
        return is_correct
    
    def _generate_suggestions(self, analysis, is_correct):
        """
        Generuje sugestie poprawy postawy na podstawie analizy.
        
        Args:
            analysis: Wyniki analizy obrazu
            is_correct: Czy postawa jest prawidłowa
            
        Returns:
            list: Lista sugestii poprawy
        """
        suggestions = []
        
        # Jeśli postawa jest prawidłowa, zwróć tylko ogólne sugestie
        if is_correct:
            suggestions.append({
                'category': 'Postawa',
                'title': 'Gratulacje!',
                'description': 'Twoja postawa wydaje się prawidłowa. Kontynuuj utrzymywanie dobrej ergonomii podczas pracy.',
                'priority': 'niska'
            })
            suggestions.extend([
                {
                    'category': 'Ogólne',
                    'title': 'Pamiętaj o przerwach',
                    'description': 'Nawet przy prawidłowej postawie rób regularne przerwy co 50-60 minut.',
                    'priority': 'średnia'
                },
                {
                    'category': 'Ogólne',
                    'title': 'Ćwiczenia rozciągające',
                    'description': 'Wykonuj ćwiczenia rozciągające podczas przerw, aby utrzymać elastyczność mięśni.',
                    'priority': 'niska'
                }
            ])
            return suggestions
        
        # Analiza konkretnych problemów
        
        # Problem 1: Wykryto kształt C (pochylone plecy)
        if analysis.get('c_shape_detected', False):
            suggestions.append({
                'category': 'Postawa',
                'title': 'Pochylone plecy (kształt C)',
                'description': 'Wykryto zaokrąglone plecy w kształcie litery C. To wskazuje na poważne pochylenie. Wyprostuj plecy, oprzyj je o oparcie krzesła i upewnij się, że siedzisz prosto.',
                'priority': 'wysoka',
                'detected_issue': 'Wykryto kształt C wskazujący na pochylone plecy'
            })
        
        # Problem 2: Za mało linii pionowych (pochylone plecy)
        if analysis['vertical_ratio'] < 0.15:
            suggestions.append({
                'category': 'Postawa',
                'title': 'Pozycja pleców - pochylone',
                'description': 'Wykryto bardzo mało linii pionowych, co wskazuje na pochylone plecy. Siedź prosto, trzymając plecy oparte o oparcie krzesła. Ramiona powinny być rozluźnione i wycofane do tyłu.',
                'priority': 'wysoka',
                'detected_issue': f'Wykryto tylko {analysis["vertical_ratio"]*100:.1f}% linii pionowych (zalecane >25%)'
            })
        
        # Problem 3: Zbyt wiele linii ukośnych wskazujących na pochylenie do przodu
        if analysis.get('diagonal_forward_ratio', 0) > 0.3:
            suggestions.append({
                'category': 'Postawa',
                'title': 'Pochylenie do przodu',
                'description': 'Wykryto wiele linii ukośnych wskazujących na pochylenie głowy i pleców do przodu. Wyprostuj głowę i plecy, upewnij się, że siedzisz prosto.',
                'priority': 'wysoka',
                'detected_issue': f'Wykryto {analysis["diagonal_forward_ratio"]*100:.1f}% linii wskazujących na pochylenie do przodu'
            })
        
        # Problem 4: Zbyt wiele linii ukośnych w ogóle
        if analysis['diagonal_ratio'] > 0.4:
            suggestions.append({
                'category': 'Postawa',
                'title': 'Pochylone plecy',
                'description': 'Wykryto zbyt wiele linii ukośnych, co wskazuje na pochylone plecy. Wyprostuj plecy i oprzyj je o oparcie krzesła.',
                'priority': 'wysoka',
                'detected_issue': f'Wykryto {analysis["diagonal_ratio"]*100:.1f}% linii ukośnych (wskazuje na pochylenie)'
            })
        
        # Problem 5: Wiele linii ukośnych w środkowym regionie
        if analysis.get('middle_diagonal_ratio', 0) > 0.4:
            suggestions.append({
                'category': 'Postawa',
                'title': 'Pochylone plecy w środkowej części',
                'description': 'Wykryto wiele linii ukośnych w środkowej części ciała, co wskazuje na pochylone plecy. Wyprostuj plecy i upewnij się, że są oparte o oparcie krzesła.',
                'priority': 'wysoka',
                'detected_issue': f'Wykryto {analysis["middle_diagonal_ratio"]*100:.1f}% linii ukośnych w środkowym regionie'
            })
        
        # Problem 6: Za mało kątów prostych
        if analysis['angles_near_90'] < 2:
            suggestions.append({
                'category': 'Postawa',
                'title': 'Kąty ciała',
                'description': 'Kąty ciała nie są optymalne. Kolana powinny być zgięte pod kątem 90 stopni, a ręce również pod kątem 90 stopni. Upewnij się, że siedzisz z prostymi plecami.',
                'priority': 'wysoka',
                'detected_issue': f'Wykryto tylko {analysis["angles_near_90"]} kątów prostych (zalecane ≥3)'
            })
        
        # Problem 7: Za mało linii w ogóle
        if analysis['line_count'] < 10:
            suggestions.append({
                'category': 'Zdjęcie',
                'title': 'Jakość zdjęcia',
                'description': 'Zdjęcie może być zbyt rozmyte lub niewyraźne. Spróbuj przesłać zdjęcie w lepszym oświetleniu, z większą ostrością i wyraźnymi konturami ciała.',
                'priority': 'średnia',
                'detected_issue': f'Wykryto tylko {analysis["line_count"]} linii w obrazie (zalecane >10)'
            })
        
        # Standardowe sugestie dla nieprawidłowej postawy
        suggestions.extend([
            {
                'category': 'Krzesło',
                'title': 'Wysokość siedziska',
                'description': 'Ustaw wysokość siedziska tak, aby stopy płasko spoczywały na podłodze, a kolana były zgięte pod kątem 90 stopni.',
                'priority': 'wysoka'
            },
            {
                'category': 'Krzesło',
                'title': 'Podparcie lędźwiowe',
                'description': 'Użyj poduszki lędźwiowej lub ustaw oparcie krzesła tak, aby wspierało naturalną krzywiznę dolnej części pleców.',
                'priority': 'wysoka'
            },
            {
                'category': 'Postawa',
                'title': 'Pozycja głowy i szyi',
                'description': 'Głowa powinna być w pozycji neutralnej, ekran na wysokości oczu. Unikaj pochylania głowy do przodu.',
                'priority': 'średnia'
            },
            {
                'category': 'Krzesło',
                'title': 'Głębokość siedziska',
                'description': 'Ustaw głębokość siedziska tak, aby między krawędzią siedziska a tyłem kolan było około 2-4 cm przestrzeni.',
                'priority': 'średnia'
            },
            {
                'category': 'Pozycja',
                'title': 'Pozycja ramion',
                'description': 'Ręce powinny być zgięte pod kątem 90 stopni, przedramiona równoległe do podłogi.',
                'priority': 'średnia'
            }
        ])
        
        # Sugestie na podstawie jasności
        if analysis.get('brightness', 0) < 80:
            suggestions.append({
                'category': 'Oświetlenie',
                'title': 'Oświetlenie stanowiska',
                'description': 'Stanowisko wydaje się zbyt ciemne. Zwiększ oświetlenie, aby zmniejszyć zmęczenie oczu i ułatwić analizę postawy.',
                'priority': 'średnia',
                'detected_issue': f'Jasność obrazu: {analysis.get("brightness", 0):.1f} (zalecane > 100)'
            })
        
        return suggestions
    
    def get_ergonomic_suggestions(self):
        """
        Zwraca ogólne sugestie dotyczące ergonomii stanowiska pracy.
        
        Returns:
            list: Lista ogólnych sugestii ergonomicznych
        """
        return self._load_ergonomic_suggestions()
    
    def _load_ergonomic_suggestions(self):
        """
        Ładuje listę ogólnych sugestii ergonomicznych.
        
        Returns:
            list: Lista sugestii
        """
        return [
            {
                'category': 'Krzesło',
                'title': 'Prawidłowe ustawienie krzesła',
                'points': [
                    'Wysokość siedziska: stopy płasko na podłodze, kolana pod kątem 90°',
                    'Głębokość siedziska: 2-4 cm przestrzeni między krawędzią a tyłem kolan',
                    'Oparcie: wsparcie dla dolnej części pleców (lędźwi)',
                    'Podłokietniki: na wysokości, która pozwala na rozluźnienie ramion'
                ]
            },
            {
                'category': 'Monitor',
                'title': 'Ustawienie monitora',
                'points': [
                    'Górna krawędź monitora na wysokości oczu lub nieco poniżej',
                    'Odległość: 50-70 cm od twarzy',
                    'Kąt nachylenia: lekko do tyłu (10-20 stopni)',
                    'Unikaj odblasków i refleksów świetlnych'
                ]
            },
            {
                'category': 'Klawiatura i mysz',
                'title': 'Pozycja klawiatury i myszy',
                'points': [
                    'Klawiatura na wysokości łokci lub nieco niżej',
                    'Nadgarstki w pozycji neutralnej, nie zgięte',
                    'Mysz blisko klawiatury, aby uniknąć nadmiernego sięgania',
                    'Używaj podkładek pod nadgarstki, jeśli to konieczne'
                ]
            },
            {
                'category': 'Ogólne',
                'title': 'Dobre praktyki',
                'points': [
                    'Rób regularne przerwy co 50-60 minut',
                    'Podczas przerw wstań i poruszaj się',
                    'Wykonuj ćwiczenia rozciągające szyję, ramiona i plecy',
                    'Utrzymuj prawidłową postawę przez cały dzień',
                    'Pij odpowiednią ilość wody'
                ]
            }
        ]
