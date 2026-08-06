import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk
from tkcalendar import DateEntry
from PIL import Image, ImageTk, Image as PILImage

# ReportLab Imports for PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


class RegistroApp(ThemedTk):
    def __init__(self):
        super().__init__(theme="radiance")
        self.title("LabSuite Laboratorio de Unidad Metabólica")
        self.geometry("750x600")

        # Set window icon using mini_LOGO.png
        self.set_window_icon("mini_LOGO.png")

        self.csv_filename = "Registro_LUM.csv"
        self.editing_row_index = None  # Tracks if we are editing an existing record
        self.init_csv()

        # Dictionary to store field variables for Tab 1
        self.vars = {}

        # Dictionary & Variables to store fields for Tab 3 (Pathology Report)
        self.report_entries = {}
        self.spectrum_img_path = tk.StringVar()
        self.spectrum_desc = tk.StringVar()
        self.stone_img_paths = [tk.StringVar() for _ in range(4)]
        self.stone_descs = [tk.StringVar() for _ in range(4)]

        # Top Branding Frame
        self.build_header()

        # Main Tab Control (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Entry Form
        self.tab_entry = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_entry, text=" Formulario de Registro ")

        # Tab 2: Record Viewer / Search
        self.tab_viewer = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_viewer, text=" Consulta y Edición de Registros ")

        # Tab 3: Pathology Report Generator (Integrated from A1.0.py)
        self.tab_report = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_report, text=" Generador de Reporte PDF ")

        # Build UI Elements for all Tabs
        self.build_form_tab()
        self.build_viewer_tab()
        self.build_report_tab()

    def build_header(self):
        """Creates top bar with title on the left and logo on the upper-right."""
        header_frame = ttk.Frame(self, padding="5 5 10 5")
        header_frame.pack(side=tk.TOP, fill=tk.X)

        # Header Title
        title_label = ttk.Label(
            header_frame, 
            text="Análisis Morfo-Constitucional de Cálculo Renal", 
            font=("Arial", 12, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Upper-Right Logo
        logo_path = "logofull2.png"
        if os.path.exists(logo_path):
            try:
                img = PILImage.open(logo_path)
                img.thumbnail((250, 100), PILImage.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)

                logo_label = ttk.Label(header_frame, image=self.logo_img)
                logo_label.pack(side=tk.RIGHT, padx=5)
            except Exception as e:
                print(f"Advertencia: No se pudo cargar el logo de branding: {e}")

    def set_window_icon(self, icon_path):
        """Sets the window title bar icon safely."""
        try:
            if os.path.exists(icon_path):
                self.icon_image = tk.PhotoImage(file=icon_path)
                self.iconphoto(False, self.icon_image)
        except Exception as e:
            print(f"Advertencia: No se pudo cargar el icono '{icon_path}': {e}")

    def init_csv(self):
        """Initializes the CSV file with headers if it doesn't exist."""
        self.headers = [
            # Identificación
            "Fecha_Recepcion", "Folio_Interno", "NSS", "Nombre", "Apellido_Paterno", "Apellido_Materno",
            "Sexo", "Edad", "Unidad_Servicio", "Medico",
            # Muestra
            "Fecha_Recoleccion", "Metodo", "Localizacion", "Lado", "Fragmentado", "Observaciones",
            # Metabolicos
            "pH", "Urocultivo", "Microorganismo",
            "Orina_Glucosa", "Orina_Creatinina", "Orina_AcidoUrico", "Orina_Na", "Orina_K",
            "Orina_Cl", "Orina_Ca", "Orina_P", "Orina_Mg", "Orina_Citrato", "Orina_Oxalato",
            "Suero_Glucosa", "Suero_Creatinina", "Suero_AcidoUrico", "Suero_Na", "Suero_K",
            "Suero_Cl", "Suero_Ca", "Suero_P", "Suero_Mg",
            # Poblacionales
            "Entidad_Federativa", "Municipio_Alcaldia", "CP", "Ocupacion", "Zona", "Evento",
            "No_Recurrencia", "Historia_Familiar", "IVU_Reciente", "Comorbilidades",
            # Analista
            "Iniciales_Analista"
        ]
        
        if not os.path.exists(self.csv_filename):
            with open(self.csv_filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)

    # ---------------- TAB 1: FORM BUILDER ----------------

    def build_form_tab(self):
        main_frame = ttk.Frame(self.tab_entry)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, padding="15")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Build Sections
        self.build_identificacion_section()
        self.build_muestra_section()
        self.build_metabolicos_section()
        self.build_poblacionales_section()
        self.build_analista_section()
        self.build_action_buttons()

    def build_identificacion_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Identificación y Trazabilidad", padding="10")
        frame.pack(fill=tk.X, pady=5)

        self.vars["Fecha_Recepcion"] = tk.StringVar()
        ttk.Label(frame, text="Fecha de recepción:").grid(row=0, column=0, sticky="w", pady=2)
        DateEntry(frame, textvariable=self.vars["Fecha_Recepcion"], date_pattern="yyyy-mm-dd").grid(row=0, column=1, sticky="w", pady=2)

        fields = [
            ("Folio interno:", "Folio_Interno"),
            ("NSS:", "NSS"),
            ("Nombre:", "Nombre"),
            ("Apellido paterno:", "Apellido_Paterno"),
            ("Apellido materno:", "Apellido_Materno"),
            ("Edad (años):", "Edad"),
            ("Unidad/Servicio:", "Unidad_Servicio"),
            ("Médico:", "Medico")
        ]

        row = 1
        for label, var_key in fields:
            self.vars[var_key] = tk.StringVar()
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(frame, textvariable=self.vars[var_key], width=30).grid(row=row, column=1, sticky="w", pady=2)
            row += 1

        self.vars["Sexo"] = tk.StringVar(value="M")
        ttk.Label(frame, text="Sexo:").grid(row=row, column=0, sticky="w", pady=2)
        sex_frame = ttk.Frame(frame)
        sex_frame.grid(row=row, column=1, sticky="w", pady=2)
        ttk.Radiobutton(sex_frame, text="M", variable=self.vars["Sexo"], value="M").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sex_frame, text="F", variable=self.vars["Sexo"], value="F").pack(side=tk.LEFT, padx=5)

    def build_muestra_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Obtención, Localización y Estado de la Muestra", padding="10")
        frame.pack(fill=tk.X, pady=5)

        self.vars["Fecha_Recoleccion"] = tk.StringVar()
        ttk.Label(frame, text="Fecha de recolección:").grid(row=0, column=0, sticky="w", pady=2)
        DateEntry(frame, textvariable=self.vars["Fecha_Recoleccion"], date_pattern="yyyy-mm-dd").grid(row=0, column=1, sticky="w", pady=2)

        self.vars["Metodo"] = tk.StringVar()
        ttk.Label(frame, text="Método:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Combobox(frame, textvariable=self.vars["Metodo"], values=["Espontánea", "Cirugía", "Ureteroscopía", "Litotricia", "NLP"], state="readonly", width=27).grid(row=1, column=1, sticky="w", pady=2)

        self.vars["Localizacion"] = tk.StringVar()
        ttk.Label(frame, text="Localización:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Combobox(frame, textvariable=self.vars["Localizacion"], values=["Riñón", "Uréter", "Vejiga", "Uretra"], state="readonly", width=27).grid(row=2, column=1, sticky="w", pady=2)

        self.vars["Lado"] = tk.StringVar(value="Derecho")
        ttk.Label(frame, text="Lado:").grid(row=3, column=0, sticky="w", pady=2)
        lado_frame = ttk.Frame(frame)
        lado_frame.grid(row=3, column=1, sticky="w", pady=2)
        for val in ["Derecho", "Izquierdo", "Bilateral"]:
            ttk.Radiobutton(lado_frame, text=val, variable=self.vars["Lado"], value=val).pack(side=tk.LEFT, padx=3)

        self.vars["Fragmentado"] = tk.StringVar(value="No")
        ttk.Label(frame, text="Fragmentado:").grid(row=4, column=0, sticky="w", pady=2)
        frag_frame = ttk.Frame(frame)
        frag_frame.grid(row=4, column=1, sticky="w", pady=2)
        ttk.Radiobutton(frag_frame, text="Si", variable=self.vars["Fragmentado"], value="Si").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frag_frame, text="No", variable=self.vars["Fragmentado"], value="No").pack(side=tk.LEFT, padx=5)

        self.vars["Observaciones"] = tk.StringVar()
        ttk.Label(frame, text="Observaciones:").grid(row=5, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=self.vars["Observaciones"], width=40).grid(row=5, column=1, sticky="w", pady=2)

    def build_metabolicos_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Estudios Metabólicos", padding="10")
        frame.pack(fill=tk.X, pady=5)

        self.vars["pH"] = tk.StringVar()
        ttk.Label(frame, text="pH:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=self.vars["pH"], width=15).grid(row=0, column=1, sticky="w", pady=2)

        self.vars["Urocultivo"] = tk.StringVar(value="No realizado")
        ttk.Label(frame, text="Urocultivo:").grid(row=1, column=0, sticky="w", pady=2)
        uro_frame = ttk.Frame(frame)
        uro_frame.grid(row=1, column=1, sticky="w", pady=2)
        for val in ["Positivo", "Negativo", "No realizado"]:
            ttk.Radiobutton(uro_frame, text=val, variable=self.vars["Urocultivo"], value=val).pack(side=tk.LEFT, padx=3)

        self.vars["Microorganismo"] = tk.StringVar()
        ttk.Label(frame, text="Microorganismo:").grid(row=2, column=0, sticky="w", pady=2)
        micro_list = [
            "Escherichia coli", "Klebsiella pneumoniae", "Klebsiella sp", "Proteus mirabilis", 
            "Proteus sp", "Pseudomonas aeruginosa", "Enterobacter sp", "Citrobacter sp", 
            "Morganella morganii", "Enterococcus faecalis", "Enterococcus faecium", 
            "Staphylococcus saprophyticus", "Staphylococcus epidermidis", "Streptococcus", "Candida sp"
        ]
        ttk.Combobox(frame, textvariable=self.vars["Microorganismo"], values=micro_list, width=30).grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(frame, text="Análisis Orina", font=('Helvetica', 9, 'bold')).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 2))
        orina_fields = [
            ("Glucosa:", "Orina_Glucosa"), ("Creatinina:", "Orina_Creatinina"), ("Ácido úrico:", "Orina_AcidoUrico"),
            ("Na (sodio):", "Orina_Na"), ("K (potasio):", "Orina_K"), ("Cl (cloro):", "Orina_Cl"),
            ("Ca (calcio):", "Orina_Ca"), ("P (fósforo):", "Orina_P"), ("Mg (magnesio):", "Orina_Mg"),
            ("Citrato:", "Orina_Citrato"), ("Oxalato:", "Orina_Oxalato")
        ]
        r = 4
        for label, var_key in orina_fields:
            self.vars[var_key] = tk.StringVar()
            ttk.Label(frame, text=label).grid(row=r, column=0, sticky="w", pady=1)
            ttk.Entry(frame, textvariable=self.vars[var_key], width=15).grid(row=r, column=1, sticky="w", pady=1)
            r += 1

        ttk.Label(frame, text="Análisis Suero", font=('Helvetica', 9, 'bold')).grid(row=r, column=0, columnspan=2, sticky="w", pady=(10, 2))
        r += 1
        suero_fields = [
            ("Glucosa:", "Suero_Glucosa"), ("Creatinina:", "Suero_Creatinina"), ("Ácido úrico:", "Suero_AcidoUrico"),
            ("Na (sodio):", "Suero_Na"), ("K (potasio):", "Suero_K"), ("Cl (cloro):", "Suero_Cl"),
            ("Ca (calcio):", "Suero_Ca"), ("P (fósforo):", "Suero_P"), ("Mg (magnesio):", "Suero_Mg")
        ]
        for label, var_key in suero_fields:
            self.vars[var_key] = tk.StringVar()
            ttk.Label(frame, text=label).grid(row=r, column=0, sticky="w", pady=1)
            ttk.Entry(frame, textvariable=self.vars[var_key], width=15).grid(row=r, column=1, sticky="w", pady=1)
            r += 1

    def build_poblacionales_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Variables Poblacionales", padding="10")
        frame.pack(fill=tk.X, pady=5)

        self.vars["Entidad_Federativa"] = tk.StringVar()
        ttk.Label(frame, text="Entidad Federativa:").grid(row=0, column=0, sticky="w", pady=2)
        entidades = [
            "AGS", "BC", "BCS", "CAMP", "CHIH", "CHIS", "COAH", "COL", "CDMX", "DGO", "GTO", 
            "GRO", "HGO", "JAL", "MEX", "MICH", "MOR", "NAY", "NL", "OAX", "PUE", "QRO", 
            "Q.ROO", "SLP", "SIN", "SON", "TAB", "TAMPS", "TLAX", "VER", "YUC", "ZAC"
        ]
        ttk.Combobox(frame, textvariable=self.vars["Entidad_Federativa"], values=entidades, state="readonly", width=15).grid(row=0, column=1, sticky="w", pady=2)

        simple_fields = [("Municipio/Alcaldía:", "Municipio_Alcaldia"), ("C.P.:", "CP"), ("Ocupación:", "Ocupacion")]
        r = 1
        for label, key in simple_fields:
            self.vars[key] = tk.StringVar()
            ttk.Label(frame, text=label).grid(row=r, column=0, sticky="w", pady=2)
            ttk.Entry(frame, textvariable=self.vars[key], width=25).grid(row=r, column=1, sticky="w", pady=2)
            r += 1

        self.vars["Zona"] = tk.StringVar(value="Urbano")
        ttk.Label(frame, text="Zona:").grid(row=r, column=0, sticky="w", pady=2)
        z_frame = ttk.Frame(frame)
        z_frame.grid(row=r, column=1, sticky="w", pady=2)
        ttk.Radiobutton(z_frame, text="Urbano", variable=self.vars["Zona"], value="Urbano").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(z_frame, text="Rural", variable=self.vars["Zona"], value="Rural").pack(side=tk.LEFT, padx=5)
        r += 1

        self.vars["Evento"] = tk.StringVar(value="1er Evento")
        ttk.Label(frame, text="Evento:").grid(row=r, column=0, sticky="w", pady=2)
        e_frame = ttk.Frame(frame)
        e_frame.grid(row=r, column=1, sticky="w", pady=2)
        ttk.Radiobutton(e_frame, text="1er Evento", variable=self.vars["Evento"], value="1er Evento").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(e_frame, text="Recurrencia", variable=self.vars["Evento"], value="Recurrencia").pack(side=tk.LEFT, padx=5)
        r += 1

        self.vars["No_Recurrencia"] = tk.StringVar()
        ttk.Label(frame, text="No. Recurrencia:").grid(row=r, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=self.vars["No_Recurrencia"], width=25).grid(row=r, column=1, sticky="w", pady=2)
        r += 1

        other_radios = [("Historia familiar:", "Historia_Familiar"), ("IVU reciente:", "IVU_Reciente")]
        for label, key in other_radios:
            self.vars[key] = tk.StringVar(value="No")
            ttk.Label(frame, text=label).grid(row=r, column=0, sticky="w", pady=2)
            r_frame = ttk.Frame(frame)
            r_frame.grid(row=r, column=1, sticky="w", pady=2)
            ttk.Radiobutton(r_frame, text="Si", variable=self.vars[key], value="Si").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(r_frame, text="No", variable=self.vars[key], value="No").pack(side=tk.LEFT, padx=5)
            r += 1

        ttk.Label(frame, text="Comorbilidades:").grid(row=r, column=0, sticky="nw", pady=5)
        comorb_frame = ttk.Frame(frame)
        comorb_frame.grid(row=r, column=1, sticky="w", pady=5)

        self.comorbilidades_vars = {}
        comorbilidades_list = ["DM", "HAS", "OBESIDAD", "SM", "GOTA", "HIPERGLUCEMIA", "ERC", "CIRUGIA BARIATRICA", "MALABSORCION"]
        
        c_row, c_col = 0, 0
        for item in comorbilidades_list:
            var = tk.BooleanVar()
            self.comorbilidades_vars[item] = var
            ttk.Checkbutton(comorb_frame, text=item, variable=var).grid(row=c_row, column=c_col, sticky="w", padx=3, pady=2)
            c_col += 1
            if c_col > 2:
                c_col = 0
                c_row += 1

        self.vars["Comorbilidad_Otros"] = tk.StringVar()
        ttk.Label(comorb_frame, text="OTROS:").grid(row=c_row+1, column=0, sticky="w", pady=2)
        ttk.Entry(comorb_frame, textvariable=self.vars["Comorbilidad_Otros"], width=20).grid(row=c_row+1, column=1, columnspan=2, sticky="w", pady=2)

    def build_analista_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Analista/Capturista", padding="10")
        frame.pack(fill=tk.X, pady=5)

        self.vars["Iniciales_Analista"] = tk.StringVar()
        ttk.Label(frame, text="Iniciales:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=self.vars["Iniciales_Analista"], width=15).grid(row=0, column=1, sticky="w", pady=2)

    def build_action_buttons(self):
        btn_frame = ttk.Frame(self.scrollable_frame, padding="15")
        btn_frame.pack(fill=tk.X, pady=10)

        btn_limpiar = ttk.Button(btn_frame, text="Limpiar", command=self.clear_fields)
        btn_limpiar.pack(side=tk.LEFT, padx=20, expand=True)

        self.btn_registro = ttk.Button(btn_frame, text="Registro", command=self.save_data)
        self.btn_registro.pack(side=tk.RIGHT, padx=20, expand=True)

    # ---------------- TAB 2: VIEWER / EDIT MODULE ----------------

    def build_viewer_tab(self):
        # Search Bar Section
        search_frame = ttk.LabelFrame(self.tab_viewer, text="Buscar Registros", padding="10")
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text="Buscar (Folio / NSS / Nombre):").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_treeview())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Button(search_frame, text="Actualizar Tabla", command=self.refresh_treeview).pack(side=tk.RIGHT, padx=5)

        # Treeview Section
        tree_frame = ttk.Frame(self.tab_viewer, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Main display columns
        self.tree_columns = ("Folio_Interno", "Fecha_Recepcion", "NSS", "Nombre", "Apellido_Paterno", "Sexo", "Edad", "Medico")
        self.tree = ttk.Treeview(tree_frame, columns=self.tree_columns, show="headings")

        for col in self.tree_columns:
            self.tree.heading(col, text=col.replace("_", " "))
            self.tree.column(col, width=110, anchor="center")

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<Double-1>", lambda event: self.load_selected_into_form())

        # Actions Panel
        action_bar = ttk.Frame(self.tab_viewer, padding="10")
        action_bar.pack(fill=tk.X, pady=10)

        ttk.Button(action_bar, text="Editar Registro Seleccionado", command=self.load_selected_into_form).pack(side=tk.LEFT, padx=20, expand=True)
        ttk.Button(action_bar, text="Eliminar Registro", command=self.delete_selected_record).pack(side=tk.RIGHT, padx=20, expand=True)

        # Load data initially
        self.refresh_treeview()

    def get_all_csv_records(self):
        """Reads and returns all rows from the CSV including header."""
        if not os.path.exists(self.csv_filename):
            return [], []
        with open(self.csv_filename, mode='r', encoding='utf-8') as file:
            reader = list(csv.reader(file))
            if not reader:
                return [], []
            return reader[0], reader[1:]

    def refresh_treeview(self):
        """Reloads records into the Treeview based on current search filter."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        headers, records = self.get_all_csv_records()
        query = self.search_var.get().lower()

        for idx, row in enumerate(records):
            if not row:
                continue
            # Search matches across Folio, NSS, or Patient Name
            match_string = f"{row[1]} {row[2]} {row[3]} {row[4]}".lower()
            if query in match_string:
                display_vals = (row[1], row[0], row[2], row[3], row[4], row[6], row[7], row[9])
                self.tree.insert("", tk.END, iid=str(idx), values=display_vals)

    def load_selected_into_form(self):
        """Loads selected Treeview record back into the input fields for editing."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Por favor seleccione un registro de la lista.")
            return

        row_index = int(selected_item[0])
        headers, records = self.get_all_csv_records()
        record = records[row_index]

        # Reset form
        self.clear_fields()

        # Map header values back to variables
        for idx, key in enumerate(headers):
            if idx >= len(record):
                continue
            val = record[idx]
            
            if key == "Comorbilidades":
                selected_items = [c.strip() for c in val.split(";")]
                for item in selected_items:
                    if item in self.comorbilidades_vars:
                        self.comorbilidades_vars[item].set(True)
                    elif item.startswith("OTROS"):
                        other_text = item.replace("OTROS (", "").rstrip(")")
                        self.vars["Comorbilidad_Otros"].set(other_text)
            elif key in self.vars:
                self.vars[key].set(val)

        # Set app into edit state
        self.editing_row_index = row_index
        self.btn_registro.config(text="Actualizar Registro")
        self.notebook.select(self.tab_entry)  # Switch to Form Tab

    def delete_selected_record(self):
        """Removes the selected record from the CSV file."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Por favor seleccione un registro para eliminar.")
            return

        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este registro?"):
            return

        row_index = int(selected_item[0])
        headers, records = self.get_all_csv_records()

        if 0 <= row_index < len(records):
            del records[row_index]

            with open(self.csv_filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(records)

            self.refresh_treeview()
            messagebox.showinfo("Éxito", "El registro fue eliminado correctamente.")

    # ---------------- TAB 3: PATHOLOGY REPORT GENERATOR (A1.0.py) ----------------

    def build_report_tab(self):
        main_frame = ttk.Frame(self.tab_report)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=15)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title Header
        ttk.Label(scrollable_frame, text="Pathology Report Form Entry", font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # --- Section 1: Report Metadata & Patient Info ---
        sec1 = ttk.LabelFrame(scrollable_frame, text=" Patient & Header Information ", padding=10)
        sec1.pack(fill="x", expand=True, pady=5)

        patient_fields = [
            ("REF Number:", "ref_no"),
            ("Patient Name:", "patient_name"),
            ("DOB / Sex:", "dob_sex"),
            ("Accession No:", "accession_no"),
            ("Specimen ID:", "specimen_id"),
            ("Ordering Dr:", "ordering_dr"),
            ("Origin:", "origin"),
            ("Test Requested:", "test_requested"),
            ("Date Collected:", "date_collected"),
            ("Date Received:", "date_received"),
            ("Report Date:", "report_date"),
        ]

        for i, (label, key) in enumerate(patient_fields):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(sec1, text=label).grid(row=row, column=col, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(sec1, width=28)
            entry.grid(row=row, column=col+1, sticky="w", padx=5, pady=3)
            self.report_entries[key] = entry

        # --- Section 2: Physical & Morphological Examination ---
        sec2 = ttk.LabelFrame(scrollable_frame, text=" 1. Physical & Morphological Examination ", padding=10)
        sec2.pack(fill="x", expand=True, pady=5)

        phys_fields = [
            ("Quantity Submitted:", "qty_submitted"),
            ("Total Mass:", "total_mass"),
            ("Dimensions:", "dimensions"),
            ("Color & Surface:", "color_surface"),
            ("Consistency:", "consistency")
        ]

        for i, (label, key) in enumerate(phys_fields):
            ttk.Label(sec2, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(sec2, width=60)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.report_entries[key] = entry

        # --- Section 3: Composition Analysis Results ---
        sec4 = ttk.LabelFrame(scrollable_frame, text=" 3. Composition Analysis Results ", padding=10)
        sec4.pack(fill="x", expand=True, pady=5)

        comp_fields = [
            ("Whewellite (COM):", "comp_whewellite"),
            ("Weddellite (COD):", "comp_weddellite"),
            ("Dahlite / Carbonate-Apatite:", "comp_dahlite"),
            ("Uric Acid / Cystine / Struvite:", "comp_other")
        ]

        for i, (label, key) in enumerate(comp_fields):
            ttk.Label(sec4, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(sec4, width=30)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.report_entries[key] = entry

        # --- Section 4: Spectrum Image Upload ---
        sec_img1 = ttk.LabelFrame(scrollable_frame, text=" Spectrum Image Upload ", padding=10)
        sec_img1.pack(fill="x", expand=True, pady=7)
        
        ttk.Button(sec_img1, text="Select Spectrum Image", command=self.select_spectrum).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(sec_img1, textvariable=self.spectrum_img_path, foreground="blue", wraplength=400).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(sec_img1, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(sec_img1, textvariable=self.spectrum_desc, width=60).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # --- Section 5: Kidney Stone Images Upload ---
        sec_img2 = ttk.LabelFrame(scrollable_frame, text=" Kidney Stone Images (Max 4) ", padding=10)
        sec_img2.pack(fill="x", expand=True, pady=5)
        
        for i in range(4):
            frame = ttk.Frame(sec_img2)
            frame.pack(fill="x", pady=2)
            ttk.Button(frame, text=f"Select Image {i+1}", command=lambda idx=i: self.select_stone(idx)).grid(row=0, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(frame, textvariable=self.stone_img_paths[i], foreground="green", wraplength=200).grid(row=0, column=1, padx=5, pady=2, sticky="w")
            ttk.Label(frame, text="Desc:").grid(row=0, column=2, padx=5, pady=2, sticky="e")
            ttk.Entry(frame, textvariable=self.stone_descs[i], width=35).grid(row=0, column=3, padx=5, pady=2, sticky="w")

        # --- Section 6: Findings & Interpretation ---
        sec5 = ttk.LabelFrame(scrollable_frame, text=" Clinical Interpretation ", padding=10)
        sec5.pack(fill="x", expand=True, pady=5)

        ttk.Label(sec5, text="Diagnostic Summary:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        entry_diag = ttk.Entry(sec5, width=60)
        entry_diag.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        self.report_entries["diagnostic_summary"] = entry_diag

        # Submit Button
        btn_submit = ttk.Button(scrollable_frame, text="Generate Pathology PDF Report & Log Entry", command=self.generate_pdf)
        btn_submit.pack(pady=20)

    # --- File Dialog Helpers ---
    def select_spectrum(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if filepath:
            self.spectrum_img_path.set(filepath)

    def select_stone(self, index):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if filepath:
            self.stone_img_paths[index].set(filepath)

    # --- Watermark Drawing Callback ---
    def draw_corner_watermarks(self, canvas, doc):
        canvas.saveState()
        canvas.setFillAlpha(0.18)
        
        wm_width = 100 * (72 / 96)
        page_width, page_height = doc.pagesize

        # Upper Left Watermark: IMSS_Logo.png
        left_logo = "IMSS_Logo.png"
        if os.path.exists(left_logo):
            with PILImage.open(left_logo) as img:
                w, h = img.size
                wm_height = wm_width * (h / w) * 0.8
                canvas.drawImage(left_logo, 10, page_height - wm_height - 10, width=wm_width, height=wm_height, mask='auto')

        # Upper Right Watermark: LOGO.png
        right_logo = "LOGO.png"
        if os.path.exists(right_logo):
            with PILImage.open(right_logo) as img:
                w, h = img.size
                wm_height = wm_width * (h / w)
                canvas.drawImage(right_logo, page_width - wm_width - 10, page_height - wm_height - 10, width=wm_width, height=wm_height, mask='auto')

        canvas.restoreState()

    # --- Image Processing Helper ---
    def resize_image_to_reference(self, source_path, reference_name, output_temp_path, default_size=(360, 270)):
        try:
            if os.path.exists(reference_name):
                with PILImage.open(reference_name) as ref_img:
                    target_size = ref_img.size
            else:
                target_size = default_size
                
            with PILImage.open(source_path) as src_img:
                resized_img = src_img.resize(target_size, PILImage.Resampling.LANCZOS)
                resized_img.save(output_temp_path)
            return output_temp_path
            
        except Exception as e:
            messagebox.showwarning("Image Error", f"Could not process image {source_path}.\nError: {e}")
            return None

    # --- CSV Master Record Logger ---
    def append_to_csv_master_record(self, data, pdf_path):
        csv_filename = "MasterRecord.csv"
        file_exists = os.path.isfile(csv_filename)

        row_data = {
            "REF No": data.get("ref_no", ""),
            "Patient Name": data.get("patient_name", ""),
            "DOB/Sex": data.get("dob_sex", ""),
            "Accession No": data.get("accession_no", ""),
            "Specimen ID": data.get("specimen_id", ""),
            "Ordering Dr": data.get("ordering_dr", ""),
            "Origin": data.get("origin", ""),
            "Test Requested": data.get("test_requested", ""),
            "Date Collected": data.get("date_collected", ""),
            "Date Received": data.get("date_received", ""),
            "Report Date": data.get("report_date", ""),
            "Quantity Submitted": data.get("qty_submitted", ""),
            "Total Mass": data.get("total_mass", ""),
            "Dimensions": data.get("dimensions", ""),
            "Color & Surface": data.get("color_surface", ""),
            "Consistency": data.get("consistency", ""),
            "Whewellite (COM)": data.get("comp_whewellite", ""),
            "Weddellite (COD)": data.get("comp_weddellite", ""),
            "Dahlite / Carbonate-Apatite": data.get("comp_dahlite", ""),
            "Uric Acid / Cystine / Other": data.get("comp_other", ""),
            "Spectrum Image Path": self.spectrum_img_path.get(),
            "Spectrum Description": self.spectrum_desc.get(),
            "Stone Image 1 Path": self.stone_img_paths[0].get(),
            "Stone Image 1 Desc": self.stone_descs[0].get(),
            "Stone Image 2 Path": self.stone_img_paths[1].get(),
            "Stone Image 2 Desc": self.stone_descs[1].get(),
            "Stone Image 3 Path": self.stone_img_paths[2].get(),
            "Stone Image 3 Desc": self.stone_descs[2].get(),
            "Stone Image 4 Path": self.stone_img_paths[3].get(),
            "Stone Image 4 Desc": self.stone_descs[3].get(),
            "Diagnostic Summary": data.get("diagnostic_summary", ""),
            "PDF Report File Link": os.path.abspath(pdf_path)
        }

        fieldnames = list(row_data.keys())

        with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row_data)

    # --- PDF Generation ---
    def generate_pdf(self):
        data = {k: v.get() for k, v in self.report_entries.items()}
        
        accession = data.get('accession_no', '').strip()
        filename = f"Pathology_Report_{accession}.pdf" if accession else "Pathology_Report.pdf"

        try:
            doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=12, leading=14, alignment=1, fontName="Helvetica-Bold")
            sub_title_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=9, leading=11, alignment=1)
            section_heading = ParagraphStyle('SecHeading', parent=styles['Heading2'], fontSize=10, leading=12, fontName="Helvetica-Bold", textColor=colors.HexColor("#003366"), spaceBefore=8, spaceAfter=4)
            normal_text = ParagraphStyle('NormalText', parent=styles['Normal'], fontSize=8.5, leading=11)
            bold_label = ParagraphStyle('BoldLabel', parent=styles['Normal'], fontSize=8.5, leading=11, fontName="Helvetica-Bold")
            center_desc = ParagraphStyle('CenterDesc', parent=styles['Normal'], fontSize=8, leading=10, alignment=1, fontName="Helvetica-Oblique")

            story = []

            # Lab Header
            story.append(Paragraph("METROPOLITAN CLINICAL PATHOLOGY LABORATORY", title_style))
            story.append(Paragraph("Department of Calculi & Spectrometric Analysis<br/>100 Medical Center Drive, Suite 400 Phone: (555) 019-2831 Direct Lab Line: (555) 019-2835", sub_title_style))
            story.append(Spacer(1, 10))

            # Patient & Specimen Info Table
            info_data = [
                [Paragraph("<b>Patient Name:</b>", bold_label), Paragraph(data.get('patient_name', ''), normal_text), Paragraph("<b>Accession No:</b>", bold_label), Paragraph(data.get('accession_no', ''), normal_text)],
                [Paragraph("<b>DOB/Sex:</b>", bold_label), Paragraph(data.get('dob_sex', ''), normal_text), Paragraph("<b>Specimen ID:</b>", bold_label), Paragraph(data.get('specimen_id', ''), normal_text)],
                [Paragraph("<b>Origin:</b>", bold_label), Paragraph(data.get('origin', ''), normal_text), Paragraph("<b>Date Received:</b>", bold_label), Paragraph(data.get('date_received', ''), normal_text)]
            ]

            t_info = Table(info_data, colWidths=[90, 180, 90, 180])
            t_info.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F2F4F8")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(t_info)
            story.append(Spacer(1, 8))

            # 1. Physical Examination
            story.append(Paragraph("1. PHYSICAL & MORPHOLOGICAL EXAMINATION", section_heading))
            phys_text = f"• <b>Total Mass:</b> {data.get('total_mass', '')} | <b>Dimensions:</b> {data.get('dimensions', '')}<br/>• <b>Consistency:</b> {data.get('consistency', '')}"
            story.append(Paragraph(phys_text, normal_text))

            # 2. Composition Analysis
            story.append(Paragraph("2. COMPOSITION ANALYSIS RESULTS", section_heading))
            comp_table_data = [
                [Paragraph("<b>MINERAL NAME</b>", bold_label), Paragraph("<b>FORMULA</b>", bold_label), Paragraph("<b>ABUNDANCE</b>", bold_label)],
                [Paragraph("Whewellite", normal_text), Paragraph("Calcium Oxalate Monohydrate", normal_text), Paragraph(data.get('comp_whewellite', ''), normal_text)],
                [Paragraph("Weddellite", normal_text), Paragraph("Calcium Oxalate Dihydrate", normal_text), Paragraph(data.get('comp_weddellite', ''), normal_text)],
                [Paragraph("Dahlite / Apatite", normal_text), Paragraph("Calcium Phosphate Carbonate", normal_text), Paragraph(data.get('comp_dahlite', ''), normal_text)],
            ]
            t_comp = Table(comp_table_data, colWidths=[150, 250, 100])
            t_comp.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E0E6ED")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(t_comp)

            # 3. Spectroscopic Findings (Image)
            story.append(Paragraph("3. SPECTROSCOPIC & MICROSCOPIC FINDINGS", section_heading))
            
            spec_path = self.spectrum_img_path.get()
            if spec_path:
                temp_spec = self.resize_image_to_reference(spec_path, "loreipsum_espectro.jpg", "temp_spectrum.jpg")
                if temp_spec:
                    story.append(Spacer(1, 5))
                    story.append(RLImage(temp_spec, width=3.5*inch, height=2.5*inch))
                    story.append(Paragraph(self.spectrum_desc.get(), center_desc))
                    story.append(Spacer(1, 5))
            else:
                story.append(Paragraph("<i>No spectroscopic image provided.</i>", normal_text))

            # 4. Kidney Stone Imagery
            story.append(Paragraph("4. MORPHOLOGY & SPECIMEN IMAGERY", section_heading))
            
            stone_images = []
            for idx, path_var in enumerate(self.stone_img_paths):
                sp = path_var.get()
                if sp:
                    temp_stone = self.resize_image_to_reference(sp, "loremipsum_im1.jpg", f"temp_stone_{idx}.jpg")
                    if temp_stone:
                        img = RLImage(temp_stone, width=2.5*inch, height=1.8*inch)
                        desc = Paragraph(self.stone_descs[idx].get(), center_desc)
                        stone_images.append([img, desc])

            if stone_images:
                grid_data = []
                for i in range(0, len(stone_images), 2):
                    row = []
                    col1_data = stone_images[i] 
                    row.append(Table([[col1_data[0]], [col1_data[1]]]))
                    
                    if i + 1 < len(stone_images):
                        col2_data = stone_images[i+1]
                        row.append(Table([[col2_data[0]], [col2_data[1]]]))
                    else:
                        row.append(Paragraph("", normal_text))
                        
                    grid_data.append(row)

                stone_table = Table(grid_data, colWidths=[2.8*inch, 2.8*inch])
                stone_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
                story.append(stone_table)
            else:
                story.append(Paragraph("<i>No specimen images provided.</i>", normal_text))

            # 5. Interpretation
            story.append(Paragraph("5. CLINICAL PATHOLOGY INTERPRETATION", section_heading))
            story.append(Paragraph(f"<b>Diagnostic Summary:</b> {data.get('diagnostic_summary', '')}", normal_text))

            # Build PDF
            doc.build(story, onFirstPage=self.draw_corner_watermarks, onLaterPages=self.draw_corner_watermarks)
            
            # Cleanup temp files
            if os.path.exists("temp_spectrum.jpg"): 
                os.remove("temp_spectrum.jpg")
            for i in range(4):
                if os.path.exists(f"temp_stone_{i}.jpg"): 
                    os.remove(f"temp_stone_{i}.jpg")

            # CSV Export Step
            self.append_to_csv_master_record(data, filename)

            messagebox.showinfo("Success", f"PDF Report created and Master Record logged:\n\nPDF Path: {os.path.abspath(filename)}\nCSV Log: {os.path.abspath('MasterRecord.csv')}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report or save CSV record: {e}")

    # ---------------- GENERAL LOGIC (TAB 1) ----------------

    def save_data(self):
        """Collects all form values and writes/updates a row in Registro_LUM.csv."""
        selected_comorb = [key for key, var in self.comorbilidades_vars.items() if var.get()]
        otros_val = self.vars["Comorbilidad_Otros"].get().strip()
        if otros_val:
            selected_comorb.append(f"OTROS ({otros_val})")
        comorbidities_str = "; ".join(selected_comorb)

        row_data = [
            self.vars["Fecha_Recepcion"].get(),
            self.vars["Folio_Interno"].get(),
            self.vars["NSS"].get(),
            self.vars["Nombre"].get(),
            self.vars["Apellido_Paterno"].get(),
            self.vars["Apellido_Materno"].get(),
            self.vars["Sexo"].get(),
            self.vars["Edad"].get(),
            self.vars["Unidad_Servicio"].get(),
            self.vars["Medico"].get(),
            self.vars["Fecha_Recoleccion"].get(),
            self.vars["Metodo"].get(),
            self.vars["Localizacion"].get(),
            self.vars["Lado"].get(),
            self.vars["Fragmentado"].get(),
            self.vars["Observaciones"].get(),
            self.vars["pH"].get(),
            self.vars["Urocultivo"].get(),
            self.vars["Microorganismo"].get(),
            self.vars["Orina_Glucosa"].get(),
            self.vars["Orina_Creatinina"].get(),
            self.vars["Orina_AcidoUrico"].get(),
            self.vars["Orina_Na"].get(),
            self.vars["Orina_K"].get(),
            self.vars["Orina_Cl"].get(),
            self.vars["Orina_Ca"].get(),
            self.vars["Orina_P"].get(),
            self.vars["Orina_Mg"].get(),
            self.vars["Orina_Citrato"].get(),
            self.vars["Orina_Oxalato"].get(),
            self.vars["Suero_Glucosa"].get(),
            self.vars["Suero_Creatinina"].get(),
            self.vars["Suero_AcidoUrico"].get(),
            self.vars["Suero_Na"].get(),
            self.vars["Suero_K"].get(),
            self.vars["Suero_Cl"].get(),
            self.vars["Suero_Ca"].get(),
            self.vars["Suero_P"].get(),
            self.vars["Suero_Mg"].get(),
            self.vars["Entidad_Federativa"].get(),
            self.vars["Municipio_Alcaldia"].get(),
            self.vars["CP"].get(),
            self.vars["Ocupacion"].get(),
            self.vars["Zona"].get(),
            self.vars["Evento"].get(),
            self.vars["No_Recurrencia"].get(),
            self.vars["Historia_Familiar"].get(),
            self.vars["IVU_Reciente"].get(),
            comorbidities_str,
            self.vars["Iniciales_Analista"].get()
        ]

        try:
            headers, records = self.get_all_csv_records()

            if self.editing_row_index is not None:
                records[self.editing_row_index] = row_data
                with open(self.csv_filename, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)
                    writer.writerows(records)
                messagebox.showinfo("Éxito", f"Registro actualizado exitosamente en {self.csv_filename}")
            else:
                with open(self.csv_filename, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(row_data)
                messagebox.showinfo("Éxito", f"Datos guardados exitosamente en {self.csv_filename}")

            self.clear_fields()
            self.refresh_treeview()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la información:\n{str(e)}")

    def clear_fields(self):
        """Clears all text entries and resets edit states."""
        self.editing_row_index = None
        self.btn_registro.config(text="Registro")

        for key, var in self.vars.items():
            if key == "Sexo":
                var.set("M")
            elif key == "Lado":
                var.set("Derecho")
            elif key == "Fragmentado":
                var.set("No")
            elif key == "Urocultivo":
                var.set("No realizado")
            elif key == "Zona":
                var.set("Urbano")
            elif key == "Evento":
                var.set("1er Evento")
            elif key in ["Historia_Familiar", "IVU_Reciente"]:
                var.set("No")
            else:
                var.set("")

        for var in self.comorbilidades_vars.values():
            var.set(False)


if __name__ == "__main__":
    app = RegistroApp()
    app.mainloop()