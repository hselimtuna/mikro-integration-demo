import tkinter as tk
from tkinter import ttk
import threading
from src.gui.widget.log_viewer import LogViewer
from src.gui.handler.log_handler import GUILogHandler
from src.logger.custom_logger import SingletonLogger
from src.run import Run


class MainWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.gui_handler = GUILogHandler()
        self.is_running = False
        self.run_thread = None

        self._setup_window()
        self._setup_theme()
        self._create_widgets()
        self._setup_gui_logging()

    def _setup_window(self):
        self.root.title("Mikro Entegrasyon")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_theme(self):
        style = ttk.Style()

        try:
            style.theme_use('clam')
        except Exception:
            style.theme_use('default')

        try:
            bg_color = '#1A237E'
            btn_color = '#3F51B5'
            btn_active = '#5C6BC0'
            btn_pressed = '#303F9F'

            style.configure('TLabel',
                            background=bg_color,
                            foreground='white')

            style.configure('TFrame',
                            background=bg_color)

            style.configure('Custom.TButton',
                            background=btn_color,
                            foreground='white',
                            borderwidth=1)

            style.map('Custom.TButton',
                      background=[('active', btn_active),
                                  ('pressed', btn_pressed)],
                      foreground=[('disabled', 'gray')])

            style.configure('TCheckbutton',
                            background=bg_color,
                            foreground='white')

            style.map('TCheckbutton',
                      background=[('active', bg_color)])

        except Exception as e:
            print(f"Theme configuration warning: {e}")

        self.root.configure(bg='#1A237E')

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(header_frame,
                                text="Mikro Entegrasyon",
                                font=('Segoe UI', 14, 'bold'))
        title_label.pack(side=tk.LEFT)

        self.status_label = ttk.Label(header_frame,
                                      text="● Durduruldu")
        self.status_label.pack(side=tk.RIGHT)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))

        self.start_stop_btn = ttk.Button(control_frame,
                                         text="Başlat",
                                         style="Custom.TButton",
                                         command=self._toggle_program)
        self.start_stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        dev_info = ttk.Label(control_frame,
                             text="Geliştirici: Halil Selim Tuna - hselimtuna@gmail.com - www.linkedin.com/in/hselimtuna")
        dev_info.pack(side=tk.RIGHT)

        self.log_viewer = LogViewer(main_frame, self.gui_handler)

    def _setup_gui_logging(self):
        logger = SingletonLogger.get_logger()
        formatter = logger.handlers[0].formatter if logger.handlers else None
        if formatter:
            self.gui_handler.setFormatter(formatter)
        logger.addHandler(self.gui_handler)

    def _toggle_program(self):
        if not self.is_running:
            self._start_program()
        else:
            self._stop_program()

    def _start_program(self):
        self.is_running = True
        self.start_stop_btn.config(text="Durdur")
        try:
            self.status_label.config(text="● Çalışıyor", foreground='#4CAF50')
        except:
            self.status_label.config(text="● Çalışıyor")

        self.run_thread = threading.Thread(target=self._run_program_loop, daemon=True)
        self.run_thread.start()

    def _stop_program(self):
        self.is_running = False
        self.start_stop_btn.config(text="Başlat")
        try:
            self.status_label.config(text="● Durduruldu", foreground='#F44336')
        except:
            self.status_label.config(text="● Durduruldu")

    def _run_program_loop(self):
        import time

        while self.is_running:
            try:
                Run().run_program()

                for _ in range(300):
                    if not self.is_running:
                        break
                    time.sleep(0.1)

            except Exception as e:
                from src.logger.custom_logger import SingletonLogger
                logger = SingletonLogger.get_logger()
                logger.error(f"Program çalışırken hata oluştu: {str(e)}")
                time.sleep(5)

    def _on_closing(self):
        self.is_running = False
        if self.log_viewer:
            self.log_viewer.stop_monitoring()
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
