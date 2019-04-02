# data.gouv.fr - édition papier

Ce code sert à produire une édition papier de **data.gouv.fr**.

Il a été écrit pour le 1er Avril 2019, car il s'agissait bien d'un poisson d'avril !

## Principe

Les données CSV sont récupérées depuis data.gouv.fr et importées dans une base postgresql.

Un script python génère un code LaTeX à partir de ces données. (make_latex.py)

Le rendu final, au format PDF est produit par xelatex. (make_pdf.sh)

## Le contenu

Seuls les jeux de données ayant au moins une réutilisation indiquée sur data.gouv.fr sont inclus dans ce premier Tome.

Ils sont regroupés en trois chapitres:
- les données de référence
- les données provenant de services publics certifiés
- les autres données

Pour chaque jeu de donnée, le producteur est décrit, puis le jeu de données (avec un QR code pour accéder au site web), puis une listes d'autres jeux de données publiés par ce producteur est fournie.

L'index final est construit à partir des mot-clés indiqués dans les métadonnées des jeux de données.

## Le résultat

Le "jeu de données" est référencé sur https://www.data.gouv.fr/fr/datasets/5ca1bab38b4c41179d661a7a
