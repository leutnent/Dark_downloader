import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import mainthread
import yt_dlp

class DownloaderApp(App):
    def build(self):
        self.title = "YT Downloader"
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        title_label = Label(
            text="YouTube Video Downloader",
            font_size='22sp',
            size_hint=(1, 0.15)
        )
        layout.add_widget(title_label)

        self.url_input = TextInput(
            hint_text="Paste YouTube URL here...",
            multiline=False,
            size_hint=(1, 0.15),
            font_size='16sp'
        )
        layout.add_widget(self.url_input)

        self.format_spinner = Spinner(
            text="Video - MP4 (720p)",
            values=(
                "Video - MP4 (720p)",
                "Video - MP4 (360p)",
                "Audio - M4A (High Quality)",
                "Audio - WEBM"
            ),
            size_hint=(1, 0.15),
            font_size='16sp'
        )
        layout.add_widget(self.format_spinner)

        self.download_btn = Button(
            text="Start Download",
            size_hint=(1, 0.15),
            font_size='18sp',
            background_color=(0.1, 0.6, 0.9, 1)
        )
        self.download_btn.bind(on_press=self.start_download_thread)
        layout.add_widget(self.download_btn)

        self.status_label = Label(
            text="Status: Ready\nSave folder: /sdcard/msc",
            font_size='15sp',
            size_hint=(1, 0.4)
        )
        layout.add_widget(self.status_label)

        return layout

    def start_download_thread(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status("Error: Please enter a valid URL!")
            return

        self.download_btn.disabled = True
        self.update_status("Status: Fetching video info...")
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        selected_format = self.format_spinner.text
        save_dir = "/sdcard/msc"
        
        try:
            os.makedirs(save_dir, exist_ok=True)
        except Exception:
            save_dir = os.path.expanduser("~")

        if "720p" in selected_format:
            fmt = "best[height<=720][ext=mp4]/best[ext=mp4]/best"
        elif "360p" in selected_format:
            fmt = "best[height<=360][ext=mp4]/best[ext=mp4]/best"
        elif "M4A" in selected_format:
            fmt = "bestaudio[ext=m4a]/bestaudio"
        else:
            fmt = "bestaudio[ext=webm]/bestaudio"

        ydl_opts = {
            'format': fmt,
            'outtmpl': f'{save_dir}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.update_status(f"Status: Download Complete!\nSaved in: {save_dir}")
        except Exception as e:
            self.update_status(f"Error: {str(e)[:60]}...")
        finally:
            self.enable_button()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            self.update_status(f"Downloading: {percent}\nSpeed: {speed}")

    @mainthread
    def update_status(self, text):
        self.status_label.text = text

    @mainthread
    def enable_button(self):
        self.download_btn.disabled = False

if __name__ == '__main__':
    DownloaderApp().run()
