#!/usr/bin/env python3
"""
circe_encoder.py -- LE point d'entrée unique. Transforme un texte
brut (n'importe quel .txt) en graphe VectorJSON.

Tissage réel, mot par mot, comme exemple.py. Le TEMPS ici est la
POSITION du glyphe (mot) dans le texte -- simple, linéaire, assumé
tel quel. Pour une conversation (Kage), le temps est "quand" en
heures réelles. Pour un texte statique, le temps est "où" dans la
séquence -- le seul analogue honnête, pas une hiérarchie artificielle
de page/paragraphe.

Genèse (comme exemple.py) : le tout premier mot du livre s'auto-lie
au nom du document -- simple, reconnaissable, une seule fois.

Usage :
    python3 circe_encoder.py corpus.txt
    -> écrit corpus.vjson
"""
import sys
import os
import re
from vector import Vector
from vector_json import registre_vers_json


def decouper_mots(texte: str) -> list[str]:
    """CHAQUE glyphe d'une phrase, sans exception -- y compris
    l'espace lui-même. Garantie : "".join(decouper_mots(phrase)) ==
    phrase, toujours, pour une phrase donnée.

    La phrase est l'unité réelle du document -- pas le flux continu
    brut. L'espacement ENTRE deux phrases (la colle de mise en forme)
    n'est pas garanti identique ; le contenu de CHAQUE phrase, lui,
    est préservé au caractère près."""
    return re.findall(
        r"[\wàâäéèêëïîôöùûüçÀÂÄÉÈÊËÏÎÔÖÙÛÜÇ\-']+|[.!?;:]|.",
        texte,
        re.DOTALL
    )


def encoder_fichier(chemin: str, source: str = "lecture") -> dict:
    """Lit un .txt, le tisse mot par mot. Le temps = la position du
    mot dans le texte entier, un compteur qui avance, simplement."""
    with open(chemin, encoding="utf-8") as f:
        texte_brut = f.read()

    phrases = [p.strip() for p in re.split(r"(?<=[.!?])\s+", texte_brut) if p.strip()]

    reg = {}
    def V(name):
        if name not in reg:
            reg[name] = Vector(name)
        return reg[name]

    nom_document = os.path.basename(chemin).rsplit(".", 1)[0]
    doc = V(nom_document)
    src = V(source)
    premier_mot = None
    position = 0

    for phrase in phrases:
        mots = decouper_mots(phrase)
        prec = None
        for mot in mots:
            m = V(mot)
            T = V(f"@{position}")  # préfixe d'un seul caractère --
                                    # élimine la collision avec un mot
                                    # qui serait littéralement un chiffre
                                    # (ex: "7" comme mot ET position 7),
                                    # tout en restant compact

            if premier_mot is None:
                m.links.append((doc, src, m))
                m.seen.append(doc)
                premier_mot = m

            m.seen.append(T)  # toujours -- chaque mot vu à sa position exacte
            if prec is not None:
                prec.links.append((T, src, m))
            prec = m
            position += 1

    return reg


def main():
    if len(sys.argv) < 2:
        print("Usage : python3 circe_encoder.py fichier.txt")
        sys.exit(1)

    chemin = sys.argv[1]
    print(f"Lecture et tissage de {chemin}...")
    reg = encoder_fichier(chemin)
    print(f"{len(reg)} citoyens (mots uniques + positions + document) -- "
          f"chaque mot compte sa position exacte, sans hiérarchie artificielle.")

    sortie = chemin.rsplit(".", 1)[0] + ".vjson"
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(registre_vers_json(reg))
    print(f"Écrit : {sortie}")


if __name__ == "__main__":
    main()
