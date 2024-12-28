import sys
import os
import ffmpeg
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QSpinBox, QPushButton, QFileDialog, QProgressBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent

class VideoCompressor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Compressor")
        self.setAcceptDrops(True)
        self.setMinimumSize(400, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create widgets
        self.status_label = QLabel("Drag and drop video file here\nor click Select File button")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("QLabel { padding: 20px; border: 2px dashed #aaa; border-radius: 10px; }")
        
        # Target size selection
        size_layout = QVBoxLayout()
        size_label = QLabel("Target Size (MB):")
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 2000)  # 1MB to 2GB
        self.size_spinbox.setValue(50)  # Default 50MB
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spinbox)
        
        # Select file button
        self.select_button = QPushButton("Select File")
        self.select_button.clicked.connect(self.select_file)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        
        # Add widgets to layout
        layout.addWidget(self.status_label)
        layout.addLayout(size_layout)
        layout.addWidget(self.select_button)
        layout.addWidget(self.progress_bar)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                padding: 8px;
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].toLocalFile().lower().endswith(
                ('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.compress_video(file_path)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv)"
        )
        if file_path:
            self.compress_video(file_path)

    def compress_video(self, input_path):
        try:
            # Get target size in bytes
            target_size_mb = self.size_spinbox.value()
            target_size_bytes = target_size_mb * 1024 * 1024
            
            # Get input video information
            probe = ffmpeg.probe(input_path)
            duration = float(probe['format']['duration'])
            
            # Calculate target bitrate (90% of target size to ensure final size is under limit)
            target_bitrate = int((target_size_bytes * 8 * 0.9) / duration)
            
            # Prepare output filename
            filename, ext = os.path.splitext(input_path)
            output_path = f"{filename}_compressed{ext}"
            
            # Update UI
            self.status_label.setText("Compressing video...")
            self.progress_bar.setRange(0, 0)
            self.progress_bar.show()
            
            # Run compression
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path,
                                 video_bitrate=target_bitrate,
                                 acodec='aac',
                                 audio_bitrate='128k')
            ffmpeg.run(stream, overwrite_output=True)
            
            # Update UI on completion
            self.status_label.setText(f"Compression complete!\nSaved to: {output_path}")
            self.progress_bar.hide()
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.progress_bar.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoCompressor()
    window.show()
    sys.exit(app.exec())
