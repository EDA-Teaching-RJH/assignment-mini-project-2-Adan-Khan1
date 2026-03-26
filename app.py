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

        if not email.endswith("@nhs.net"):  # Gives the authentic feel that a clinician is using the application
            self.lbl_login_error.configure(text="Unauthorised domain. NHS @nhs.net credentials required.")
            return
        
        if email == "admin@nhs.net" and password == "admin123": # Ease of use as an "admin" is testing the prototype version to see if the app is good enough for their trust
            self.lbl_login_error.configure(text="") 
            self.show_frame("dashboard")
            self.entry_pass.delete(0, 'end')
        else: 
            self.lbl_login_error.configure(text="Invalid credentials. Please try again.")


    # ---------------------------------------------------------
    # DASHBOARD SCREEN
    # ---------------------------------------------------------
    # FEATURE 3: The Dashboard creates visually appealing KPI cards and hooks up the Drag & Drop framework into the visual Dropzone

    def build_dashboard(self): 
        dash_container = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.frames["dashboard"] = dash_container

        # Header
        header = ctk.CTkFrame(dash_container, fg_color="transparent")
        header = ctk.CTkFrame(dash_container, fg_color="transparent")

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Eligibill Pipeline", font=("Helvetica", 28, "bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_box, text="● System Online & Connected", font=("Helvetica", 12, "bold"), text_color=COLOR_SUCCESS).pack(anchor="w")

        btn_logout = ctk.CTkButton(header, text="Logout", width=80, height=35, fg_color="transparent", border_width=1, border_color=BORDER, hover_color=BORDER, command=lambda: self.show_frame("login"))
        btn_logout.pack(side="right")

        # Stage 1: Ingestion
        ing_panel = ctk.CTkFrame(dash_container, fg_color=BG_CARD, corner_radius=12, border_color=BORDER, border_width=1)
        ing_panel.pack(fill="x", padx=40, pady=(0, 20))

        ing_head = ctk.CTkFrame(ing_panel, fg_color="transparent")
        ing_head.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(ing_head, text="01", font=("Courier", 14, "bold"), fg_color=BORDER, text_color=TEXT_MUTED, corner_radius=6, width=28, height=24).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(ing_head, text="Data Ingestion", font=("Helvetica", 16, "bold"), text_color=TEXT_PRIMARY).pack(side="left")


        # Dropzone for the drag and drop function 
        self.dropzone = ctk.CTkFrame(ing_panel, fg_color=BG_DROP, corner_radius=8, border_width=1, border_color=BORDER)
        self.dropzone.pack(fill="x", padx=20, pady=(0, 25))

        self.lbl_drop_text = ctk.CTkLabel(self.dropzone, text="Click to browse or Drag & drop .json dataset here", font=("Helvetica", 14), text_color=TEXT_MUTED)
        self.lbl_drop_text.pack(pady=30)

        # Clicking the dropzone opens file dialog, since it gives the user flexibility to do whichever method they prefer
        self.lbl_drop_text.bind("<Button-1>", lambda e: self.select_file())
        self.dropzone.bind("<Button-1>", lambda e: self.select_file())

        # Bind Drag & Drop natively
        self.dropzone.drop_target_register(DND_FILES)
        self.dropzone.dnd_bind('<<Drop>>', self.handle_drop)


        # File Selected Card (Hidden initially)
        self.file_card = ctk.CTkFrame(ing_panel, fg_color=BG_DROP, corner_radius=8, border_width=1, border_color=BORDER)
        
        self.lbl_filename = ctk.CTkLabel(self.file_card, text="dataset.json", font=("Helvetica", 14, "bold"), text_color=TEXT_PRIMARY)
        self.lbl_filename.pack(side="left", padx=20, pady=15)

        btn_remove = ctk.CTkButton(self.file_card, text="✕", width=30, height=30, fg_color="transparent", hover_color=BORDER, command=self.remove_file)
        btn_remove.pack(side="right", padx=10)

        # KPIs
        self.kpi_frame = ctk.CTkFrame(dash_container, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=40, pady=(0, 20))
        self.kpi_frame.grid_columnconfigure((0,1,2,3), weight=1)

        def create_kpi(parent, title, text_color, col):
            card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12, border_color=BORDER, border_width=1, height=120)
            card.grid(row=0, column=col, padx=(0 if col==0 else 10, 0 if col==3 else 10), sticky="ew")
            card.pack_propagate(False)

            ctk.CTkLabel(card, text=title, font=("Helvetica", 12, "bold"), text_color=TEXT_MUTED).pack(pady=(20, 5))
            val = ctk.CTkLabel(card, text="0", font=("Courier", 38, "bold"), text_color=text_color)
            val.pack()
            return val

        self.kpi_total = create_kpi(self.kpi_frame, "Total Processed", TEXT_PRIMARY, 0)
        self.kpi_eligible = create_kpi(self.kpi_frame, "Eligible (CPG 2-5)", COLOR_SUCCESS, 1)
        self.kpi_excluded = create_kpi(self.kpi_frame, "Excluded", COLOR_WARN, 2)
        self.kpi_manual = create_kpi(self.kpi_frame, "Manual Review", COLOR_DANGER, 3)

        # Stage 2: Execution
        exec_panel = ctk.CTkFrame(dash_container, fg_color=BG_CARD, corner_radius=12, border_color=BORDER, border_width=1)
        exec_panel.pack(fill="x", padx=40, pady=0)

        ex_head = ctk.CTkFrame(exec_panel, fg_color="transparent")
        ex_head.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(ex_head, text="02", font=("Courier", 14, "bold"), fg_color=BORDER, text_color=TEXT_MUTED, corner_radius=6, width=28, height=24).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(ex_head, text="Pipeline Execution", font=("Helvetica", 16, "bold"), text_color=TEXT_PRIMARY).pack(side="left")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(exec_panel, progress_color=COLOR_ACCENT, fg_color=BG_DROP, height=10, corner_radius=5)
        self.progress_bar.pack(fill="x", padx=20, pady=(10, 5))
        self.progress_bar.set(0)

        self.lbl_status = ctk.CTkLabel(exec_panel, text="Awaiting dataset...", font=("Helvetica", 13), text_color=TEXT_MUTED)
        self.lbl_status.pack(anchor="w", padx=20, pady=(0, 20))


        # Buttons
        self.btn_run = ctk.CTkButton(
            exec_panel, text="Initialise Screening", command=self.run_pipeline_thread,
            height=45, state="disabled", fg_color=COLOR_ACCENT, hover_color="#4281FF",
            font=("Helvetica", 15, "bold"), corner_radius=8
        )
        self.btn_run.pack(fill="x", pady=(0, 10))

        self.btn_save = ctk.CTkButton(
            exec_panel, 
            text="Download Audit Trail", 
            command=self.open_export_dialog,
            height=50,
            fg_color=COLOR_SUCCESS, hover_color="#4AC75B", text_color=BG_MAIN,
            font=("Helvetica", 16, "bold"), corner_radius=8
        )
