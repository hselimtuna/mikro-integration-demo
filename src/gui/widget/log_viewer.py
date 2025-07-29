import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import time


class LogViewer(ttk.Frame):

    def __init__(self, parent, gui_handler):
        super().__init__(parent)
        self.gui_handler = gui_handler
        self.is_running = True

        self._setup_styles()
        self._create_widgets()
        self._start_log_monitoring()

    def _setup_styles(self):
        self.colors = {
            'INFO': '#4FC3F7',  # Light blue for info
            'WARNING': '#FFB74D',  # Orange for warnings
            'ERROR': '#F44336',  # Red for errors
            'DEBUG': '#81C784',  # Green for debug
            'CRITICAL': '#E91E63',  # Pink for critical
            'background': '#1A237E',  # Dark blue background
            'text': '#FFFFFF',  # White text
            'timestamp': '#90CAF9'  # Light blue for timestamps
        }

    def _create_widgets(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title_label = ttk.Label(self, text="Mikro Entegrasyon Logger")
        title_label.pack(pady=(0, 10))

        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.clear_btn = ttk.Button(control_frame, text="Temizle",
                                    command=self._clear_logs)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_cb = ttk.Checkbutton(control_frame, text="Otomatik Kaydır",
                                              variable=self.auto_scroll_var)
        self.auto_scroll_cb.pack(side=tk.LEFT)

        self.log_count_label = ttk.Label(control_frame, text="Log Sayısı: 0")
        self.log_count_label.pack(side=tk.RIGHT)

        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True)

        import platform
        if platform.system() == "Darwin":  # macOS
            font_family = ('Monaco', 10)
        elif platform.system() == "Windows":
            font_family = ('Consolas', 10)
        else:
            font_family = ('monospace', 10)

        self.text_widget = tk.Text(text_frame,
                                   bg=self.colors['background'],
                                   fg=self.colors['text'],
                                   font=font_family,
                                   wrap=tk.WORD,
                                   state=tk.DISABLED,
                                   insertbackground=self.colors['text'])

        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL,
                                  command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)

        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._configure_text_tags()

        self.log_count = 0

    def _configure_text_tags(self):
        import platform
        if platform.system() == "Darwin":  # macOS
            font_family = ('Monaco', 10, 'bold')
        elif platform.system() == "Windows":
            font_family = ('Consolas', 10, 'bold')
        else:
            font_family = ('monospace', 10, 'bold')

        for level, color in self.colors.items():
            if level in ['INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL']:
                self.text_widget.tag_configure(level, foreground=color, font=font_family)

        self.text_widget.tag_configure('timestamp', foreground=self.colors['timestamp'])
        self.text_widget.tag_configure('separator', foreground='#555555')

    def _start_log_monitoring(self):
        self.monitor_thread = threading.Thread(target=self._monitor_logs, daemon=True)
        self.monitor_thread.start()

    def _monitor_logs(self):
        while self.is_running:
            try:
                log_entry = self.gui_handler.get_log_entry()
                if log_entry:
                    self.after(0, self._add_log_entry, log_entry)
                time.sleep(0.1)  # Check every 100ms
            except Exception as e:
                print(f"Error in log monitoring: {e}")

    def _add_log_entry(self, log_entry):
        self.text_widget.config(state=tk.NORMAL)

        timestamp = datetime.fromtimestamp(log_entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        level = log_entry['level']
        message = log_entry['message']

        self.text_widget.insert(tk.END, level, level)
        self.text_widget.insert(tk.END, ' | ', 'separator')
        self.text_widget.insert(tk.END, timestamp, 'timestamp')
        self.text_widget.insert(tk.END, ' | ', 'separator')
        self.text_widget.insert(tk.END, message + '\n')

        self.text_widget.config(state=tk.DISABLED)

        if self.auto_scroll_var.get():
            self.text_widget.see(tk.END)

        self.log_count += 1
        self.log_count_label.config(text=f"Log Sayısı: {self.log_count}")

    def _clear_logs(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)
        self.log_count = 0
        self.log_count_label.config(text="Log Sayısı: 0")
        self.gui_handler.clear_queue()

    def stop_monitoring(self):
        self.is_running = False