def getChildren(room):
    path = "C:\\Users\\Utilisateur\\Documents\\IMT atlantique\\OGrEE_NLP\\DEMO_BASIC.ocli"
    childrens = []

    #nameLst = room.name
    nameLst = ["P", "BASIC", "A", "R1"]
    with open(path, encoding = 'utf-8') as file:
        for line in file.readlines():
            if line[0] == "+":
                lst = line.split("/")
                test = True
                for i in range(len(nameLst)):
                    if nameLst[i] != lst[i+1]:
                        test = False
                if test:
                    childrens.add(line) #A voir comment on traite la ligne, si on al convertit en Rack
    #TODO : enlever les objets et voir les modifications -> est ce qu'on ne recréerait pas un jumeau numérique ?

getChildren("a")