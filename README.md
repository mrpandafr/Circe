# Circé

*Que chacun puisse interroger les livres, pas seulement les lire.*

*Circé implémente le modèle **Nœud** — deux champs, onze lignes,
[github.com/mrpandafr/noeud](https://github.com/mrpandafr/noeud).
Anciennement publié sous le nom Vector : même modèle, même lignée,
même DOI.*

## Le constat

Un livre fermé garde son sens en otage. Il faut le lire en entier,
deviner le bon mot pour le retrouver.

Circé garde **chaque glyphe du document**, dans l'ordre exact — les
espaces, les retours à la ligne, la ponctuation. Rien n'est découpé,
donc rien ne se perd : la concaténation des nœuds reproduit le fichier
au caractère près.

C'est une simplification autant qu'un gain. Les versions précédentes
segmentaient en phrases, ce qui mangeait les séparateurs et coupait
`art. 7` en deux. Ne jamais couper règle le problème au lieu de le
contourner — et supprime au passage toute dépendance à un segmenteur.

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

## NoeudJSON, la preuve

Nœud est une idée. NoeudJSON est ce qui reste quand l'idée tient
sur un texte réel, moche, jamais nettoyé pour l'occasion.

La preuve, ce n'est pas la théorie qui convainc — c'est le code
testé sur un vrai corpus, avec ses erreurs montrées plutôt que
cachées.

## Un lien porte 1 à n nœuds

Un lien est une liste vivante. Le **premier** nœud est la cible ;
tout ce qui précède qualifie la relation. L'arité est libre, et
plusieurs arités coexistent sans problème dans le même fichier.

**Cible seule** — graphe de transitions pures. L'émergence est
possible, la trace ne l'est pas : arrivé sur un mot fréquent, on ne
sait plus laquelle de ses sorties suivre.
**+ une position** — les occurrences deviennent distinctes, le texte
redevient reconstructible. Minimum pour un document.
**+ une source** — quand plusieurs voix coexistent (dialogue,
annotations). Inutile quand une seule parle.
**+ n'importe quoi d'autre** — langue, confiance, version,
annotateur. Aucun changement à `vector.py` n'est nécessaire : un
qualificateur est un citoyen, pas un champ typé.

Retirer un nœud ne rend pas Nœud plus efficace. Ça change les
questions auxquelles il peut répondre. C'est pour ça que le format
sérialise un lien comme un tableau positionnel et non comme un objet
à clés nommées : nommer `temps` et `source` inventerait des types
que le modèle n'a pas.

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
"Alice" à deux endroits distincts du texte, jamais cités l'un l'autre,
mais bien connectés par le glyphe partagé. (Circé ne segmente plus du
tout : la frontière de phrase est une décision de lecture, prise par
l'observateur sur la ponctuation, jamais inscrite dans le stockage.)

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

## Trois niveaux de lecture

Circé ne jette personne dans un réseau abstrait. On entre par le
lisible, on découvre les recoupements, on descend dans la structure
seulement si on en a besoin.

**1. Lire.** `/docs` liste les documents du corpus, leur taille, leur
vocabulaire. `/extrait DOC` en donne les premiers mots, reconstruits
depuis le graphe.

**2. Recouper.** `/recoupe DOC` montre quels autres documents partagent
du vocabulaire avec celui-ci, classés par poids. `/partage A B` détaille
chaque mot commun **avec la phrase où il apparaît** — pas une affirmation
de ressemblance, la preuve à côté.

**Aucun filtre, aucun seuil.** Un mot pèse l'inverse de sa fréquence :
l'espace et « le » pèsent presque rien, un terme rare pèse lourd, et le
classement émerge tout seul. Rien n'est écarté — le bruit reste visible,
en bas, à sa vraie valeur.

C'est Zipf appliqué tel quel. Les versions précédentes filtraient par
seuils (60 %, trois documents, cinq documents) ; chaque seuil décidait à
la place de la fréquence, et le corpus suivant le prenait en défaut. Le
sens émerge de la fréquence — on ne l'aide pas en écartant d'avance ce
qu'on croit être du bruit.

**3. Explorer.** `/texte`, `/voisins`, `/contexte` — le graphe complet :
les liens d'un nœud, ses occurrences exactes, les documents où il vit,
et la phrase autour de n'importe laquelle de ses apparitions.

Chaque niveau reste utile seul. Personne n'est obligé de descendre.

## Comment

```
python3 circe_encoder.py a.txt b.txt c.txt -o corpus.vjson   # un ou plusieurs
python3 circe_encoder.py fichier.txt   # texte -> graphe NoeudJSON
python3 validateur.py fichier.vjson    # vérifie le format
python3 circe_explorer.py fichier.vjson  # traverse, interroge
```

Trois commandes. Bibliothèque standard. Rien d'autre à installer.

## Pour qui

Pour tous, vraiment. MIT, ouvert, sans laboratoire à remercier.

Surtout pour ceux pris dans le pire — un dossier qu'on n'a pas
choisi, une loi qu'on ne comprend pas, un corpus à affronter seul.

## Développement

- **Jean-Sébastien** — architecture et conception de Nœud/Circé
- **FB** — développement et co-architecture
- **Kage** — expérimentation, mémoire et documentation

## Contributions techniques

- **GPT (OpenAI)** — audit technique, conception et exécution de
  tests adversariaux, revue de robustesse

---

*K1SS Atelier 0 — 24 juillet 2026*
