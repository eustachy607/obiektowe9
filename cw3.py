import sys
import math
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor


class SevenSegmentDisplay(QWidget):
    """Minimalny wyświetlacz 7-segmentowy dla jednej cyfry (0-9)."""

    SEGMENTS = {
        0: (1, 1, 1, 1, 1, 1, 0),
        1: (0, 1, 1, 0, 0, 0, 0),
        2: (1, 1, 0, 1, 1, 0, 1),
        3: (1, 1, 1, 1, 0, 0, 1),
        4: (0, 1, 1, 0, 0, 1, 1),
        5: (1, 0, 1, 1, 0, 1, 1),
        6: (1, 0, 1, 1, 1, 1, 1),
        7: (1, 1, 1, 0, 0, 0, 0),
        8: (1, 1, 1, 1, 1, 1, 1),
        9: (1, 1, 1, 1, 0, 1, 1),
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._digit = 0
        self._active = QColor(0, 255, 0)
        self._inactive = QColor(40, 40, 40)
        self._background = QColor(20, 20, 20)
        self.setMinimumSize(48, 80)

    def set_digit(self, d: int) -> None:
        self._digit = max(0, min(9, int(d)))
        self.update()

    def set_color(self, color: QColor) -> None:
        self._active = color
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), self._background)

        w = self.width() - 10
        h = self.height() - 10
        x0, y0 = 5, 5
        thick = max(4, min(w, h) // 12)

        # Aktywne segmenty: a,b,c,d,e,f,g
        s = SevenSegmentDisplay.SEGMENTS.get(self._digit, (0,) * 7)

        def rect(x, y, ww, hh, on):
            color = self._active if on else self._inactive
            p.setBrush(QBrush(color))
            p.setPen(QPen(color, 1))
            p.drawRect(x, y, ww, hh)

        # a (top)
        rect(x0 + thick, y0, w - 2 * thick, thick, s[0])
        # b (top-right)
        rect(x0 + w - thick, y0 + thick, thick, h // 2 - thick, s[1])
        # c (bottom-right)
        rect(x0 + w - thick, y0 + h // 2 + thick, thick, h // 2 - thick, s[2])
        # d (bottom)
        rect(x0 + thick, y0 + h - thick, w - 2 * thick, thick, s[3])
        # e (bottom-left)
        rect(x0, y0 + h // 2 + thick, thick, h // 2 - thick, s[4])
        # f (top-left)
        rect(x0, y0 + thick, thick, h // 2 - thick, s[5])
        # g (middle)
        rect(x0 + thick, y0 + h // 2, w - 2 * thick, thick, s[6])


class TimerDisplay(QWidget):
    """Wyświetlacz MM:SS z 4 cyfr 7-segmentowych + dwukropek."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.d1 = SevenSegmentDisplay()
        self.d2 = SevenSegmentDisplay()
        self.d3 = SevenSegmentDisplay()
        self.d4 = SevenSegmentDisplay()

        layout = QHBoxLayout(self)
        layout.setSpacing(6)
        layout.addWidget(self.d1)
        layout.addWidget(self.d2)

        self.colon = QLabel(":")
        self.colon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.colon)

        layout.addWidget(self.d3)
        layout.addWidget(self.d4)

        self._base_color = QColor(0, 255, 0)
        self._apply_color(self._base_color)
        self._update_colon_color()

    def set_time(self, minutes: int, seconds: int) -> None:
        self.d1.set_digit((minutes // 10) % 10)
        self.d2.set_digit(minutes % 10)
        self.d3.set_digit((seconds // 10) % 10)
        self.d4.set_digit(seconds % 10)

    def set_base_color(self, color: QColor) -> None:
        self._base_color = color
        self._apply_color(self._base_color)
        self._update_colon_color()

    def apply_intensity(self, intensity: float) -> None:
        """intensity in [0.2..1.0] — skaluje jasność aktywnych segmentów."""
        intensity = max(0.2, min(1.0, intensity))
        c = self._scale_color(self._base_color, intensity)
        self._apply_color(c)

    def _apply_color(self, color: QColor) -> None:
        for d in (self.d1, self.d2, self.d3, self.d4):
            d.set_color(color)

    def _update_colon_color(self) -> None:
        c = self._base_color
        self.colon.setStyleSheet(
            f"color: rgb({c.red()}, {c.green()}, {c.blue()}); font-size: 42px; font-weight: bold;"
        )

    @staticmethod
    def _scale_color(c: QColor, k: float) -> QColor:
        return QColor(int(c.red() * k), int(c.green() * k), int(c.blue() * k))


class MainWindow(QWidget):
    """Prosty minutnik z cyframi 7-segmentowymi, pulsującymi szybciej bliżej końca.
       Ostatnie 10 sekund w kolorze czerwonym."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Minutnik 7-segmentowy (prosty)")

        self.total_seconds = 0
        self.remaining_seconds = 0
        self.is_running = False
        self._pulse_t = 0.0  # czas dla animacji pulsowania

        # Tick co sekundę
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)

        # Puls co ~40 ms
        self.pulse_timer = QTimer(self)
        self.pulse_timer.setInterval(40)
        self.pulse_timer.timeout.connect(self._pulse_tick)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Input + przyciski
        input_layout = QHBoxLayout()
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("MM:SS lub sekundy")
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        input_layout.addWidget(self.time_input)
        input_layout.addWidget(self.start_button)
        input_layout.addWidget(self.stop_button)

        # Wyświetlacz 7-segmentowy
        self.display = TimerDisplay()

        # Status
        self.status_label = QLabel("Wprowadź czas i naciśnij Start")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(input_layout)
        layout.addWidget(self.display)
        layout.addWidget(self.status_label)

    def start(self) -> None:
        if self.is_running:
            return
        total = self._parse_time(self.time_input.text().strip())
        if total <= 0:
            self.status_label.setText("Nieprawidłowy czas")
            return
        self.total_seconds = total
        self.remaining_seconds = total
        self.is_running = True
        self._pulse_t = 0.0
        self.timer.start()
        self.pulse_timer.start()
        self.status_label.setText("Odliczanie...")
        self._update_display()
        self._update_base_color()

    def stop(self) -> None:
        self.is_running = False
        self.timer.stop()
        self.pulse_timer.stop()
        self.status_label.setText("Zatrzymano")
        # Przywróć bazową zieleń i jasność
        self.display.set_base_color(QColor(0, 255, 0))
        self.display.apply_intensity(1.0)

    def _tick(self) -> None:
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._update_display()
            self._update_base_color()
        if self.remaining_seconds <= 0 and self.is_running:
            self.timer.stop()
            self.is_running = False
            self.status_label.setText("Koniec")

    def _pulse_tick(self) -> None:
        if not self.is_running:
            return
        # Postęp od 0 (start) do 1 (koniec). Zabezpieczenie na dzielenie przez zero.
        progress = 1.0 if self.total_seconds <= 0 else 1.0 - (self.remaining_seconds / self.total_seconds)
        progress = max(0.0, min(1.0, progress))

        # Częstotliwość rośnie wraz z postępem (0.5 Hz -> 4.0 Hz)
        freq = 0.5 + 3.5 * progress
        self._pulse_t += 0.04  # ~40 ms

        # Sygnał 0..1
        phase = math.sin(2.0 * math.pi * freq * self._pulse_t) * 0.5 + 0.5

        # Amplituda rośnie (delikatnie na początku, mocno pod koniec)
        amp = 0.25 + 0.65 * progress  # 0.25..0.9
        # Skala jasności (0.2..1.0), oscyluje wokół ~0.7..1.0 bliżej końca
        intensity = 0.4 + amp * phase
        intensity = max(0.2, min(1.0, intensity))

        self.display.apply_intensity(intensity)

    def _update_base_color(self) -> None:
        # Czerwony w ostatnich 10 sekundach, inaczej zielony
        if self.remaining_seconds <= 10:
            self.display.set_base_color(QColor(255, 0, 0))
        else:
            self.display.set_base_color(QColor(0, 255, 0))

    def _update_display(self) -> None:
        m = max(0, self.remaining_seconds) // 60
        s = max(0, self.remaining_seconds) % 60
        self.display.set_time(m, s)

    @staticmethod
    def _parse_time(text: str) -> int:
        """Zwraca całkowitą liczbę sekund dla 'MM:SS' lub liczby całkowitej."""
        try:
            if ":" in text:
                parts = text.split(":")
                if len(parts) == 2:
                    return int(parts[0]) * 60 + int(parts[1])
                return 0
            return int(text)
        except ValueError:
            return 0


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
