# Méthode directe

Ce dépôt contient l’implémentation et les expériences liées à la **méthode directe** pour l’énumération des vecteurs de Lorenz non dominés dans un problème de sac à dos multiobjectif, à l’aide d’une scalarisation de type **OWA** (Ordered Weighted Averaging).

---

## Contenu du dépôt

- `fonctions.py`  
  Contient l’implémentation des modèles d’optimisation :
  - **P1** : problème OWA linéarisé permettant d’obtenir un vecteur de Lorenz optimal pour une pondération donnée.
  - **PL** : problème permettant d’énumérer successivement les vecteurs de Lorenz non dominés à partir des solutions déjà trouvées.
  - Fonctions utilitaires pour la génération des pondérations et l’extraction des vecteurs de Lorenz.

- `experiments_direct.py`  
  Script principal pour lancer les expériences numériques de la méthode directe.
  Il permet :
  - de fixer le nombre d’objets `n` et le nombre d’objectifs `p`,
  - de tester différentes familles de pondérations OWA (`linéaire`, `normalisée`, `géométrique`, `aléatoire`),
  - de mesurer les temps de calcul et le nombre de vecteurs de Lorenz non dominés.

- `data/`  
  Dossier contenant les instances du problème (fichiers `.dat`).

- `results/`  
  Dossier contenant les fichiers CSV générés lors des expériences (temps de calcul, nombre de vecteurs de Lorenz, pondérations utilisées).

---

## Dépendances

Le projet est écrit en **Python 3** et nécessite les bibliothèques suivantes :

- `gurobipy` (solveur Gurobi, avec licence valide)
- `numpy`
- `matplotlib` (pour les visualisations)

---

## Arguments

Le script `experiments_direct.py` accepte les arguments suivants :

- `--data DATA`  
  Chemin vers le fichier d’instance au format `.dat`.
- `--n N`
  Nombre d’objets considérés. Le script utilise uniquement les n premiers objets du fichier d’instance.
- `--p P`
  Nombre d’objectifs considérés. Le script utilise uniquement les p premiers objectifs du fichier d’instance.
- `--seed SEED`
  Graine du générateur aléatoire, utilisée pour assurer la reproductibilité des pondérations OWA aléatoires.
- `--random-omega RANDOM_OMEGA`
  Nombre de pondérations OWA aléatoires supplémentaires à générer, en plus des familles de pondérations de base (linéaire, normalisée, géométrique).
- `--verbose`
  Affiche le détail des solutions trouvées pendant l’exécution.

---

## Lancement des expériences

Mettez-vous d'abord dans le dossier `methode_directe/` :
```bash
  cd methode_directe
```

Exemple de commande pour lancer la méthode directe sur une instance donnée :
```bash
python codes/experiments_direct.py --data ../data/2KP200-TA-0.dat --n 20 --p 3 --random-omega 1
```