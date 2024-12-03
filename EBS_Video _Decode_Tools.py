import sys
import pyaudio
import speech_recognition as sr
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QTextEdit, QLabel

class AudioDeviceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EBS Ses Decode Tools")
        self.setGeometry(100, 100, 600, 450)
        self.setWindowFlag(0x0002)  # Set window to be frameless
        self.setStyleSheet("background-color: #f4f4f4; border-radius: 10px;")  # Rounded window corners
        self.device_list = []
        self.init_ui()

    def init_ui(self):
        """GUI öğelerini oluştur."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Add margins for better spacing
        layout.setSpacing(15)  # Add space between widgets

        # Cihazları listeleme butonu (Oval button)
        self.list_devices_button = QPushButton("Ses Cihazlarını Listele")
        self.list_devices_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                font-size: 16px; 
                padding: 12px 30px; 
                border-radius: 30px; 
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.list_devices_button.clicked.connect(self.list_audio_devices)
        layout.addWidget(self.list_devices_button)

        # Cihaz seçimi için liste
        self.device_dropdown = QListWidget()
        self.device_dropdown.setStyleSheet("""
            QListWidget {
                font-size: 14px; 
                padding: 10px; 
                border-radius: 10px; 
                background-color: #ffffff;
                border: 1px solid #ddd;
            }
        """)
        layout.addWidget(self.device_dropdown)

        # Cihazı seç ve dinle butonu (Oval button)
        self.select_device_button = QPushButton("Cihazı Seç ve Dinle")
        self.select_device_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                font-size: 16px; 
                padding: 12px 30px; 
                border-radius: 30px; 
                border: none;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
        """)
        self.select_device_button.clicked.connect(self.select_audio_device)
        layout.addWidget(self.select_device_button)

        # Sonuçları göstermek için QLabel ve QTextEdit
        self.output_label = QLabel("Ses Tanıma Sonucu:")
        self.output_label.setStyleSheet("""
            QLabel {
                font-size: 18px; 
                font-weight: bold;
                color: #333;
            }
        """)
        layout.addWidget(self.output_label)

        self.output_text = QTextEdit()
        self.output_text.setStyleSheet("""
            QTextEdit {
                font-size: 14px; 
                padding: 10px; 
                background-color: #f0f0f0;
                border-radius: 10px; 
                border: 1px solid #ddd;
            }
        """)
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def list_audio_devices(self):
        """Mevcut ses cihazlarını listele."""
        p = pyaudio.PyAudio()
        self.device_list.clear()
        self.device_dropdown.clear()

        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            device_name = info['name']
            self.device_list.append((i, device_name))
            self.device_dropdown.addItem(device_name)

        p.terminate()

    def select_audio_device(self):
        """Seçilen cihazdan ses dinlemek için mikrofon oluştur."""
        selected_item = self.device_dropdown.currentItem()
        if selected_item is None:
            return  # Eğer bir cihaz seçilmemişse işlem yapma

        device_index = self.device_dropdown.currentRow()
        selected_device = self.device_list[device_index]
        device_id, device_name = selected_device

        # Ses dinleme işlemini bir thread üzerinden başlat
        self.output_text.append(f"{device_name} cihazından dinleniyor...")
        self.listener_thread = ListenerThread(device_id)
        self.listener_thread.update_text.connect(self.update_output)
        self.listener_thread.start()

    def update_output(self, text):
        """QTextEdit'e ses tanıma sonucunu yaz."""
        self.output_text.append(text)

class ListenerThread(QThread):
    update_text = pyqtSignal(str)

    def __init__(self, device_index):
        super().__init__()
        self.device_index = device_index

    def run(self):
        """Ses dinleme ve tanıma işlemini başlat."""
        r = sr.Recognizer()
        with sr.Microphone(device_index=self.device_index) as source:
            while True:
                try:
                    audio = r.listen(source)
                    text = r.recognize_google(audio, language='tr-TR')
                    self.update_text.emit(f"Duyulan: {text}")
                except sr.UnknownValueError:
                    # "Anlayamadım" mesajı gösterilmiyor
                    continue
                except sr.RequestError as e:
                    self.update_text.emit(f"Google Speech API hatası: {e}")
                    break

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application-wide style
    app.setStyleSheet("""
        QWidget {
            font-family: 'Arial', sans-serif;
            background-color: #ffffff;
        }
    """)

    window = AudioDeviceApp()
    window.show()
    sys.exit(app.exec_())
