# Circé

*Que chacun puisse interroger les livres, pas seulement les lire.*

## Le constat

Un livre fermé garde son sens en otage. Il faut le lire en entier,
deviner le bon mot pour le retrouver.

Circé garde chaque glyphe d'une phrase, dans l'ordre exact — y
compris l'espace lui-même. La phrase est l'unité réelle du document ;
son contenu ne perd rien. Seul l'espacement entre deux phrases (la
mise en forme, pas le sens) n'est pas garanti identique.

## Redécouvrir

Chercher n'est plus deviner un mot-clé. C'est demander : qu'est-ce
qui ressemble à ceci, qu'est-ce qui cite cela.

C'est plus que lire. On trouve des chemins qu'on n'avait jamais vus,
dans un texte qu'on croyait déjà connaître.

## Une science ouverte

L'étude lexicale demandait des laboratoires. Elle tient aujourd'hui
dans six fichiers Python, moins de 500 lignes au total, bibliothèque
standard.

Vérifié sur du texte, sur de la musique, sur un corpus légal de
près de trois mille articles, sur un livre entier. Le même
mécanisme, chaque fois.

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

## Pourquoi et comment utiliser BGE-M3

**Pourquoi** : le graphe seul trouve déjà plus qu'il n'y paraît — deux
textes qui partagent un même mot sont réellement reliés, visible via
`seen` sur ce mot, sans aucune citation explicite entre eux. Vérifié :
"Alice" dans deux phrases distinctes, jamais citées l'une l'autre,
mais bien connectées par le mot partagé. (Circé ne détecte plus les
frontières de paragraphe — seule la phrase est une unité reconnue.)

Ce qu'il rate, précisément : la ressemblance **sans mot commun** — un
synonyme, une paraphrase, deux phrases sur la même idée dites
autrement. Là, BGE-M3 apporte un angle que le graphe seul n'a pas.

**Comment**, deux usages distincts :

Chercher après coup, sans toucher au graphe :
```bash
python3 circe_explorer.py corpus.vjson vecteurs.npy
circe> /near "un texte exact déjà présent dans le graphe"
```

Tisser automatiquement pendant la construction, avec une source
honnêtement étiquetée comme venant du modèle, jamais confondue avec
une citation humaine :
```bash
python3 tissage_semantique.py
```
(à adapter : charge tes propres textes, ajuste le seuil de
similarité selon ce que tu juges pertinent).

`pip install sentence-transformers --break-system-packages` est
requis pour les deux — absent, ces commandes échouent avec un
message clair plutôt qu'un plantage silencieux.

## Ce que ça enlève

Un juriste qui ne feuillette plus. Un citoyen qui retrouve la loi
qui le concerne sans payer un traducteur.

Pas un gain de temps. Un poids en moins — celui de devoir se
souvenir où chercher.

## Comment

```
python3 circe_encoder.py fichier.txt   # texte -> graphe VectorJSON
python3 validateur.py fichier.vjson    # vérifie le format
python3 circe_explorer.py fichier.vjson  # traverse, interroge
```

Trois commandes. Bibliothèque standard. Rien d'autre à installer.

## Pour qui

Pour tous, vraiment. MIT, ouvert, sans laboratoire à remercier.

Surtout pour ceux pris dans le pire — un dossier qu'on n'a pas
choisi, une loi qu'on ne comprend pas, un corpus à affronter seul.

---

*K1SS Atelier 0 — 23 juillet 2026*
