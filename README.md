# Circé

*Que chacun puisse interroger les livres, pas seulement les lire.*

## Le constat

Un livre fermé garde son sens en otage. Il faut le lire en entier,
deviner le bon mot pour le retrouver.

Circé garde le texte intact et le rend interrogeable. Pas résumé.
Traversé.

## Redécouvrir

Chercher n'est plus deviner un mot-clé. C'est demander : qu'est-ce
qui ressemble à ceci, qu'est-ce qui cite cela.

C'est plus que lire. On trouve des chemins qu'on n'avait jamais vus,
dans un texte qu'on croyait déjà connaître.

## Une science ouverte

L'étude lexicale demandait des laboratoires. Elle tient aujourd'hui
dans deux fichiers de moins de cent lignes.

Vérifié sur du texte, sur de la musique, sur un corpus légal de
près de trois mille articles. Le même mécanisme, chaque fois.

## VectorJSON, la preuve

Vector est une idée. VectorJSON est ce qui reste quand l'idée tient
sur un texte réel, moche, jamais nettoyé pour l'occasion.

La preuve, ce n'est pas la théorie qui convainc — c'est le code
testé sur un vrai corpus, avec ses erreurs montrées plutôt que
cachées.

## Boîte noire, boîte transparente

Le graphe — `links`, `seen` — est du code qu'on peut lire et
corriger. Deux bugs y ont été trouvés et réparés en public,
précisément parce que c'était possible de les voir.

L'angle sémantique (BGE-M3) est une boîte noire neuronale. Zéro bug
trouvé — pas par perfection, mais parce qu'on ne peut inspecter que
sa sortie, jamais son raisonnement. On l'utilise faute de mieux, pas
comme idéal.

## Ce que ça enlève

Un juriste qui ne feuillette plus. Un citoyen qui retrouve la loi
qui le concerne sans payer un traducteur.

Pas un gain de temps. Un poids en moins — celui de devoir se
souvenir où chercher.

## Comment

```
python3 circe_encoder.py            # texte -> graphe VectorJSON
python3 validateur.py fichier.vjson # vérifie le format
python3 circe_explorer.py fichier.vjson  # traverse, interroge
```

Trois commandes. Bibliothèque standard. Rien d'autre à installer.

## Pour qui

Pour tous, vraiment. MIT, ouvert, sans laboratoire à remercier.

Surtout pour ceux pris dans le pire — un dossier qu'on n'a pas
choisi, une loi qu'on ne comprend pas, un corpus à affronter seul.

---

*K1SS Atelier 0 — 23 juillet 2026*
