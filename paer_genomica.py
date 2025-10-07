import tkinter as tk
from tkinter import ttk, filedialog
import json
from datetime import datetime
import os

# -------------------------------
# Section 1: Main Directory Setup
# -------------------------------
# This defines the directory where the configuration JSON will be saved.
main_directory_path = os.getcwd()

# -------------------------------
# Section 2: Main Window & Scroll
# -------------------------------
# A scrollable canvas is used because the form has many sections.
root = tk.Tk()
root.title("Genome Analysis Configuration")
root.geometry("900x700")

canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

# Bind frame resizing to canvas scroll
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# -------------------------------
# Section 3: Global Variables
# -------------------------------
# Store all Tkinter variables for easy access and dynamic updates.
variables = {}

def create_bool_var(name, default=False):
    var = tk.BooleanVar(value=default)
    variables[name] = var
    return var

def create_int_var(name, default=0):
    var = tk.IntVar(value=default)
    variables[name] = var
    return var

# -------------------------------
# Section 4: Utility Functions
# -------------------------------
# These functions manage dynamic frames, file selection, and input generation.

def toggle_frame(frame, state):
    """Show or hide a frame based on a boolean state."""
    if state:
        frame.pack(fill="x", padx=20, pady=2)
    else:
        frame.pack_forget()

def browse_file(entry_widget, filetypes=(("All files", "*.*"),)):
    """Open a file dialog and set the path in the Entry widget."""
    filename = filedialog.askopenfilename(filetypes=filetypes)
    if filename:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filename)

def update_inputs(frame, num, widget_type='entry', filetype=None):
    """Dynamically generate input rows inside a frame.
    Critical: must be called when Spinbox value changes or checkbox activates.
    """
    for widget in frame.winfo_children():
        widget.destroy()
    for i in range(num):
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=2)
        if widget_type == 'entry':
            label = ttk.Label(row, text=f'Item {i+1}')
            label.pack(side="left", padx=5)
            entry = ttk.Entry(row, width=50)
            entry.pack(side="left", padx=5)
        elif widget_type == 'file':
            entry = ttk.Entry(row, width=50)
            entry.pack(side="left", padx=5)
            btn = ttk.Button(row, text="Browse", command=lambda e=entry: browse_file(e, filetype))
            btn.pack(side="left", padx=5)

def create_section(parent, label_text, var_type='bool', default=False, max_value=10):
    """Create a GUI section with a checkbox or spinbox and a frame for dynamic inputs.
    Critical: input frame is initially empty and updated dynamically.
    """
    section_frame = ttk.Frame(parent)
    section_frame.pack(fill="x", pady=5)

    inputs_frame = ttk.Frame(section_frame)
    inputs_frame.pack(fill="x", padx=20, pady=2)

    if var_type == 'bool':
        var = create_bool_var(label_text.replace(" ", "_"), default=default)
        widget = ttk.Checkbutton(section_frame, text=label_text, variable=var)
    elif var_type == 'int':
        var = create_int_var(label_text.replace(" ", "_"), default=default)
        label = ttk.Label(section_frame, text=label_text)
        label.pack(side="left", padx=5)
        widget = ttk.Spinbox(section_frame, from_=0, to=max_value, textvariable=var, width=5)
    else:
        raise ValueError("var_type must be 'bool' or 'int'")

    widget.pack(side="left", padx=5)

    return section_frame, inputs_frame, var

# -------------------------------
# Section 5: Create Sections
# -------------------------------
# Each section corresponds to a widget or group of widgets from the original Jupyter notebook.
sections = {}
def add_section(name, label, var_type='bool', default=False, max_value=10):
    frame, inputs, var = create_section(scrollable_frame, label, var_type, default, max_value)
    sections[name] = {'frame': frame, 'inputs': inputs, 'var': var}
    return var, inputs

# Create all main sections
config_var, config_inputs = add_section("configuration", "Configuration file")
merge_var, merge_inputs = add_section("merge", "Merge .fastq files")
download_var, download_inputs = add_section("download", "Download reference genome", var_type='int')
index_var, index_inputs = add_section("indexing", "Genome indexing", var_type='int')
bowtie2_var, bowtie2_inputs = add_section("bowtie2", "Bowtie2 alignment")
alignment_var, alignment_inputs = add_section("alignment", "Strains", var_type='int', default=1)
realign_var, realign_inputs = add_section("realign", "SAMtools realign assembly")
realignment_var, realignment_inputs = add_section("realignment", "Strains", var_type='int', default=1)
snps_var, snps_inputs = add_section("snps", "Find SNPs")
indels_var, indels_inputs = add_section("indels", "Find indels")
build_var, build_inputs = add_section("build", "Build genome database")
database_var, database_inputs = add_section("database", "Databases", var_type='int', default=1)
snpeff_var, ncbi_inputs = add_section("snpeff", "SNP/indel annotation")
ncbi_var, ncbi_inputs = add_section("ncbi", "NCBI RefSeq", var_type='int', default=1)
filter_var, parental_inputs = add_section("filter", "Filter SNP/indel by parental")
parental_var, parental_inputs = add_section("parental", "Parental", var_type='int', default=1)
table_var, strains_inputs = add_section("table", "Sample/mutation table")
threshold_var, threshold_inputs = add_section("threshold", "Threshold", var_type='int', default=1)
strains_var, strains_inputs = add_section("strains", "Strains", var_type='int', default=1)
denovo_var, denovo_inputs = add_section("denovo", "De novo genome assembly")
compress_var, compress_inputs = add_section("compress", "Compress large files")
confirm_var, confirm_inputs = add_section("confirm", "Confirm")

# -------------------------------
# Section 6: Dynamic Input Updates
# -------------------------------
# Each Spinbox or checkbox triggers dynamic input generation in its section.
def update_section(var, inputs_frame, widget_type='entry', filetype=None):
    num = var.get() if isinstance(var, tk.IntVar) else 1
    update_inputs(inputs_frame, num, widget_type, filetype)

download_var.trace_add('write', lambda *args: update_section(download_var, download_inputs))
index_var.trace_add('write', lambda *args: update_section(index_var, index_inputs))
alignment_var.trace_add('write', lambda *args: update_section(alignment_var, alignment_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))
realignment_var.trace_add('write', lambda *args: update_section(realignment_var, realignment_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))
database_var.trace_add('write', lambda *args: update_section(database_var, database_inputs))
ncbi_var.trace_add('write', lambda *args: update_section(ncbi_var, ncbi_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))
parental_var.trace_add('write', lambda *args: update_section(parental_var, parental_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))
strains_var.trace_add('write', lambda *args: update_section(strains_var, strains_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))

# -------------------------------
# Section 7: Section Dependency Logic
# -------------------------------
# Toggle visibility of dependent frames based on parent checkbox states.
def bind_toggle(parent_var, target_frames):
    def callback(*args):
        state = parent_var.get()
        for frame in target_frames:
            toggle_frame(frame, state)
    parent_var.trace_add('write', callback)
    callback()

# Bind checkboxes to dependent frames
bind_toggle(config_var, [merge_inputs, download_inputs, index_inputs, alignment_inputs, realignment_inputs, database_inputs, ncbi_inputs, parental_inputs, strains_inputs])
bind_toggle(bowtie2_var, [alignment_inputs])
bind_toggle(realign_var, [realignment_inputs])
bind_toggle(build_var, [database_inputs])
bind_toggle(snpeff_var, [ncbi_inputs])
bind_toggle(filter_var, [parental_inputs])
bind_toggle(table_var, [strains_inputs])

# -------------------------------
# Section 8: Confirm Button Logic
# -------------------------------
# Critical: collects all user inputs and writes them to a JSON configuration file.
def on_confirm():
    configuration = {
        "configuration_file": config_var.get(),
        "merge": merge_var.get(),
        "download": [child.winfo_children()[1].get() for child in download_inputs.winfo_children()],
        "indexing": [child.winfo_children()[1].get() for child in index_inputs.winfo_children()],
        "bowtie2": {
            "enabled": bowtie2_var.get(),
            "strains": [child.winfo_children()[1].get() for child in alignment_inputs.winfo_children()]
        },
        "realign": {
            "enabled": realign_var.get(),
            "strains": [child.winfo_children()[1].get() for child in realignment_inputs.winfo_children()]
        },
        "snps": snps_var.get(),
        "indels": indels_var.get(),
        "build_database": {
            "enabled": build_var.get(),
            "databases": [child.winfo_children()[1].get() for child in database_inputs.winfo_children()]
        },
        "SNP_indel_annotation": {
            "enabled": snpeff_var.get(),
            "NCBI": [child.winfo_children()[1].get() for child in ncbi_inputs.winfo_children()]
        },
        "filter_by_parental": {
            "enabled": filter_var.get(),
            "parental": [child.winfo_children()[1].get() for child in parental_inputs.winfo_children()]
        },
        "table": {
            "enabled": table_var.get(),
            "strains": [child.winfo_children()[1].get() for child in strains_inputs.winfo_children()]
        },
        "denovo": denovo_var.get(),
        "compress": compress_var.get(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    config_file_path = os.path.join(main_directory_path, "config.json")
    with open(config_file_path, 'w') as f:
        json.dump(configuration, f, indent=4)
    print("Configuration saved to", config_file_path)

confirm_btn = ttk.Button(scrollable_frame, text="Confirm", command=on_confirm)
confirm_btn.pack(pady=20)

# ============================================================
# Start GUI loop
# ============================================================
root.mainloop()
