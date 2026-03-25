import os
import json 
import csv 
import threading 
import customtkinter as ctk 
from tkinter import filedialog, messagebox 
try: 
    from tkinterdnd2 import tkinterDnD, DND_FILES
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
