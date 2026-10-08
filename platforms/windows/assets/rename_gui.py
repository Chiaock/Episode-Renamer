import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.m4v', '.webm', '.ass', '.ssa', '.srt', '.vtt'}
PATTERNS = [
    re.compile(r'S\d{1,3}E(\d{1,3})(?!\d)', re.I),
    re.compile(r'\[(\d{1,3})\]'),
    re.compile(r'\b(?:Episode|EP|E)[ ._-]*(\d{1,3})(?!\d)', re.I),
    re.compile(r'[-_ ](\d{1,3})(?=\s*(?:\[[^\]]*\]\s*)*$)'),
]
SPECIAL = re.compile(r'(?<![a-z])(?:OVA|OAD|Specials?)(?![a-z])[ ._\-\[\]]*(\d{1,3})?', re.I)

root = tk.Tk()
root.title('Episode File Renamer')
root.geometry('900x560')
try:
    app_icon = tk.PhotoImage(file=str(script.parent / 'icon.png'))
    root.iconphoto(True, app_icon)
except tk.TclError:
    pass
folder = tk.StringVar()
title = tk.StringVar()
season = tk.StringVar(value='1')
plan = []

def invalidate(*_):
    plan.clear()
    rename_button.config(state='disabled')
    status.set('Click Preview to check the filenames.')

def browse():
    selected = filedialog.askdirectory(title='Choose your show or season folder')
    if selected:
        folder.set(selected)

def preview():
    invalidate()
    tree.delete(*tree.get_children())
    try:
        directory = Path(folder.get()).expanduser()
        if not folder.get() or not directory.is_dir():
            raise ValueError('Choose a valid folder.')
        name = title.get().strip()
        if not name or name in {'.', '..'} or any(c in name for c in '/\\:*?"<>|'):
            raise ValueError('Enter a valid show title.')
        number = int(season.get())
        if number < 1:
            raise ValueError('Season must be a positive whole number.')
        pending = []
        skipped = 0
        for source in sorted(directory.iterdir()):
            if not source.is_file() or source.suffix.lower() not in EXTENSIONS:
                continue
            special = SPECIAL.search(source.stem)
            episode = int(special.group(1)) if special and special.group(1) else None
            if episode is None:
                for pattern in PATTERNS:
                    match = pattern.search(source.stem)
                    if match:
                        episode = int(match.group(1))
                        break
            if special and episode is None:
                episode = 1
            if episode is None:
                skipped += 1
                continue
            target = source.with_name(f'{name} - S{0 if special else number:02d}E{episode:02d}{source.suffix}')
            if source.name != target.name:
                pending.append((source, target))
        seen = set()
        existing = {p.name.casefold() for p in directory.iterdir()}
        for source, target in pending:
            key = target.name.casefold()
            if key in seen or (key in existing and key != source.name.casefold()):
                raise ValueError(f'Filename conflict: {target.name}\nGive duplicate episodes or specials different numbers.')
            seen.add(key)
        for source, target in pending:
            tree.insert('', 'end', values=(source.name, target.name))
        plan.extend(pending)
        status.set(f'{len(plan)} files ready; {skipped} files skipped because no episode was detected.')
        if plan:
            rename_button.config(state='normal')
    except (ValueError, OSError) as error:
        messagebox.showerror('Cannot preview', str(error))

def rename():
    if not plan or not messagebox.askyesno('Rename files?', f'Rename these {len(plan)} files?'):
        return
    completed = 0
    try:
        # Recheck before starting in case the folder changed after preview.
        for source, target in plan:
            if not source.is_file() or (target.exists() and not source.samefile(target)):
                raise OSError(f'File changed or destination exists: {target.name}')
        for source, target in plan:
            if target.exists() and not source.samefile(target):
                raise OSError(f'Destination exists: {target.name}')
            source.rename(target)
            completed += 1
        messagebox.showinfo('Done', f'Renamed {completed} files.')
    except OSError as error:
        messagebox.showerror('Rename stopped', f'Renamed {completed} files before stopping.\n{error}')
    finally:
        invalidate()

panel = ttk.Frame(root, padding=16)
panel.pack(fill='both', expand=True)
panel.columnconfigure(1, weight=1)
ttk.Label(panel, text='Folder:').grid(row=0, column=0, sticky='w', pady=6)
ttk.Entry(panel, textvariable=folder).grid(row=0, column=1, sticky='ew', padx=8)
ttk.Button(panel, text='Choose folder…', command=browse).grid(row=0, column=2)
ttk.Label(panel, text='Show title:').grid(row=1, column=0, sticky='w', pady=6)
ttk.Entry(panel, textvariable=title).grid(row=1, column=1, columnspan=2, sticky='ew', padx=8)
ttk.Label(panel, text='Season:').grid(row=2, column=0, sticky='w', pady=6)
ttk.Entry(panel, textvariable=season, width=8).grid(row=2, column=1, sticky='w', padx=8)
ttk.Label(panel, text='Episode numbers are preserved. OVA / OAD / Special use season 00.').grid(row=3, column=0, columnspan=3, sticky='w', pady=8)
buttons = ttk.Frame(panel)
buttons.grid(row=4, column=0, columnspan=3, sticky='w', pady=8)
ttk.Button(buttons, text='Preview', command=preview).pack(side='left')
rename_button = ttk.Button(buttons, text='Rename files', command=rename, state='disabled')
rename_button.pack(side='left', padx=8)
tree = ttk.Treeview(panel, columns=('old', 'new'), show='headings')
tree.heading('old', text='Current filename')
tree.heading('new', text='New filename')
tree.column('old', width=420)
tree.column('new', width=380)
tree.grid(row=5, column=0, columnspan=3, sticky='nsew')
panel.rowconfigure(5, weight=1)
scroll = ttk.Scrollbar(panel, orient='vertical', command=tree.yview)
scroll.grid(row=5, column=3, sticky='ns')
tree.configure(yscrollcommand=scroll.set)
status = tk.StringVar(value='Choose a folder and enter the show title and season.')
ttk.Label(panel, textvariable=status, wraplength=820).grid(row=6, column=0, columnspan=3, sticky='w', pady=8)
for variable in (folder, title, season):
    variable.trace_add('write', invalidate)
root.mainloop()
