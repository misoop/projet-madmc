# Génération de l’ensemble des points non dominés au sens de Lorenz pour le problème de sac à dos multi-objectifs

Ce dépôt contient le code et les résultats associés au projet de MADMC portant sur la résolution d’un problème de sac à dos multiobjectif.

Deux approches sont étudiées et comparées expérimentalement :
- une **méthode indirecte**, basée sur l’énumération des points de Pareto non dominés ;
- une **méthode directe**, visant à générer directement les vecteurs de Lorenz non dominés.

L’objectif du projet est de comparer ces deux méthodes en termes de **temps de calcul**, de **nombre de solutions non dominées** et de **scalabilité**.

---

## Contributeurs

- Michelle Song
- Mohamed Najem

---

## Organisation du projet

```text
projet_madmc/
├── data/
├── methode_directe/
├── methode_indirecte/
├── bibliographie/
├── Rapport.pdf
├── projetMADMC.pdf
└── README.md
```

---

## Remarques

- Pour exécuter une des deux méthodes, allez directement dans le dossier (`methode_indirecte`/`methode_directe`) et lisez le README pour plus d'informations (scripts à lancer). 
- L'énoncé du projet se trouve dans le fichier `projetMADMC.pdf`
- Le rapport est dans `Rapport.pdf`