# Projet MADMC – Partie 2 : Méthode indirecte

Ce README décrit uniquement la Partie 2 du projet MADMC.
Cette partie correspond à l’implémentation de la méthode indirecte
pour le problème du sac à dos multi-objectifs en maximisation.

La méthode indirecte consiste à générer des solutions Pareto non dominées
par programmation dynamique, puis à filtrer ces solutions afin d’obtenir
les solutions Lorenz non dominées.

---

## Organisation des fichiers

### data/madmcprojet_DATA.txt
Fichier de données contenant les objets du problème.
Chaque objet est décrit par un poids et plusieurs valeurs d’objectifs.
Ce fichier est uniquement lu par le code et n’est pas exécuté.

---

### src/data_loader.py
Lit le fichier de données et extrait :
- les poids des objets,
- les vecteurs d’objectifs,
- la capacité du sac à dos.
Ce fichier n’est pas exécuté directement.

---

### src/dominance.py
Contient les fonctions de dominance :
- dominance de Pareto,
- dominance de Lorenz,
- filtrage des solutions dominées.
Ce fichier n’est pas exécuté directement.

---

### src/dp_indirect.py
Implémente la programmation dynamique multi-objectifs utilisée
dans la méthode indirecte.
Ce fichier n’est pas exécuté directement.

---

## Fichiers exécutables

### src/main_indirect.py
Script principal de la Partie 2.

Il permet de :
- charger les données,
- exécuter la méthode indirecte,
- afficher les solutions Pareto non dominées,
- afficher les solutions Lorenz non dominées,
- afficher des statistiques.

Commande d’exécution : python -m src.main_indirect
 

Les paramètres n_items (nombre d’objets) et n_obj (nombre d’objectifs)
peuvent être modifiés directement dans ce fichier.

---

### src/experiments_indirect.py
Script d’expérimentation et d’analyse de complexité.

Il permet de :
- tester plusieurs valeurs de n_items et n_obj,
- mesurer le temps de calcul,
- compter le nombre de solutions générées,
- compter le nombre de solutions Pareto non dominées,
- compter le nombre de solutions Lorenz non dominées,
- interrompre le calcul au-delà d’un timeout fixé à 1h30.

Commande d’exécution : python -m src.experiments_indirect


---

### src/plots_indirect.py
Script de visualisation des résultats.

Il génère des graphes représentant :
- toutes les solutions candidates générées par la programmation dynamique,
- les solutions Pareto non dominées,
- les solutions Lorenz non dominées.

Commande d’exécution : python -m src.plots_indirect


---

## Environnement

Le projet nécessite :
- Python version 3.9 ou supérieure,
- la bibliothèque matplotlib pour la visualisation.

Installation de la dépendance : pip install matplotlib




## Remarque sur la complexité

La méthode indirecte repose sur une programmation dynamique multi-objectifs.
Le temps de calcul augmente rapidement avec le nombre d’objets et le nombre
d’objectifs. Pour certaines instances de grande taille, le calcul peut dépasser
le temps limite fixé, ce qui est attendu compte tenu de la complexité combinatoire
du problème.


