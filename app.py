import os
import json 
import csv 
import threading 
import customtkinter as ctk 
from tkinter import filedialog, messagebox 
try: 
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError: 
    messagebox.showerror("Missing Dependency", "Please run: pip install tkinterdnd2") # need to pip install tkinterdnd2 and customtkinter. Since these are custom libraries and github do not support the GUI for it, these will be manually shown during the video on local computer
    exit()
from clinical_engine import UrologyPatient 

# Colour Palette for the GUI 
BG_MAIN = "#0B0D11"
BG_CARD = "#1A1D24"
BG_DROP = "#13161A"
BORDER = "#2E3641"
TEXT_PRIMARY = "#F0F6FC"
TEXT_MUTED = "#8B949E"

COLOR_ACCENT = "#2E71FA"
COLOR_SUCCESS = "#3FB950"
COLOR_WARN = "#D29922"
COLOR_DANGER = "#F85149"

# Base wrappe to enable native drag and drop on customTkinter since drag and drop functionality is better UX
class TkinterDnD_CTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):  # *args is used for the position arguments while **kwargs is used for the keyword arugment for the DnD feature
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class EligibillApp(TkinterDnD_CTk):
    def __init__(self): 
        super().__init__()

        self.title("Eligibill Pipeline")
        self.geometry("1000x800")
        self.minsize(900,700)
        self.configure(fg_color=BG_MAIN)
        ctk.set_appearance_model("dark")

        self.input_filepath = None
        self.processed_patients = []
        self.metrics = {"total": 0, "excluded": 0, "manual": 0}
        self.frames = {}

        self.build_login_screen() 
        self.build_dashboard()

        self.show_frame("login")

    def show_frame(self, name): 
        for frame in self.frames.values(): 
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

