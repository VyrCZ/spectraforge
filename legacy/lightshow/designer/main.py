import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton
)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem
from PyQt5.QtGui import QBrush, QPen


class Block(QGraphicsRectItem):
    """Draggable and resizable block on the timeline."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.setBrush(QBrush(QColor("blue")))
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.SizeHorCursor)


class Timeline(QGraphicsView):
    """Custom timeline with a scrollable and interactive interface."""
    def __init__(self, media_player):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.media_player = media_player

        # Timeline properties
        self.track_height = 50
        self.timeline_width = 3000  # Width in pixels for the entire timeline
        self.marker_line = None

        # Draw timeline background
        self.setBackgroundBrush(QBrush(QColor(50, 50, 50)))

        # Draw marker line
        self.marker_line = QGraphicsLineItem(0, 0, 0, self.track_height)
        self.marker_line.setPen(QPen(QColor("red"), 2))
        self.scene.addItem(self.marker_line)

        # Draw track background
        track_background = QGraphicsRectItem(0, 0, self.timeline_width, self.track_height)
        track_background.setBrush(QBrush(QColor(70, 70, 70)))
        track_background.setPen(QPen(Qt.NoPen))
        self.scene.addItem(track_background)

        # Set scene size
        self.setSceneRect(0, 0, self.timeline_width, self.track_height)

        # Auto-scroll with audio position
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_marker)
        self.timer.start(30)

    def add_block(self, start, duration):
        """Add a new block to the timeline."""
        x = start * 10  # Scale factor (10px per second)
        width = duration * 10
        block = Block(x, 10, width, 30)
        self.scene.addItem(block)

    def update_marker(self):
        """Update the marker line position based on audio playback."""
        position = self.media_player.position() / 1000.0  # Audio position in seconds
        x = position * 10  # Scale factor
        self.marker_line.setLine(x, 0, x, self.track_height)

        # Scroll the timeline view if the marker is near the edge
        if x > self.horizontalScrollBar().value() + self.viewport().width() - 50:
            self.horizontalScrollBar().setValue(int(x - 50))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adjustable Panels with Custom Gaps and Timeline")
        self.setFixedSize(1920, 1080)

        # Central widget with vertical layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left container (main part + bottom panel)
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: gray;
                height: 8px;  /* Thickness for vertical splitters */
            }
        """)

        # Main part (top left, black background)
        main_part = QWidget()
        main_part.setAutoFillBackground(True)
        palette = main_part.palette()
        palette.setColor(QPalette.Background, QColor("black"))
        main_part.setPalette(palette)
        main_part.setMinimumHeight(100)

        # Bottom panel with timeline and controls
        bottom_panel = self.create_bottom_panel()

        # Add to vertical splitter
        left_splitter.addWidget(main_part)
        left_splitter.addWidget(bottom_panel)
        left_splitter.setSizes([720, 380])  # Initial sizes
        left_splitter.setCollapsible(0, False)  # Prevent collapsing
        left_splitter.setCollapsible(1, False)

        # Right panel
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: darkgray;")
        right_panel.setMinimumWidth(200)

        # Horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([1200, 720])  # Initial sizes
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: gray;
                width: 8px;  /* Thickness for horizontal splitters */
            }
        """)
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)

        # Add main splitter to the layout
        main_layout.addWidget(main_splitter)

    def create_bottom_panel(self):
        """Create the bottom panel with controls and a timeline."""
        bottom_panel = QWidget()
        layout = QVBoxLayout(bottom_panel)

        # Media player
        self.media_player = QMediaPlayer()

        # Controls
        controls_layout = QHBoxLayout()
        play_button = QPushButton("Play")
        pause_button = QPushButton("Pause")
        stop_button = QPushButton("Stop")

        play_button.clicked.connect(self.media_player.play)
        pause_button.clicked.connect(self.media_player.pause)
        stop_button.clicked.connect(self.media_player.stop)

        controls_layout.addWidget(play_button)
        controls_layout.addWidget(pause_button)
        controls_layout.addWidget(stop_button)

        layout.addLayout(controls_layout)

        # Timeline
        self.timeline = Timeline(self.media_player)
        layout.addWidget(self.timeline)

        # Add a test block
        self.timeline.add_block(5, 3)  # Block at 5s, duration 3s

        # Load sample audio
        audio_url = QUrl.fromLocalFile("lightshow/static/audio/peer_gynt.mp3")  # Replace with your audio file
        content = QMediaContent(audio_url)
        self.media_player.setMedia(content)

        return bottom_panel


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
