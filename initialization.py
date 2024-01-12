import tkinter as tk
from tkinter import filedialog
import re
from functools import partial

FILEPATH = ""
COPIED_FILEPATH = ""

def select_file(root):
    global FILEPATH
    file_path = filedialog.askopenfilename()
    if file_path: 
        FILEPATH = file_path
        root.destroy() 
    
def close_window(root):
    root.destroy()

def findDirectoryPath() -> str:
    new_path=""
    for i in range(len(re.split('/', FILEPATH))-1):
        new_path+=re.split('/', FILEPATH)[i] + "/"
    return new_path[:-1]

def copieFile(file_path : str):
    source_file = file_path
    destination_file =re.split(r'\.', file_path)[0] + r"_Copie." + re.split(r'\.', file_path)[1]
    with open(source_file, 'rb') as src, open(destination_file, 'wb') as dest:
        # Lire le contenu du fichier source et écrire dans le fichier de destination
        dest.write(src.read())
    return destination_file

#Now, we will create a copy of this file 

def addCommandInOcli(cmd : str) :
    with open(COPIED_FILEPATH, 'a') as file:
        file.write('\n' + cmd + '\n')

def main():
    root = tk.Tk() 
    root.update()

    button = tk.Button(root, text="Open the OCLI file to work on", command=partial(select_file,root))
    close_button = tk.Button(root, text="Exit", command=partial(close_window,root))
    button.pack()  
    close_button.pack()
    root.mainloop() 

    global COPIED_FILEPATH
    COPIED_FILEPATH = copieFile(FILEPATH)

# addCommandInOcli(destination_file, "+bd:BATIMENT@[0,20]@d5d5fg5g")