import tkinter as tk
from tkinter import filedialog
import re

FILEPATH =""

root = tk.Tk() 
root.update()

def select_file():
    global FILEPATH
    file_path = filedialog.askopenfilename()
    if file_path: 
        FILEPATH = file_path
        root.destroy() 
    
def close_window():
    root.destroy()

def findDirectoryPath(path :str) -> str:
    new_path=""
    for i in range(len(re.split('/', FILEPATH))-1):
        new_path+=re.split('/', FILEPATH)[i] + "/"
    return new_path[:-1]

button = tk.Button(root, text="Open the file ocli to work on", command=select_file)
close_button = tk.Button(root, text="Exit", command=close_window)
button.pack()  
close_button.pack()
root.mainloop() 

def copieFile(file_path : str):
    source_file = file_path
    destination_file =re.split(r'\.', file_path)[0] + r"_Copie." + re.split(r'\.', file_path)[1]
    with open(source_file, 'rb') as src, open(destination_file, 'wb') as dest:
        # Lire le contenu du fichier source et écrire dans le fichier de destination
        dest.write(src.read())
    return destination_file

#Now, we will create a copy of this file 
destination_file = copieFile(FILEPATH)

def addCommandInOcli(path : str, cmd : str) :
    with open(path, 'a') as file:
        file.write('\n' + cmd + '\n')

addCommandInOcli(destination_file, "+bd:BATIMENT@[0,20]@d5d5fg5g")