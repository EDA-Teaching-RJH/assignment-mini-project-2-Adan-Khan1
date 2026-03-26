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
        ctk.set_appearance_mode("dark")

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

        center_frame = ctk.CTkFrame(login_container, fg_color="transparent")
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

    # ---------------------------------------------------------
    # INTERACTIONS & LOGIC
    # ---------------------------------------------------------
    # FEATURE 4: Multi-threaded Execution Pipeline. Uses Python Native Threads to execute process_cohort() in the background without freezing the UI otherwise moving the window will buffer the process
    def handle_drop(self, event): 
        filepath = event.data
        if filepath.startswith('{') and filepath.endswith('}'):
            filepath = filepath[1:-1] # Remove Tkinter brackets 

        if filepath.lower().endswith('.json'):
            self.set_active_file(filepath)
        else:
            messagebox.showwarning("Invalid File", "Please drop a .json clinical dataset.")

    def select_file(self):
        filepath = filedialog.askopenfilename(title="Select Raw Data JSON", filetypes=[("JSON Files", "*.json")])
        if filepath:
            self.set_active_file(filepath)

    def set_active_file(self, filepath):
        self.input_filepath = filepath
        self.lbl_filename.configure(text=os.path.basename(filepath))

        self.dropzone.pack_forget()
        self.file_card.pack(fill="x", padx=20, pady=(0, 25))

        self.btn_run.configure(state="normal")
        self.lbl_status.configure(text="Ready to process cohort.", text_color=COLOR_ACCENT)

        self.reset_pipeline()

    def remove_file(self):
        self.input_filepath = None
        self.file_card.pack_forget()
        self.dropzone.pack(fill="x", padx=20, pady=(0, 25))


        self.btn_run.configure(state="disabled")
        self.lbl_status.configure(text="Awaiting dataset...", text_color=TEXT_MUTED)
        self.reset_pipeline()


    def reset_pipeline(self):
        self.btn_save.pack_forget()
        self.btn_run.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        self.processed_patients = []
        self.metrics = {"total": 0, "eligible": 0, "excluded": 0, "manual": 0}
        self.update_kpis()

    def update_kpis(self):
        self.kpi_total.configure(text=str(self.metrics["total"]))
        self.kpi_eligible.configure(text=str(self.metrics["eligible"]))
        self.kpi_excluded.configure(text=str(self.metrics["excluded"]))
        self.kpi_manual.configure(text=str(self.metrics["manual"]))

    def run_pipeline_thread(self):
        if not self.input_filepath: return
        self.btn_run.configure(state="disabled")
        self.lbl_status.configure(text="Engine parsing array through NLG Regex...", text_color=COLOR_ACCENT)
        threading.Thread(target=self.process_cohort, daemon=True).start()

    def process_cohort(self):
        try:
            with open(self.input_filepath, mode='r', encoding='utf-8') as infile:
                dataset = json.load(infile)
                total_records = len(dataset)

                for index, row in enumerate(dataset):
                    raw_text = row.get('patient', '')
                    pt_id = row.get('patient_uid', f"PMC_PT_{index+1}")

                    if not raw_text: continue

                    self.metrics["total"] += 1
                    patient = UrologyPatient(patient_id=pt_id, raw_text=raw_text)
                    patient.evaluate_eligibility()
                    if "Eligible" in patient.status:
                        self.metrics["eligible"] += 1
                    elif "Ineligible" in patient.status:
                        self.metrics["excluded"] += 1
                    else:
                        self.metrics["manual"] += 1

                    self.processed_patients.append({
                        "Patient_ID": patient.patient_id,
                        "Age": patient.age,
                        "Gleason_Score": patient.gleason,
                        "PSA_Level": patient.psa,
                        "T_Stage": patient.t_stage,
                        "Prostate_Volume_cc": patient.prostate_volume,
                        "Eligibility_Status": patient.status,
                        "Clinical_Rationale": patient.reason
                    })

                    if index % 500 == 0:
                        progress = index / max(1, total_records)
                        self.after(0, self.progress_bar.set, progress)
                        self.after(0, self.update_kpis)

            self.after(0, self.progress_bar.set, 1.0)
            self.after(0, self.update_kpis)
            self.after(0, self.lbl_status.configure, {"text": "Pipeline Complete. Audit trail generated.", "text_color": COLOR_SUCCESS})
            self.after(0, self.show_save_button)


        except Exception as e:
            self.after(0, self.lbl_status.configure, {"text": f"Critical Error: {str(e)}", "text_color": COLOR_DANGER})
            self.after(0, self.btn_run.configure, {"state": "normal"})


    # FEATURE 5: The Selective CSV Audit Trail Exporter. This allows the user to only download specific eligibilities
    def show_save_button(self):
        self.btn_run.pack_forget()
        self.btn_save.pack(fill="x", pady=(10, 0))

    def open_export_dialog(self):
        if not self.processed_patients: 
            messagebox.showerror("Error", "No processed data to save.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Export Options")

        dialog_w = 450
        dialog_h = 350

        # Center relative to the main application window
        self.update_idletasks()
        main_x = self.winfo_rootx()
        main_y = self.winfo_rooty()
        main_w = self.winfo_width()
        main_h = self.winfo_height()
        x = main_x + (main_w // 2) - (dialog_w // 2)
        y = main_y + (main_h // 2) - (dialog_h // 2)

        dialog.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")
        dialog.minsize(dialog_w, dialog_h)
        dialog.configure(fg_color=BG_CARD)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Select Export Categories", font=("Helvetica", 18, "bold"), text_color=TEXT_PRIMARY).pack(pady=(25, 20))

        var_eligible = ctk.BooleanVar(value=True)
        var_excluded = ctk.BooleanVar(value=False)
        var_manual = ctk.BooleanVar(value=True)

        chk_eligible = ctk.CTkCheckBox(dialog, text="Eligible Patients (CPG 2-5)", variable=var_eligible, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS, text_color=TEXT_PRIMARY, font=("Helvetica", 14))
        chk_eligible.pack(anchor="w", padx=50, pady=10)

        chk_excluded = ctk.CTkCheckBox(dialog, text="Excluded Patients (Irrelevant/CPG 1)", variable=var_excluded, fg_color=COLOR_WARN, hover_color=COLOR_WARN, text_color=TEXT_PRIMARY, font=("Helvetica", 14))
        chk_excluded.pack(anchor="w", padx=50, pady=10)

        chk_manual = ctk.CTkCheckBox(dialog, text="Manual Review Patients", variable=var_manual, fg_color=COLOR_DANGER, hover_color=COLOR_DANGER, text_color=TEXT_PRIMARY, font=("Helvetica", 14))
        chk_manual.pack(anchor="w", padx=50, pady=10)

        def confirm_export():
            self.save_csv_filtered(
                export_eligible=var_eligible.get(),
                export_excluded=var_excluded.get(),
                export_manual=var_manual.get()
            )
            dialog.destroy()

        btn_confirm = ctk.CTkButton(dialog, text="Export CSV to System", command=confirm_export, height=45, fg_color=COLOR_ACCENT, hover_color="#4281FF", font=("Helvetica", 14, "bold"))
        btn_confirm.pack(fill="x", padx=50, pady=(30, 20))

    def save_csv_filtered(self, export_eligible, export_excluded, export_manual):
        output_filepath = filedialog.asksaveasfilename(
            title="Save Audit Trail As", 
            defaultextension=".csv", 
            filetypes=[("CSV Files", "*.csv")],
            initialfile="Eligibill_Cohort_Audit_Trail.csv"
        )
        if not output_filepath: return 

        filtered_patients = []
        for p in self.processed_patients:
            status = p["Eligibility_Status"]
            if "Eligible" in status and export_eligible:
                filtered_patients.append(p)
            elif "Ineligible" in status and export_excluded:
                filtered_patients.append(p)
            elif "Manual" in status and export_manual:
                filtered_patients.append(p)

        if not filtered_patients:
            messagebox.showinfo("Export Empty", "No records matched your selected criteria.")
            return

        try:
            with open(output_filepath, mode='w', encoding='utf-8', newline='') as outfile:
                fieldnames = ["Patient_ID", "Age", "Gleason_Score", "PSA_Level", "T_Stage", "Prostate_Volume_cc", "Eligibility_Status", "Clinical_Rationale"]
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(filtered_patients)

            self.lbl_status.configure(text=f"Saved successfully: {os.path.basename(output_filepath)}", text_color=COLOR_SUCCESS)
            messagebox.showinfo("Export Successful", f"Audit trail successfully exported to:\n\n{output_filepath}\n\nExported {len(filtered_patients)} records.")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save CSV: {str(e)}")

if __name__ == "__main__":
    app = EligibillApp()
    app.mainloop()