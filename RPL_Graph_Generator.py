import glob
import os
from shutil import move as smove
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

DEBUG = False
_converter = True
_BackupPath = False
_RemoveMetters = False
_OneFile = False
_BackupMeters = False


def _debug(var):
    global DEBUG
    if DEBUG:
        print(var)


def main():
    global root
    root = Root()
    root.mainloop()


def change_debug_mode():
    global DEBUG
    if DEBUG:
        _debug("Debug mode Off")
        DEBUG = False
        root.submenu.entryconfig(0, label='Turn Debug On')
    else:
        DEBUG = True
        _debug("Debug mode On")
        root.submenu.entryconfig(0, label='Turn Debug Off')


def change_converter():
    global _converter
    if _converter:
        _debug("Converter Off")
        _converter = False
        root.submenu.entryconfig(1, label='Turn Converter On')
    else:
        _converter = True
        _debug("Converter On")
        root.submenu.entryconfig(1, label='Turn Converter Off')


def change_RemoveMetters():
    global _RemoveMetters
    if _RemoveMetters:
        _RemoveMetters = False
        _debug(f"Remove Metters {_RemoveMetters}")
        root.e_medidores.configure(state=DISABLED)  #  Precisa passar a classe como argumento
    else:
        _RemoveMetters = True
        _debug(f"Remove Metters {_RemoveMetters}")
        root.e_medidores.configure(state=NORMAL)  # Precisa passar a classe como argumento


def change_BackupPath():
    global _BackupPath
    if _BackupPath:
        _BackupPath = False
        root.cb_backup_meters.configure(state=DISABLED)
        _debug(f"Backup Path {_BackupPath}")
    else:
        _BackupPath = True
        root.cb_backup_meters.configure(state=NORMAL)
        _debug(f"Backup Path {_BackupPath}")


def change_BackupMeters():
    global _BackupMeters
    if _BackupMeters:
        _BackupMeters = False
        _debug(f"Backup Meters {_BackupMeters}")
    else:
        _BackupMeters = True
        _debug(f"Backup Meters {_BackupMeters}")


def togle_one_file():
    global _OneFile
    if _OneFile:
        _OneFile = False
        _debug(f"One File {_OneFile}")
    else:
        _OneFile = True
        _debug(f"One File {_OneFile}")


def processFile(file_input):
    global _BackupPath
    global _RemoveMetters
    fileOutput = 'out_' + os.path.basename(file_input)
    _debug(f"Opening {file_input}")
    with open(file_input, 'r') as f:
        _debug(f"Creating {fileOutput}")
        with open(fileOutput, 'w') as g:
            matches = False
            for line in f:
                # Add configs at the beginning
                line = re.sub('{',
                              '{\nrankdir = RL\n'
                              'bgcolor = white\n'
                              'nodesep=0.3\n'
                              'node [shape=box, style=filled]\n'
                              'edge [style=dashed]'
                              '//"8077:123C" [style=filled,color=red]',
                              line, re.IGNORECASE)  # .rstrip()
                # Remove clutter
                line = re.sub(r"(FDA\d::([a-zA-Z0-9]{1,3}):([a-zA-Z0-9]{1,3}):\d{4}:)", "", line, re.IGNORECASE)
                # Add Backup Routes
                if _BackupPath:
                    line = re.sub(r"\" \n", "\" [label=B, color=red]\n", line)
                    if not _BackupMeters:
                        result = re.search(r"> \"40", line)
                        if result:
                            line = ""
                # Remove Meters
                if _RemoveMetters:
                    full_string = root.e_medidores.get()
                    results = re.findall("[0-9]{4}", full_string)
                    for meter in results:
                        result = re.search(fr"\t\"{meter}", line)
                        if result:
                            line = ""
                            matches = True
                _debug(line)
                g.writelines(line)
            if not matches and _RemoveMetters:
                root.warning_box("Warning", "No matches found!")
    f.close()
    g.close()
    if _converter:
        print("Converting " + file_input)
        filePS = fileOutput[:-4] + '.ps'
        filePNG = fileOutput[:-4] + '.png'
        cmd1 = '.\dot -Tps2 {0} -o {1}'.format(fileOutput, filePS)
        cmd2 = 'gswin64c -o {0} -sDEVICE=pngalpha {1} > nul'.format(filePNG, filePS)
        # cmd3 = 'del {0} && del {1} && move {2} proccessed > nul'.format(fileOutput, filePS, file_input)
        cmd3 = 'del {0} && del {1} > nul'.format(fileOutput, filePS)
        _debug("Generating dot file...")
        os.system(cmd1)
        _debug("Generating PNG file...")
        os.system(cmd2)
        _debug(f"Moving {filePNG} file to {os.path.dirname(file_input)}\\RPL Graph Out")
        smove(f".\\{filePNG}", os.path.dirname(file_input)+f"\\RPL Graph Out\\{filePNG}")   #  Fixme: os.getcwd()
        _debug(f"Moving {os.path.basename(file_input)} file to {os.path.dirname(file_input)}\\RPL Graph Proccessed")
        smove(file_input, os.path.dirname(file_input)+f"\\RPL Graph Proccessed\\{os.path.basename(file_input)}")
        _debug("Cleaning up base files...")
        os.system(cmd3)


def create_folders(path):
    if not os.path.exists(path+'\\RPL Graph Out'):
        _debug(f"Creating {path}+\\RPL Graph Out")
        os.makedirs(path+'\\RPL Graph Out')
    if not os.path.exists(path+'\\RPL Graph Proccessed'):
        _debug(f"Creating {path}+\\RPL Graph Proccessed")
        os.makedirs(path+'\\RPL Graph Proccessed')


def run():
    file_or_dir = root.e1.get()
    _debug(file_or_dir)
    if os.path.isfile(file_or_dir):
        _debug("File Found")
        create_folders(os.path.dirname(file_or_dir))
        if file_or_dir.lower().endswith('.txt'):
            processFile(file_or_dir)
        else:
            _debug("File must be .txt format!")
            root.warning_box("Warning", "File must be .txt format!")
    elif os.path.isdir(file_or_dir):
        _debug("Directory Found")
        create_folders(file_or_dir)
        list_files = []
        for file in glob.glob(file_or_dir+"\\*.txt"):
            _debug(file)
            list_files.append(file)
        if len(list_files) > 0:
            for item in list_files:
                processFile(item)
        else:
            root.warning_box("Warning", "No .txt files found in this folder!")
            _debug("No .txt files found in this folder!")
    else:
        _debug("File or path not Found!")
        root.warning_box("Warning", "File or path not found!")


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("RPL Graph Generator")
        self.geometry("355x200+200+200")
        self.resizable(0, 0)
        column = 5
        row = 5
        pad = 6
        self.cb_medidores = Checkbutton(self, command=change_RemoveMetters, text="Remove Meters:", width=14)
        self.cb_medidores.grid(row=row-1, column=column, ipadx=pad+6, ipady=pad, sticky=W)
        self.e_medidores = Entry(self, width=28)
        self.e_medidores.grid(row=row-1, column=column+1, padx=pad, pady=pad+2, columnspan=2)
        self.e_medidores.insert(0, "4004, 4003, ...")
        self.e_medidores.configure(state=DISABLED)
        self.cb_backup = Checkbutton(self, command=change_BackupPath, text="Show Backup Path")
        self.cb_backup.grid(row=row, column=column, ipadx=pad+12, ipady=pad, sticky=W)
        self.cb_backup_meters = Checkbutton(self, command=change_BackupMeters, text="Accept Meters as Backup")
        self.cb_backup_meters.grid(row=row, column=column+1, ipadx=pad, ipady=pad, sticky=W, columnspan=2)
        self.cb_backup_meters.configure(state=DISABLED)
        self.e1 = Entry(self, width=40, fg="grey", validate="focusin", vcmd=self.clear_entry)
        self.e1.grid(row=row+1, column=column, padx=pad+6, pady=pad, sticky=W, columnspan=2)
        self.e1.insert(0, "File or Folder full path...")
        self.button_search = ttk.Button(self, text="Search", command=self.file_dialog)
        self.button_search.grid(row=row+1, column=column+2, sticky=W)
        self.rb_var = IntVar()
        self.rb_onefile = Radiobutton(self, text="Pick a file.",
                                      variable=self.rb_var, value=1, command=togle_one_file)  # command
        self.rb_allfiles = Radiobutton(self, text="Run on all files from folder.",
                                       variable=self.rb_var, value=0, command=togle_one_file)
        self.rb_allfiles.grid(row=row + 2, column=column+1, padx=pad, pady=pad, columnspan=2)  # command
        self.rb_onefile.grid(row=row+2, column=column, ipadx=pad)
        self.button_run = ttk.Button(self, text="Run", command=run, width=30)
        self.button_run.grid(row=row+4, column=column, columnspan=3, padx=pad, pady=pad+5)
        self.menu_bar = Menu(self)
        self.submenu = Menu(self.menu_bar, tearoff=0)
        self.submenu.add_command(label=f"Turn Debug On", command=change_debug_mode)
        self.submenu.add_command(label=f"Turn Converter Off", command=change_converter)
        self.menu_bar.add_cascade(label="Menu", menu=self.submenu)
        self.config(menu=self.menu_bar)

    def file_dialog(self):
        if _OneFile:
            filename = filedialog.askopenfilename(parent=self,
                                                  initialdir=os.path.dirname(os.getcwd()),
                                                  title="Selecione um arquivo .txt do Coletor",
                                                  filetype=(('Text files', '*.txt'), ('All files', '*.*')))
            self.e1.delete(0, END)
            self.e1.configure(fg="black")
            self.e1.insert(0, str(filename))
        elif not _OneFile:
            pathname = filedialog.askdirectory(parent=self,
                                               initialdir=os.path.dirname(os.getcwd()),
                                               title="Selecione um arquivo .txt do Coletor",)
            self.e1.delete(0, END)
            self.e1.configure(fg="black")
            self.e1.insert(0, str(pathname))

    def warning_box(self, title, text):
        messagebox.showinfo(title, text, parent=self)

    # def one_file_off(self):
    #     self.e1.configure(state=DISABLED)
    #     self.button['state'] = 'disabled'
    # global _OneFile = False

    # def all_files_off(self):
    #     self.e1.configure(state=NORMAL)
    #     self.button['state'] = 'normal'

    def clear_entry(self):
        self.e1.delete(0, END)
        self.e1.configure(fg="black")


if __name__ == '__main__':
    main()
