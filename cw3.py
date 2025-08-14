import sys
import math
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import QTimer, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt, QPoint


class SevenSegmentDisplay(QWidget):
    """Customowy widżet wyświetlający cyfry w stylu 7-segmentowym"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.digit = 0
        self.segment_color = QColor(0, 255, 0)  # Zielony
        self.background_color = QColor(20, 20, 20)  # Ciemny
        self.inactive_color = QColor(40, 40, 40)  # Ciemny szary dla nieaktywnych segmentów
        self.setMinimumSize(60, 100)
        
        # Definicja segmentów dla każdej cyfry (a, b, c, d, e, f, g)
        self.segments = {
            0: [1, 1, 1, 1, 1, 1, 0],
            1: [0, 1, 1, 0, 0, 0, 0],
            2: [1, 1, 0, 1, 1, 0, 1],
            3: [1, 1, 1, 1, 0, 0, 1],
            4: [0, 1, 1, 0, 0, 1, 1],
            5: [1, 0, 1, 1, 0, 1, 1],
            6: [1, 0, 1, 1, 1, 1, 1],
            7: [1, 1, 1, 0, 0, 0, 0],
            8: [1, 1, 1, 1, 1, 1, 1],
            9: [1, 1, 1, 1, 0, 1, 1],
        }
    
    def set_digit(self, digit):
        """Ustawia cyfrę do wyświetlenia"""
        self.digit = digit % 10
        self.update()
    
    def set_color(self, color):
        """Ustawia kolor segmentów"""
        self.segment_color = color
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Tło
        painter.fillRect(self.rect(), self.background_color)
        
        # Wymiary segmentów
        w = self.width() - 10
        h = self.height() - 10
        thickness = max(4, min(w, h) // 15)
        
        # Pozycje segmentów
        segments_active = self.segments.get(self.digit, [0, 0, 0, 0, 0, 0, 0])
        
        # Rysowanie segmentów
        self.draw_segment(painter, 'a', 5 + thickness, 5, w - 2*thickness, thickness, segments_active[0])
        self.draw_segment(painter, 'b', 5 + w - thickness, 5 + thickness, thickness, h//2 - thickness, segments_active[1])
        self.draw_segment(painter, 'c', 5 + w - thickness, 5 + h//2 + thickness, thickness, h//2 - thickness, segments_active[2])
        self.draw_segment(painter, 'd', 5 + thickness, 5 + h - thickness, w - 2*thickness, thickness, segments_active[3])
        self.draw_segment(painter, 'e', 5, 5 + h//2 + thickness, thickness, h//2 - thickness, segments_active[4])
        self.draw_segment(painter, 'f', 5, 5 + thickness, thickness, h//2 - thickness, segments_active[5])
        self.draw_segment(painter, 'g', 5 + thickness, 5 + h//2, w - 2*thickness, thickness, segments_active[6])
    
    def draw_segment(self, painter, segment, x, y, w, h, active):
        """Rysuje pojedynczy segment"""
        color = self.segment_color if active else self.inactive_color
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color, 1))
        painter.drawRect(x, y, w, h)


class TimerDisplay(QWidget):
    """Widżet wyświetlający czas w formacie MM:SS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.minutes_tens = SevenSegmentDisplay()
        self.minutes_ones = SevenSegmentDisplay()
        self.seconds_tens = SevenSegmentDisplay()
        self.seconds_ones = SevenSegmentDisplay()
        
        self.setup_ui()
        
        # Animacja pulsowania
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_update)
        self.pulse_timer.setInterval(50)  # 20 FPS
        
        self.pulse_value = 0
        self.pulse_direction = 1
        self.is_pulsing = False
        self.base_color = QColor(0, 255, 0)  # Domyślny zielony
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(5)
        
        layout.addWidget(self.minutes_tens)
        layout.addWidget(self.minutes_ones)
        
        # Dwukropek
        colon_label = QLabel(":")
        colon_label.setStyleSheet("color: #00FF00; font-size: 48px; font-weight: bold;")
        colon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(colon_label)
        
        layout.addWidget(self.seconds_tens)
        layout.addWidget(self.seconds_ones)
        
        self.setLayout(layout)
    
    def set_time(self, minutes, seconds):
        """Ustawia czas do wyświetlenia"""
        self.minutes_tens.set_digit(minutes // 10)
        self.minutes_ones.set_digit(minutes % 10)
        self.seconds_tens.set_digit(seconds // 10)
        self.seconds_ones.set_digit(seconds % 10)
    
    def start_pulse(self):
        """Rozpoczyna animację pulsowania"""
        if not self.is_pulsing:
            self.is_pulsing = True
            self.pulse_timer.start()
    
    def stop_pulse(self):
        """Zatrzymuje animację pulsowania"""
        if self.is_pulsing:
            self.is_pulsing = False
            self.pulse_timer.stop()
            self.pulse_value = 0
            self.update_pulse_colors()
    
    def pulse_update(self):
        """Aktualizuje animację pulsowania"""
        self.pulse_value += self.pulse_direction * 5
        if self.pulse_value >= 100:
            self.pulse_value = 100
            self.pulse_direction = -1
        elif self.pulse_value <= 0:
            self.pulse_value = 0
            self.pulse_direction = 1
        
        self.update_pulse_colors()
    
    def update_pulse_colors(self):
        """Aktualizuje kolory podczas pulsowania"""
        if self.is_pulsing:
            # Interpolacja między normalnym kolorem a ciemniejszym
            intensity = 0.3 + 0.7 * (self.pulse_value / 100.0)
            red = int(self.base_color.red() * intensity)
            green = int(self.base_color.green() * intensity)
            blue = int(self.base_color.blue() * intensity)
            pulse_color = QColor(red, green, blue)
            
            for display in [self.minutes_tens, self.minutes_ones, self.seconds_tens, self.seconds_ones]:
                display.set_color(pulse_color)
    
    def set_color(self, color):
        """Ustawia kolor wszystkich wyświetlaczy"""
        self.base_color = color
        if not self.is_pulsing:
            for display in [self.minutes_tens, self.minutes_ones, self.seconds_tens, self.seconds_ones]:
                display.set_color(color)


class SpinningShape(QWidget):
    """Obracająca się figura geometryczna"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.speed = 1  # Prędkość obrotu
        self.setFixedSize(100, 100)
        
        # Timer dla animacji
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.rotate)
        self.animation_timer.start(16)  # ~60 FPS
    
    def rotate(self):
        """Obraca figurę"""
        self.angle += self.speed
        if self.angle >= 360:
            self.angle = 0
        self.update()
    
    def set_speed(self, speed):
        """Ustawia prędkość obrotu"""
        self.speed = speed
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Środek widżetu
        center = QPoint(self.width() // 2, self.height() // 2)
        
        # Przesunięcie i obrót
        painter.translate(center)
        painter.rotate(self.angle)
        
        # Rysowanie trójkąta
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.setPen(QPen(QColor(255, 150, 150), 2))
        
        # Punkty trójkąta
        size = 30
        points = [
            QPoint(0, -size),
            QPoint(int(-size * 0.866), size // 2),
            QPoint(int(size * 0.866), size // 2)
        ]
        
        painter.drawPolygon(points)


class CountdownTimer(QWidget):
    """Główny widżet minutnika"""
    
    finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.is_running = False
        
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Input dla czasu
        input_layout = QHBoxLayout()
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Wprowadź czas (MM:SS)")
        self.time_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 8px;
                border: 2px solid #333;
                border-radius: 5px;
                background-color: #222;
                color: #00FF00;
            }
        """)
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px 16px;
                border: 2px solid #00AA00;
                border-radius: 5px;
                background-color: #004400;
                color: #00FF00;
            }
            QPushButton:hover {
                background-color: #006600;
            }
            QPushButton:pressed {
                background-color: #002200;
            }
        """)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_timer)
        self.stop_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px 16px;
                border: 2px solid #AA0000;
                border-radius: 5px;
                background-color: #440000;
                color: #FF0000;
            }
            QPushButton:hover {
                background-color: #660000;
            }
            QPushButton:pressed {
                background-color: #220000;
            }
        """)
        
        input_layout.addWidget(self.time_input)
        input_layout.addWidget(self.start_button)
        input_layout.addWidget(self.stop_button)
        
        # Wyświetlacz czasu
        self.timer_display = TimerDisplay()
        
        # Obracająca się figura
        shape_layout = QHBoxLayout()
        shape_layout.addStretch()
        self.spinning_shape = SpinningShape()
        shape_layout.addWidget(self.spinning_shape)
        shape_layout.addStretch()
        
        # Status
        self.status_label = QLabel("Wprowadź czas i naciśnij Start")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #AAAAAA;
                padding: 10px;
            }
        """)
        
        layout.addLayout(input_layout)
        layout.addWidget(self.timer_display)
        layout.addLayout(shape_layout)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Styl głównego okna
        self.setStyleSheet("""
            QWidget {
                background-color: #111111;
            }
        """)
    
    def setup_timer(self):
        """Konfiguruje timer"""
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.setInterval(1000)  # 1 sekunda
    
    def parse_time_input(self, time_str):
        """Parsuje input czasu w formacie MM:SS"""
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    minutes = int(parts[0])
                    seconds = int(parts[1])
                    return minutes * 60 + seconds
            else:
                # Jeśli tylko liczba, traktuj jako sekundy
                return int(time_str)
        except ValueError:
            return 0
        return 0
    
    def start_timer(self):
        """Rozpoczyna odliczanie"""
        if self.is_running:
            return
        
        time_str = self.time_input.text().strip()
        self.total_seconds = self.parse_time_input(time_str)
        
        if self.total_seconds <= 0:
            self.status_label.setText("Nieprawidłowy format czasu!")
            return
        
        self.remaining_seconds = self.total_seconds
        self.is_running = True
        self.countdown_timer.start()
        
        # Reset efektów wizualnych
        self.timer_display.stop_pulse()
        self.timer_display.set_color(QColor(0, 255, 0))  # Zielony
        self.spinning_shape.set_speed(1)
        
        self.status_label.setText("Odliczanie...")
        self.update_display()
    
    def stop_timer(self):
        """Zatrzymuje odliczanie"""
        self.is_running = False
        self.countdown_timer.stop()
        self.timer_display.stop_pulse()
        self.timer_display.set_color(QColor(0, 255, 0))
        self.spinning_shape.set_speed(1)
        self.status_label.setText("Zatrzymano")
    
    def update_countdown(self):
        """Aktualizuje odliczanie"""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()
            
            # Efekty wizualne w ostatnich 10 sekundach
            if self.remaining_seconds <= 10:
                # Zmiana koloru na czerwony
                self.timer_display.set_color(QColor(255, 0, 0))
                # Przyspieszenie animacji
                speed = max(1, 11 - self.remaining_seconds)
                self.spinning_shape.set_speed(speed)
                
                # Pulsowanie w ostatnich 5 sekundach
                if self.remaining_seconds <= 5:
                    self.timer_display.start_pulse()
        else:
            # Czas się skończył
            self.finish_countdown()
    
    def update_display(self):
        """Aktualizuje wyświetlacz czasu"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        self.timer_display.set_time(minutes, seconds)
    
    def finish_countdown(self):
        """Kończy odliczanie z efektami"""
        self.is_running = False
        self.countdown_timer.stop()
        
        # Intensywne efekty wizualne
        self.timer_display.set_color(QColor(255, 0, 0))  # Czerwony
        self.timer_display.start_pulse()
        self.spinning_shape.set_speed(10)  # Bardzo szybko
        
        self.status_label.setText("CZAS MINĄŁ!")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #FF0000;
                font-weight: bold;
                padding: 10px;
            }
        """)
        
        self.finished.emit()


class MainWindow(QWidget):
    """Główne okno aplikacji"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minutnik 7-Segmentowy")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        # Tytuł
        title = QLabel("Minutnik z Cyframi 7-Segmentowymi")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #00FF00;
                padding: 20px;
            }
        """)
        
        # Minutnik
        self.countdown_timer = CountdownTimer()
        self.countdown_timer.finished.connect(self.on_timer_finished)
        
        layout.addWidget(title)
        layout.addWidget(self.countdown_timer)
        
        self.setLayout(layout)
        
        # Styl głównego okna
        self.setStyleSheet("""
            QWidget {
                background-color: #111111;
            }
        """)
    
    def on_timer_finished(self):
        """Obsługuje zakończenie odliczania"""
        print("Minutnik zakończony!")


def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()