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
                    if i+1 < len(lst) and nameLst[i] != lst[i+1]:
                        test = False
                if test and len(lst) == 6: #Only keep the rack and not the device
                    print(lst[5])
                    childrens.append(line) #Can be convert in Rack maybe ?
        print(len(childrens))
    #TODO : enlever les objets et voir les modifications -> est ce qu'on ne recréerait pas un jumeau numérique ?

getChildren("a")