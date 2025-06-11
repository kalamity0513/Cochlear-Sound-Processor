import tkinter as tk
from tkinter import filedialog
from tkinter import font
#from gui.custom_widgets import RoundedFrame
from tkinter import Frame
from processing.audio_loader import load_and_process_audio
from utils.plot_utils import plot_time_domain, plot_electrodogram
from utils.file_utils import load_icon, play_click, play_wav
from utils.constants import ICON_PATHS, ICON_SIZES, COLOR_SCHEME
import pygame
import os
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from processing.vocoder import vocoder  

WIDTH = 980
HEIGHT = 800

class CochlearImplantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cochlear Implant Sound Processor")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg=COLOR_SCHEME["background"])

        self.wav_file = None
        self.strategy = tk.StringVar(value='F0F1F2')
        self.time_canvas = None
        self.electrodogram_canvas = None
        self.vocoded_result = None

        pygame.init()
        pygame.mixer.init()
        self.click_sound = pygame.mixer.Sound("Final_Cochlear_Stimulator_Code/deep_click.wav")

        try:
            self.pixelfont = font.Font("pixelfont.ttf", size=12)
        except:
            self.pixelfont = font.Font(family="Courier", size=12, weight="bold")

        self.icons = {k: load_icon(ICON_PATHS[k], ICON_SIZES[k]) for k in ICON_PATHS}
        self.icon_big = {k: load_icon(ICON_PATHS[k], ICON_SIZES[k + "_big"]) for k in ICON_PATHS}

        self._build_gui()

    def _render_step1_upload(self, parent):
        tk.Label(parent, text="Step 1: Upload Your File",
            font=(self.pixelfont.actual("family"), 18, "bold"),
            bg=COLOR_SCHEME["background"], fg=COLOR_SCHEME["header"]).pack()

        self.filebox_btn = tk.Label(parent, image=self.icons["filebox"], bg=COLOR_SCHEME["background"])
        self.filebox_btn.pack()
        self.filebox_btn.bind("<Button-1>", lambda e: (self.load_file(), play_click(self.click_sound)))
        self.filebox_btn.bind("<Enter>", lambda e: self.filebox_btn.config(image=self.icon_big["filebox"]))
        self.filebox_btn.bind("<Leave>", lambda e: self.filebox_btn.config(image=self.icons["filebox"]))

        self.label = tk.Label(parent, text="No file selected", bg=COLOR_SCHEME["background"],
            fg="gray", font=self.pixelfont)
        self.label.pack()


    def _render_step2_strategy(self, parent):
        tk.Label(parent, text="Step 2: Choose Strategy",
            font=(self.pixelfont.actual("family"), 18, "bold"),
            bg=COLOR_SCHEME["background"], fg=COLOR_SCHEME["header"]).pack(pady=(20, 5))

        # Create a dedicated frame for radio buttons
        strategy_frame = tk.Frame(parent, bg=COLOR_SCHEME["background"])
        strategy_frame.pack(pady=5)

        for s in ['F0F1F2', 'ACE', 'CIS']:
            tk.Radiobutton(strategy_frame, text=s, variable=self.strategy, value=s,
                font=self.pixelfont, bg=COLOR_SCHEME["background"],
                fg=COLOR_SCHEME["radio"]).pack(side="left", padx=10)

    def _render_step3_processing(self, parent):
        tk.Label(parent, text="Step 3: Process and Play",
                font=(self.pixelfont.actual("family"), 18, "bold"),
                bg=COLOR_SCHEME["background"], fg=COLOR_SCHEME["header"]).pack(pady=(20, 5))

        self.run_btn = tk.Label(parent, image=self.icons["run"], bg=COLOR_SCHEME["background"])
        self.run_btn.pack(pady=5)
        self.run_btn.bind("<Button-1>", lambda e: (self.run_processing(), play_click(self.click_sound)))
        self.run_btn.bind("<Enter>", lambda e: self.run_btn.config(image=self.icon_big["run"]))
        self.run_btn.bind("<Leave>", lambda e: self.run_btn.config(image=self.icons["run"]))

        self.play_btn = tk.Label(parent, image=self.icons["play"], bg=COLOR_SCHEME["background"])
        self.play_btn.pack(pady=5)
        self.play_btn.bind("<Button-1>", lambda e: (play_wav(self.wav_file), play_click(self.click_sound)))
        self.play_btn.bind("<Enter>", lambda e: self.play_btn.config(image=self.icon_big["play"]))
        self.play_btn.bind("<Leave>", lambda e: self.play_btn.config(image=self.icons["play"]))
        
        # Play Result Icon Button
        self.play_result_btn = tk.Label(parent, image=self.icons["play_result"], bg=COLOR_SCHEME["background"])
        self.play_result_btn.pack(pady=5)
        self.play_result_btn.bind("<Button-1>", lambda e: (self.play_result(), play_click(self.click_sound)))
        self.play_result_btn.bind("<Enter>", lambda e: self.play_result_btn.config(image=self.icon_big["play_result"]))
        self.play_result_btn.bind("<Leave>", lambda e: self.play_result_btn.config(image=self.icons["play_result"]))

        # Save FTM Icon Button
        self.save_btn = tk.Label(parent, image=self.icons["save_ftm"], bg=COLOR_SCHEME["background"])
        self.save_btn.pack(pady=5)
        self.save_btn.bind("<Button-1>", lambda e: (self.save_ftm_to_csv(), play_click(self.click_sound)))
        self.save_btn.bind("<Enter>", lambda e: self.save_btn.config(image=self.icon_big["save_ftm"]))
        self.save_btn.bind("<Leave>", lambda e: self.save_btn.config(image=self.icons["save_ftm"]))


    def load_file(self):
        self.wav_file = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if self.wav_file:
            self.label.config(text=os.path.basename(self.wav_file), fg="black")

    def run_processing(self):
        if not self.wav_file:
            print("No WAV file selected!")
            return

        x, fs, ftm = load_and_process_audio(self.wav_file, self.strategy.get())
        # ftm = compress_ftm_dB(ftm)
        sample_length = 0.002  # 2 ms per column
        self.vocoded_result = vocoder(ftm, sample_length, fs)

        fig1 = plot_time_domain(x, fs)
        fig2 = plot_electrodogram(ftm, self.strategy.get())

        # save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        # if save_path:
        #     pd.DataFrame(ftm).to_csv(save_path, index=False, header=False)

        self._update_timeplot(fig1)
        self._update_electrodogram(fig2)
        
    
    def _build_gui(self):
        main_frame = tk.Frame(self.root, bg=COLOR_SCHEME["background"], width=WIDTH, height=HEIGHT)
        main_frame.pack(fill="both", expand=False)
        main_frame.pack_propagate(False)

        control_frame = tk.Frame(main_frame, bg=COLOR_SCHEME["background"], width=480, height=640)
        control_frame.pack_propagate(False)
        #control_frame.pack(side="left", fill="y", padx=30, pady=30)
        control_frame.pack(side="left", fill="y", padx=10, pady=30)

        self._render_step1_upload(control_frame)
        self._render_step2_strategy(control_frame)
        self._render_step3_processing(control_frame)
        
        self.plot_frame = tk.Frame(main_frame, bg=COLOR_SCHEME["background"], width=480, height=640)
        self.plot_frame.pack_propagate(False)
        #self.plot_frame.pack(side="right", fill="both", expand=True, padx=(10, 30), pady=30)
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=30)

        #self.plot_container_time = RoundedFrame(self.plot_frame, width=420, height=320, corner_radius=30, border_width=10)
        self.plot_container_time = Frame(self.plot_frame, width=420, height=320, bd=10)
        self.plot_container_time.pack(padx=15, pady=15)

        #self.plot_container_electro = RoundedFrame(self.plot_frame, width=420, height=320, corner_radius=30, border_width=10)
        self.plot_container_electro = Frame(self.plot_frame, width=420, height=320, bd=10)
        self.plot_container_electro.pack(padx=15, pady=15)


    def _update_timeplot(self, fig):
        if self.time_canvas:
            self.time_canvas.get_tk_widget().destroy()
            self.time_canvas.get_tk_widget().update_idletasks()
        self.time_canvas = FigureCanvasTkAgg(fig, master=self.plot_container_time)
        self.time_canvas.draw()
        self.time_canvas.get_tk_widget().pack(anchor="center", pady=10, padx=10)       
        
        
    def _update_electrodogram(self, fig):
        if self.electrodogram_canvas:
            self.electrodogram_canvas.get_tk_widget().destroy()
            self.electrodogram_canvas.get_tk_widget().update_idletasks()
        self.electrodogram_canvas = FigureCanvasTkAgg(fig, master=self.plot_container_electro)
        self.electrodogram_canvas.draw()
        self.electrodogram_canvas.get_tk_widget().pack(anchor="center", pady=10, padx=10) 
        
    def play_result(self):
        if self.vocoded_result is not None:
            try:
                import sounddevice as sd
                sd.stop()
                sd.play(self.vocoded_result, 16000)
            except Exception as e:
                print("Error playing vocoded sound:", e)
        else:
            print("No result to play yet. Run processing first.")
            
    def save_ftm_to_csv(self):
        if self.vocoded_result is None or not self.wav_file:
            print("No FTM to save. Run processing first.")
            return

        try:
            strategy = self.strategy.get()
            default_name = f"FTM_{strategy}.csv"

            save_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_name,
                title="Save Frequency-Time Matrix"
            )

            if save_path:
                _, _, ftm = load_and_process_audio(self.wav_file, strategy)
                pd.DataFrame(ftm).to_csv(save_path, index=False, header=False)
                messagebox.showinfo("Success", f"FTM saved successfully as:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save FTM.\n{str(e)}")
            print("Error saving FTM:", e)




            
