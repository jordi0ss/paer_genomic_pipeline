import tkinter as tk
from tkinter import ttk, filedialog
import json
from datetime import datetime
import os

# -------------------------------
# Main Window & Scroll
# -------------------------------
root = tk.Tk()
root.title("Genome Analysis Configuration")
root.geometry("1000x800")

canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

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
# Global Variables
# -------------------------------
variables = {}

def create_bool_var(name, default=False):
    var = tk.BooleanVar(value=default)
    variables[name] = var
    return var

def create_int_var(name, default=0):
    var = tk.IntVar(value=default)
    variables[name] = var
    return var

def create_str_var(name, default=""):
    var = tk.StringVar(value=default)
    variables[name] = var
    return var

# -------------------------------
# Utility Functions
# -------------------------------
# Functions for toggling frames, browsing for files/dirs, dynamic inputs.

def toggle_frame(frame, state):
    """Show or hide a frame based on a boolean state."""
    if state:
        frame.pack(fill="x", padx=20, pady=2)
    else:
        frame.pack_forget()

def browse_file(entry_widget, filetypes=(("All files", "*.*"),), initialdir=None):
    """Open a file dialog and set the path in the Entry widget."""
    start = initialdir if initialdir else (main_dir_var.get() or os.getcwd())
    filename = filedialog.askopenfilename(filetypes=filetypes, initialdir=start)
    if filename:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filename)

def browse_directory(entry_widget, initialdir=None):
    """Open a directory dialog and set the path in the Entry widget."""
    start = initialdir if initialdir else (main_dir_var.get() or os.getcwd())
    dirname = filedialog.askdirectory(initialdir=start)
    if dirname:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, dirname)

def update_inputs(frame, num, widget_type='entry', filetype=None):
    """Dynamically generate input rows inside a frame. """
    for widget in frame.winfo_children():
        widget.destroy()
    for i in range(num):
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=2)
        if widget_type == 'entry':
            label = ttk.Label(row, text=f'Item {i+1}')
            label.pack(side="left", padx=5)
            entry = ttk.Entry(row, width=60)
            entry.pack(side="left", padx=5)
        elif widget_type == 'file':
            # Entry + Browse button for selecting files
            entry = ttk.Entry(row, width=60)
            entry.pack(side="left", padx=5)
            btn = ttk.Button(row, text="Browse", command=lambda e=entry: browse_file(e, filetype))
            btn.pack(side="left", padx=5)

# -------------------------------
# Section Factory
# -------------------------------
def create_section(parent, label_text, var_type='bool', default=False, max_value=10):
    """Create a GUI section with a checkbox or spinbox and a frame for dynamic inputs.
    Returns (section_frame, inputs_frame, var).
    """
    section_frame = ttk.LabelFrame(parent, text=label_text)  # LabelFrame gives a border and title
    section_frame.pack(fill="x", pady=8, padx=10)

    controls_frame = ttk.Frame(section_frame)
    controls_frame.pack(fill="x", padx=10, pady=4)

    inputs_frame = ttk.Frame(section_frame)
    inputs_frame.pack(fill="x", padx=20, pady=4)

    if var_type == 'bool':
        var = create_bool_var(label_text.replace(" ", "_"), default=default)
        widget = ttk.Checkbutton(controls_frame, text=label_text, variable=var)
        widget.pack(side="left")
    elif var_type == 'int':
        var = create_int_var(label_text.replace(" ", "_"), default=default)
        label = ttk.Label(controls_frame, text=label_text)
        label.pack(side="left", padx=(0,6))
        widget = ttk.Spinbox(controls_frame, from_=0, to=max_value, textvariable=var, width=6)
        widget.pack(side="left")
    else:
        raise ValueError("var_type must be 'bool' or 'int'")

    return section_frame, inputs_frame, var

# -------------------------------
# Files/Directories Paths
# -------------------------------
# This replaces a hard-coded call to os.getcwd() and allows the GUI user to set all paths.
# There are diffenent subgroups with different meanings

paths_frame = ttk.LabelFrame(scrollable_frame, text="Files/directories paths (set all paths here)")
paths_frame.pack(fill="x", pady=10, padx=10)

# --- Directories ---
dirs_frame = ttk.LabelFrame(paths_frame, text="Directories")
dirs_frame.pack(fill="x", pady=6, padx=6)

# Main directory (where config.json will be written if selected)
main_dir_var = create_str_var("main_directory", default=os.getcwd())
main_dir_row = ttk.Frame(dirs_frame)
main_dir_row.pack(fill="x", pady=2, padx=4)
ttk.Label(main_dir_row, text="Main directory (config output)").pack(side="left", padx=4)
main_dir_entry = ttk.Entry(main_dir_row, textvariable=main_dir_var, width=70)
main_dir_entry.pack(side="left", padx=4)
ttk.Button(main_dir_row, text="Browse", command=lambda: browse_directory(main_dir_entry)).pack(side="left", padx=4)

# Input directory (default used for file dialogs)
input_dir_var = create_str_var("input_directory", default="")
input_dir_row = ttk.Frame(dirs_frame)
input_dir_row.pack(fill="x", pady=2, padx=4)
ttk.Label(input_dir_row, text="Input directory (default for file dialogs)").pack(side="left", padx=4)
input_dir_entry = ttk.Entry(input_dir_row, textvariable=input_dir_var, width=60)
input_dir_entry.pack(side="left", padx=4)
ttk.Button(input_dir_row, text="Browse", command=lambda: browse_directory(input_dir_entry, initialdir=main_dir_var.get() or None)).pack(side="left", padx=4)

# Output directory
output_dir_var = create_str_var("output_directory", default="")
output_dir_row = ttk.Frame(dirs_frame)
output_dir_row.pack(fill="x", pady=2, padx=4)
ttk.Label(output_dir_row, text="Output directory").pack(side="left", padx=4)
output_dir_entry = ttk.Entry(output_dir_row, textvariable=output_dir_var, width=70)
output_dir_entry.pack(side="left", padx=4)
ttk.Button(output_dir_row, text="Browse", command=lambda: browse_directory(output_dir_entry, initialdir=main_dir_var.get() or None)).pack(side="left", padx=4)

# --- Software choices ---
software_frame = ttk.LabelFrame(paths_frame, text="Software (select which tools the pipeline should call)")
software_frame.pack(fill="x", pady=6, padx=6)

# Create boolean checkboxes for common tools used in your notebook
sw_bowtie2 = create_bool_var("software_bowtie2", default=False)
sw_samtools = create_bool_var("software_samtools", default=False)
sw_spades = create_bool_var("software_spades", default=False)
sw_snpeff = create_bool_var("software_snpeff", default=False)
sw_bwa = create_bool_var("software_bwa", default=False)

ttk.Checkbutton(software_frame, text="Bowtie2", variable=sw_bowtie2).pack(side="left", padx=8, pady=6)
ttk.Checkbutton(software_frame, text="SAMtools", variable=sw_samtools).pack(side="left", padx=8, pady=6)
ttk.Checkbutton(software_frame, text="SPAdes", variable=sw_spades).pack(side="left", padx=8, pady=6)
ttk.Checkbutton(software_frame, text="snpEff", variable=sw_snpeff).pack(side="left", padx=8, pady=6)
ttk.Checkbutton(software_frame, text="BWA", variable=sw_bwa).pack(side="left", padx=8, pady=6)

# --- Other paths / settings ---
other_frame = ttk.LabelFrame(paths_frame, text="Other paths and settings")
other_frame.pack(fill="x", pady=6, padx=6)

temp_dir_var = create_str_var("temp_directory", default="")
ref_dir_var = create_str_var("reference_directory", default="")
config_suggestion_var = create_str_var("config_suggestion", default="config.json")

tmp_row = ttk.Frame(other_frame); tmp_row.pack(fill="x", pady=2, padx=4)
ttk.Label(tmp_row, text="Temp / working directory").pack(side="left", padx=4)
temp_dir_entry = ttk.Entry(tmp_row, textvariable=temp_dir_var, width=60); temp_dir_entry.pack(side="left", padx=4)
ttk.Button(tmp_row, text="Browse", command=lambda: browse_directory(temp_dir_entry, initialdir=main_dir_var.get() or None)).pack(side="left", padx=4)

ref_row = ttk.Frame(other_frame); ref_row.pack(fill="x", pady=2, padx=4)
ttk.Label(ref_row, text="Reference sequences directory (FASTA etc.)").pack(side="left", padx=4)
ref_dir_entry = ttk.Entry(ref_row, textvariable=ref_dir_var, width=50); ref_dir_entry.pack(side="left", padx=4)
ttk.Button(ref_row, text="Browse", command=lambda: browse_directory(ref_dir_entry, initialdir=main_dir_var.get() or None)).pack(side="left", padx=4)

cfg_row = ttk.Frame(other_frame); cfg_row.pack(fill="x", pady=2, padx=4)
ttk.Label(cfg_row, text="Suggested config filename").pack(side="left", padx=4)
cfg_entry = ttk.Entry(cfg_row, textvariable=config_suggestion_var, width=30); cfg_entry.pack(side="left", padx=4)

# -------------------------------
# Main GUI Sections
# -------------------------------
# Creating the rest of sections. Each is a labeled frame with inputs.
sections = {}
def add_section(name, label, var_type='bool', default=False, max_value=10):
    frame, inputs, var = create_section(scrollable_frame, label, var_type, default, max_value)
    sections[name] = {'frame': frame, 'inputs': inputs, 'var': var}
    return var, inputs

# Create all main sections (mirrors previous Jupyter layout)
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
snpeff_var, snpeff_inputs = add_section("snpeff", "SNP/indel annotation")
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
# Dynamic Input Updates
# -------------------------------
# Spinboxes generate the right number of input rows when changed.
def update_section(var, inputs_frame, widget_type='entry', filetype=None):
    # For IntVar show 'num' inputs; for Bool show 1 (enabled) or 0 (disabled)
    if isinstance(var, tk.IntVar):
        num = var.get()
    else:
        num = 1 if var.get() else 0
    update_inputs(inputs_frame, num, widget_type, filetype)

# Wire up trace callbacks for dynamic sections
download_var.trace_add('write', lambda *args: update_section(download_var, download_inputs))
index_var.trace_add('write', lambda *args: update_section(index_var, index_inputs))
alignment_var.trace_add('write', lambda *args: update_section(alignment_var, alignment_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))
realignment_var.trace_add('write', lambda *args: update_section(realignment_var, realignment_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))
database_var.trace_add('write', lambda *args: update_section(database_var, database_inputs))
ncbi_var.trace_add('write', lambda *args: update_section(ncbi_var, ncbi_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))
parental_var.trace_add('write', lambda *args: update_section(parental_var, parental_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))
strains_var.trace_add('write', lambda *args: update_section(strains_var, strains_inputs, widget_type='file', filetype=(("Text files","*.txt"),)))

# Initialize dynamic inputs once with defaults:
update_section(download_var, download_inputs)
update_section(index_var, index_inputs)
update_section(alignment_var, alignment_inputs, widget_type='file', filetype=(("Text files","*.txt"),))
update_section(realignment_var, realignment_inputs, widget_type='file', filetype=(("Text files","*.txt"),))
update_section(database_var, database_inputs)
update_section(ncbi_var, ncbi_inputs, widget_type='file', filetype=(("Text files","*.txt"),))
update_section(parental_var, parental_inputs, widget_type='file', filetype=(("Text files","*.txt"),))
update_section(strains_var, strains_inputs, widget_type='file', filetype=(("Text files","*.txt"),))

# -------------------------------
# Section Dependency Logic
# -------------------------------
# Show/hide input frames according to the state of their parent checkbox.
def bind_toggle(parent_var, target_inputs):
    def callback(*args):
        state = parent_var.get()
        # Each target_inputs is a frame to toggle; if parent_var is IntVar treat >0 as enabled
        for frame in target_inputs:
            toggle_frame(frame, bool(state))
    parent_var.trace_add('write', callback)
    callback()

# Bind checkboxes/spinboxes to their dependent inputs
bind_toggle(config_var, [merge_inputs, download_inputs, index_inputs, alignment_inputs, realignment_inputs, database_inputs, ncbi_inputs, parental_inputs, strains_inputs])
bind_toggle(bowtie2_var, [alignment_inputs])
bind_toggle(realign_var, [realignment_inputs])
bind_toggle(build_var, [database_inputs])
bind_toggle(snpeff_var, [ncbi_inputs])
bind_toggle(filter_var, [parental_inputs])
bind_toggle(table_var, [strains_inputs])

# -------------------------------
# Confirm / JSON output
# -------------------------------
# This collects all GUI values and writes them to a JSON file in the chosen Main directory.
def collect_children_entries(frame):
    """Helper: from a dynamic inputs_frame, return list of entry values (string)."""
    results = []
    for child in frame.winfo_children():
        # Each child is a row frame; second child is the Entry (index 1) for our patterns
        row_children = child.winfo_children()
        if len(row_children) >= 1:
            # find first Entry in the row
            val = None
            for w in row_children:
                if isinstance(w, ttk.Entry) or isinstance(w, tk.Entry):
                    val = w.get()
                    break
            results.append(val)
    return results

def on_confirm():
    # where to write the config file: main directory if provided, else current working directory
    main_dir = main_dir_var.get().strip() or os.getcwd()
    suggested_name = config_suggestion_var.get().strip() or "config.json"
    config_file_path = os.path.join(main_dir, suggested_name)

    configuration = {
        # Files/paths section
        "paths": {
            "main_directory": main_dir,
            "input_directory": input_dir_var.get().strip() or None,
            "output_directory": output_dir_var.get().strip() or None,
            "temp_directory": temp_dir_var.get().strip() or None,
            "reference_directory": ref_dir_var.get().strip() or None
        },
        # Software choices
        "software": {
            "bowtie2": sw_bowtie2.get(),
            "samtools": sw_samtools.get(),
            "spades": sw_spades.get(),
            "snpeff": sw_snpeff.get(),
            "bwa": sw_bwa.get()
        },
        # Pipeline options
        "configuration_file": config_var.get(),
        "merge": merge_var.get(),
        "download": {
            "n": download_var.get(),
            "assemblies": collect_children_entries(download_inputs)
        },
        "indexing": {
            "n": index_var.get(),
            "assemblies": collect_children_entries(index_inputs)
        },
        "bowtie2": {
            "enabled": bowtie2_var.get(),
            "strains": collect_children_entries(alignment_inputs)
        },
        "realign": {
            "enabled": realign_var.get(),
            "strains": collect_children_entries(realignment_inputs)
        },
        "snps": snps_var.get(),
        "indels": indels_var.get(),
        "build_database": {
            "enabled": build_var.get(),
            "databases": collect_children_entries(database_inputs)
        },
        "SNP_indel_annotation": {
            "enabled": snpeff_var.get(),
            "NCBI": collect_children_entries(ncbi_inputs)
        },
        "filter_by_parental": {
            "enabled": filter_var.get(),
            "parental": collect_children_entries(parental_inputs)
        },
        "table": {
            "enabled": table_var.get(),
            "strains": collect_children_entries(strains_inputs)
        },
        "denovo": denovo_var.get(),
        "compress": compress_var.get(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Write the JSON file, creates main dir if necessary
    try:
        os.makedirs(main_dir, exist_ok=True)
        with open(config_file_path, 'w') as f:
            json.dump(configuration, f, indent=4)
        tk.messagebox.showinfo("Saved", f"Configuration saved to\n{config_file_path}")
        print("Configuration saved to", config_file_path)
    except Exception as e:
        tk.messagebox.showerror("Error saving config", str(e))
        print("ERROR saving configuration:", str(e))

confirm_btn = ttk.Button(scrollable_frame, text="Confirm and Save Config", command=on_confirm)
confirm_btn.pack(pady=14)

# -------------------------------
# Summary, printed to console when started
# -------------------------------
print("=== User's guide ===")
print("1) Use the 'Files/directories paths' section to set a main directory for the output config.")
print("2) Software checkboxes indicate which external tools the pipeline will attempt to call.")
print("3) Spinboxes create dynamic input rows; use Browse to choose files where required.")
print("4) Press 'Confirm and Save Config' to generate the JSON. The file will be written to the main directory.")
print("=======================")

# Start the GUI loop
root.mainloop()
