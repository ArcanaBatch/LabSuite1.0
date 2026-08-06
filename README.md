<img src="logofull2.png" alt="Description of the image" width="250">


# LabSuite - Laboratorio de Unidad Metabólica (LUM)
### Morpho-Constitutional Kidney Stone Analysis & Pathology Report System

**LabSuite** is a comprehensive Python desktop application designed for medical laboratories, path-labs, and metabolic unit specialists analyzing kidney stones (renal calculi). The system facilitates patient data entry, metabolic urine and serum parameter tracking, historical record query and modification, and automated creation of pathology PDF reports complete with spectroscopic analysis and specimen imagery.

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [File Architecture & Assets](#file-architecture--assets)
- [Prerequisites & Dependencies](#prerequisites--dependencies)
- [Installation Guide](#installation-guide)
- [Application Workflow & Usage](#application-workflow--usage)
  - [Tab 1: Formulario de Registro (Data Entry)](#tab-1-formulario-de-registro-data-entry)
  - [Tab 2: Consulta y Edición de Registros (Record Search & Edit)](#tab-2-consulta-y-edición-de-registros-record-search--edit)
  - [Tab 3: Generador de Reporte PDF (Pathology Report Generator)](#tab-3-generador-de-reporte-pdf-pathology-report-generator)
- [Data Storage & Output Files](#data-storage--output-files)
- [Troubleshooting & FAQs](#troubleshooting--faqs)

---

## Overview

`Merged2.0.py` merges data logging, patient tracking, and pathology PDF reporting into a unified graphical interface built on `Tkinter` and `ThemedTk`. It is tailored for the analysis of renal calculi, capturing clinical parameters, demographic metadata, metabolic panels (serum and urine), and physical stone properties.

---

## Key Features

1. **Patient & Specimen Data Tracking (Formulario de Registro)**
   - Captures patient identification (Name, NSS, Internal Folio, Sex, Age, Ordering Physician, Medical Unit).
   - Records sample collection details (Method, Anatomical Location, Side, Fragmentation, Observations).
   - Full metabolic tracking:
     - **Urine Panel:** pH, Urinalysis/Culture, Microorganism, Glucose, Creatinine, Uric Acid, Na, K, Cl, Ca, P, Mg, Citrate, Oxalate.
     - **Serum Panel:** Glucose, Creatinine, Uric Acid, Na, K, Cl, Ca, P, Mg.
   - Epidemiological and population metadata (State, Municipality, ZIP code, Occupation, Area Type, Recurrence, Family History, Recent UTIs, Comorbidities).

2. **Interactive Database Viewer & Management (Consulta y Edición)**
   - Real-time search by **Folio**, **NSS**, or **Patient Name**.
   - Treeview table listing existing records.
   - One-click record loading into the registration form for modifications.
   - Record deletion capability with CSV sync.

3. **PDF Pathology Report Generator (Generador de Reporte PDF)**
   - Form for pathology-specific headers, reference numbers, and accession numbers.
   - Physical and morphological stone attributes (mass, dimensions, color/surface, consistency).
   - Stone composition percentages (Whewellite/COM, Weddellite/COD, Dahlite/Apatite, Uric Acid/Cystine/Struvite, etc.).
   - Image attachment engine:
     - 1 Spectroscopic Analysis Chart with description.
     - Up to 4 Specimen/Morphology images with individual descriptions.
   - Automatic image resizing and normalization for PDF rendering.
   - Dual-corner translucent image watermarking (`IMSS_Logo.png` and `LOGO.png`).
   - Automated export to PDF and logging into `MasterRecord.csv`.

---

## File Architecture & Assets

Place all logo images in the same directory as `Merged2.0.py`:

```
labsuite-project/
│
├── Merged2.0.py              # Main executable script
├── Registro_LUM.csv          # Local database for clinical registration (auto-generated)
├── MasterRecord.csv          # Master database for pathology PDF entries (auto-generated)
│
├── mini_LOGO.png             # Application window icon
├── logofull2.png             # Main header branding logo
├── IMSS_Logo.png             # Left watermark logo for PDF reports
└── LOGO.png                  # Right watermark logo for PDF reports
```

---

## Prerequisites & Dependencies

The application is written in **Python 3.x**. Ensure you have the following third-party packages installed:

* `ttkthemes` (Theme engine for Tkinter UI)
* `tkcalendar` (DateEntry widget)
* `Pillow` (PIL image handling and thumbnail generation)
* `reportlab` (PDF document generation and layout engine)

### Standard Libraries Used
`os`, `csv`, `tkinter`

---

## Installation Guide

1. **Clone or Download the Repository**
   Ensure `Merged2.0.py` and required image assets are in the target working directory.

2. **Install Required Packages**
   Run the following command in your terminal or command prompt:

   ```bash
   pip install ttkthemes tkcalendar pillow reportlab
   ```

3. **Run the Application**
   Launch the interface with:

   ```bash
   python Merged2.0.py
   ```

---

## Application Workflow & Usage

### Tab 1: Formulario de Registro (Data Entry)
1. Fill out the relevant fields in the 5 main sections:
   - **Identificación y Trazabilidad**: Patient demographics, Reception date, Folio.
   - **Obtención, Localización y Estado de la Muestra**: Sample retrieval details.
   - **Estudios Metabólicos**: Urine and serum biochemical indicators.
   - **Variables Poblacionales**: Comorbidities (Diabetes, Hypertension, Obesity, Gout, etc.) and region.
   - **Analista/Capturista**: Staff initials.
2. Click **Registro** to append the record to `Registro_LUM.csv`.
3. Use **Limpiar** to clear all form fields.

### Tab 2: Consulta y Edición de Registros (Record Search & Edit)
1. Type a query into the search bar (matches Folio, NSS, or Patient Name).
2. Double-click a row or select it and click **Editar Registro Seleccionado**.
   - The system switches to Tab 1 and populates all fields.
   - Modify the fields and click **Actualizar Registro** to update the existing row.
3. Select a row and click **Eliminar Registro** to remove it from `Registro_LUM.csv`.

### Tab 3: Generador de Reporte PDF (Pathology Report Generator)
1. Complete header and accession information.
2. Input stone mass, dimensions, and mineral abundance percentages.
3. Upload images:
   - **Spectrum Image**: Select IR/Raman spectrum chart and provide a caption.
   - **Stone Images**: Select up to 4 high-resolution stone photographs and add descriptions.
4. Fill in the **Diagnostic Summary**.
5. Click **Generate Pathology PDF Report & Log Entry**.
   - Generates a PDF file named `Pathology_Report_<Accession_No>.pdf`.
   - Appends all input fields and absolute file pathways to `MasterRecord.csv`.

---

## Data Storage & Output Files

* **`Registro_LUM.csv`**: Contains all metabolic and demographic registry data. Created automatically upon first submission if absent.
* **`MasterRecord.csv`**: Contains complete diagnostic entries from the PDF generator tab, including file links to generated PDFs and uploaded image paths.
* **`Pathology_Report_<Accession_No>.pdf`**: Generated clinical report suitable for patient delivery or archiving.

---

## Troubleshooting & FAQs

* **Missing Logo Warnings (`Advertencia: No se pudo cargar...`)**:
  - The program will launch even if logo images are missing. However, to see branding elements and PDF watermarks, verify `mini_LOGO.png`, `logofull2.png`, `IMSS_Logo.png`, and `LOGO.png` exist in the working directory.
* **`ModuleNotFoundError`**:
  - Ensure all required packages (`ttkthemes`, `tkcalendar`, `pillow`, `reportlab`) are installed in your active Python environment.
* **PDF Layout Issues**:
  - Check that attached images are standard PNG or JPG files. Pillow will resize them automatically during PDF creation.
