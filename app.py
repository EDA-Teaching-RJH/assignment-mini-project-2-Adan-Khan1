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

    # ---------------------------------------------------------
    # LOGIN SCREEN
    # ---------------------------------------------------------
    def build_login_screen(self): 
        login_container = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self.frames["login"] = login_container

        center_frame = ctk.CTkFrame(login_containier, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        #Header 
        ctk.CTkLabel(center_frame, text="Eligibill", font=("Helvetica", 42, "bold"), text_color=TEXT_PRIMARY).pack()
        ctk.CTkLabel(center_frame, text="ONCOLOGY TRIAL SCREENER • RESTRICTED ACCESS", font=("Helvetica", 12, "bold"), text_color=TEXT_MUTED).pack(pady=(5, 30))

        # Box
        box = ctk.CTkFrame(center_frame, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
        box.pack(padx=20, pady=20, fill="both", expand=True)

        box_inner = ctk.CTkFrame(box, fg_color="transparent")
        box_inner.pack(padx=40, pady=40)

        ctk.CTkLabel(box_inner, text="System Authentication", font=("Helvetica", 18, "bold"), text_color=TEXT_PRIMARY).pack(pady=(0, 25))

        # Inputs 
        ctk.CTkLabel(box_inner, text="Clinical Email Address", font=("Helvetica", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w")
        self.entry_email = ctk.CTkEntry(box_inner, width=300, height=45, placeholder_text="doctor@nhs.net", fg_color=BG_DROP, border_color=BORDER)
        self.entry_email.pack(pady=(5, 15))

        ctk.CTkLabel(box_inner, text="Password", font=("Helvetica", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w")
        self.entry_pass = ctk.CTkEntry(box_inner, width=300, height=45, show="*", fg_color=BG_DROP, border_color=BORDER)
        self.entry_pass.pack(pady=(5, 5))

        self.lbl_login_error = ctk.CTkLabel(box_inner, text="", text_color=COLOR_DANGER, font=("Helvetica", 12))
        self.lbl_login_error.pack(pady=(0, 15))

        btn_login = ctk.CTkButton(box_inner, text="Secure Login", height=45, fg_color=COLOR_ACCENT, hover_color="#4281FF", font=("Helvetica", 14, "bold"), command=self.verify_login)
        btn_login.pack(fill="x", pady=(0, 10))

        btn_smartcard = ctk.CTkButton(box_inner, text="Authenticate via Smartcard", height=40, fg_color="transparent", border_width=1, border_color=BORDER, text_color=TEXT_MUTED, hover_color=BORDER, command=lambda: self.lbl_login_error.configure(text="Hardware Error: Smartcard reader not detected.", text_color=COLOR_WARN))
        btn_smartcard.pack(fill="x")

        self.entry_pass.bind("<Return>", lambda e: self.verify_login())
        self.entry_email.bind("<Return>", lambda e: self.verify_login())
    
    def verify_login(self): 
        email = self.entry_email.get().strip().lower()
        password = self.entry_pass.get()

        if not email.endswith("@nhs.net"):
            self.lbl_login_error.configure(text="Unauthorised domain. NHS @nhs.net credentials required.")
            return
        
        if email == "admin@nhs.net" and password == "admin123": 
            self.lbl_login_error.configure(text="") 
            self.show_frame("dashboard")
            self.entry_pass.delete(0, 'end')
        else: 
            self.lbl_login_error.configure(text="Invalid credentials. Please try again.")

            