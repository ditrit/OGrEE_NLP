# Fonctionnement du solver

## Préface
Un solver est un algorithme développé dans le but précis de donner une solution à un problème. Le problème peut être de tout type. 
### Principe d'un modèle
Pour résoudre le problème on identifie dans ce dernier les caractéristiques suivantes :

 - Une fonction objectif, c'est à dire une fonction qui définit l'objectif à atteindre.
 - Les variables du problème
 - Les données du problème
 - Les contraintes auxquelles sont soumises les variables
 
**Exemple du problème du sac à dos** : Le (très célèbre) problème du sac à dos se définit comme suit, 
![sac à dos](https://upload.wikimedia.org/wikipedia/commons/f/fd/Knapsack.svg)
On a un sac à dos capable de porter jusqu'à 15kg et on souhaite y mettre des objets de sorte d'avoir la plus grande valeur dans le sac sans dépasser 15kg.
#### Données
- n le nombre d'objets
- p~i~ le poids de l'objet i
- v~i~ la valeur de l'objet i
#### Variables
Pour savoir si un objet est effectivement dans le sac, on lui associera un bouléen comme suit :
$$ x_i=\begin{cases}  
1 \;si\;l'objet\;i\;est\;dans\;le\;sac\\  
0\;sinon\\  
\end{cases} $$
#### Objectif
On cherche donc simplement $$max(\sum_{i=1}^{n} v_i x_i)$$
#### Contraintes
Il faut ensuite vérifier la contrainte de poids :
$$\sum_{i=1}^{n} p_i x_i\leq 15$$

---
Une fois toutes ces caractéristiques identifiées, on dit que le problème est modélisé, c'est à dire qu'on a toutes les informations nécessaires pour le résoudre et qu'on peut donner ces informations à un algorithme spécialisé dans la résolution de problèmes.

## Choix du solver
Puisque le langage de programmation est **Pyhton** le choix du solver s'est assez vite dirigé vers **Pulp** qui est une librairie *Open Source*  permettant la résolution de problèmes très populaire et bien documentée. 
Le seul inconvénient de **Pulp** est que la traite les problèmes en programmation linéaire. C'est à dire que toutes les définitions de contraintes ou d'objectif doivent dépendre **linéairement** des variables du problème.
**Exemple** : Si on cherche à placer des points dans l'espace, ce qui veut dire que les coordonnées des points à placer sont variables, on ne peut pas travailler avec les distances euclidiennes car : $$d(p_1,p_2) = \sqrt{(x_1-x_2)^2+(y_1-y_2)^2}$$
Ce qui dépend quadratiquement de x~1~, x~2~, y~1~ et y~2~.
## Modélisation du problème
Comme dit plus tôt, afin de résoudre le problème, il faut le modéliser linéairement pour qu'il soit exploitable par **Pulp**.
### Données

 1. Coordonnées des coins de la salle
 2. Dimensions de la salle
 3. Position, rotation et dimensions des objets déjà présents dans la salle
 4. Dimensions du racks à poser
 ### Variables
 5. Position du coin inférieur droit du rack.
 Pour simplifier le problème, on définira les coordonnées des quatres coins du rack à partir de la position du coin inférieur droit, des dimensions du rack et de sa clearance. 
Ces points sont calculés grâce à la fonction ***set_vertices()***
### Objectif
Pour avoir un objectif, on définit d'abord un *point cible*, un point vers lequel notre rack doit se rapprocher le plus possible.
On définit ainsi un distance linéaire pour se rapprocher d'un point $$p_1 = (x_1,y_1)\newline d(p,p_1)=d_x+d_y\;telle\;que : \newline \begin{cases}  
d_x\geq x-x_1\\  
d_x\geq x_1-x\\  
d_y\geq y-y_1\\  
d_y\geq y_1-y\\
\end{cases}  $$
On vient en faite de définir la norme 1 puisque $$d_x = |x-x_1|\newline d_y = |y-y_1|$$de manière linéaire (la fonction *valeur absolue* n'étant pas linéaire).
On peut donc définir l'objectif : $$ z = min(d(p,p_1))$$
C'est la fonction ***aim_point***
### Contraintes
#### Le rack reste à l'intérieur de la salle
On suppose que les salles utilisées sont convexes ainsi on a la propriété suivante pour un polygone ***P*** convexe : 
Pour tous *p~1~, p~2~* des sommets de ***P*** et pour tout point *p*,
$$p\in P \Leftrightarrow (y-y_1)*(x_2-x_1)-(x-x_1)*(y_2-y_1)\geq0$$
**Remarque** : Cette propriété de semble fonctionner que pour les bornes supérieures de la salle, le rack peut dépasser les bornes inférieures.
Cette contrainte est réalisée grâce à la méthode ***contraintWithin***
### Le rack se colle à un rack déjà présent
Pour coller un rack, on positionne le point cible dans le rack auquel on veut coller notre rack. Ensuite, le rack se colle par une contrainte de non-collision.
Cette contrainte fonctionne comme suit : Si un coin du rack est assez proche d'un côté du rack, ce dernier est collé on lui donnant des coordonnées appartenant au segment de droite du rack cible.
Les segments sont calculés avec ***ifThen_y_and_x_eq*** et la propriété de collage se fait par ***set_positionning_problem***.
## Affichage du résultat
La méthode ***set_positionning_problem*** se charge de créer le problème à partir du rack1 (rack cible), rack2 (rack à placer) et de la salle dans laquelle se trouvent les racks. On donne également un point cible qui doit se trouver dans un rack pour le placer au plus proche. Une fois que tous ces arguments sont donnés, la fonction renvoie les coordonnées du point en bas à droite du rack à placer.

 
