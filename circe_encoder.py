#!/usr/bin/env python3
"""
circe_encoder.py -- LE point d'entrée unique. Transforme un texte
brut (n'importe quel .txt) en graphe VectorJSON.

Tissage RÉEL, mot par mot, comme exemple.py (le vrai vector.py) :
chaque mot est un citoyen, une phrase est une chaîne de liens
(temps, source, cible). Les mots répétés se déduplique naturellement
par identité de contenu -- pas un accident, la propriété centrale
de Vector.

Usage :
    python3 circe_encoder.py corpus.txt
    -> écrit corpus.vjson
"""
import sys
import re
from vector import Vector
from vector_json import registre_vers_json


def decouper_mots(texte: str) -> list[str]:
    """Mots et ponctuation forte comme citoyens séparés -- rien perdu."""
    return re.findall(r"[\wàâäéèêëïîôöùûüçÀÂÄÉÈÊËÏÎÔÖÙÛÜÇ\-']+|[.!?;:]", texte)


def encoder_fichier(chemin: str, source: str = "lecture") -> dict:
    """Lit un .txt, tisse mot par mot, DANS des phrases, groupées par
    PARAGRAPHE. Le temps est le paragraphe -- pas une position plate
    par phrase (jamais réutilisée, un citoyen sans vraie raison
    d'être), mais une vraie unité partagée par tous les mots qui s'y
    trouvent, exactement comme une date chez Kage est réutilisée par
    tout ce qui s'y passe."""
    with open(chemin, encoding="utf-8") as f:
        texte_brut = f.read()

    paragraphes = [p.strip() for p in re.split(r"\n\s*\n", texte_brut) if p.strip()]
    print(f"{len(paragraphes)} paragraphes trouvés.")

    reg = {}
    def V(name):
        if name not in reg:
            reg[name] = Vector(name)
        return reg[name]

    for num_para, paragraphe in enumerate(paragraphes):
        T_paragraphe = V(f"paragraphe_{num_para}")  # réutilisé par tous les mots du paragraphe
        src = V(source)
        phrases = [p for p in re.split(r"(?<=[.!?])\s+", paragraphe) if p.strip()]
        for phrase in phrases:
            mots = decouper_mots(phrase)
            prec = None
            for mot in mots:
                m = V(mot)
                if prec is not None:
                    prec.links.append((T_paragraphe, src, m))
                    m.seen.append(T_paragraphe)
                prec = m
    return reg


def main():
    if len(sys.argv) < 2:
        print("Usage : python3 circe_encoder.py fichier.txt")
        sys.exit(1)

    chemin = sys.argv[1]
    print(f"Lecture et tissage de {chemin}...")
    reg = encoder_fichier(chemin)
    print(f"{len(reg)} citoyens (mots uniques + repères de paragraphe) -- "
          f"la répétition du langage dédoublonne d'elle-même, et chaque "
          f"paragraphe-temps est réutilisé par tous les mots qui s'y trouvent.")

    sortie = chemin.rsplit(".", 1)[0] + ".vjson"
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(registre_vers_json(reg))
    print(f"Écrit : {sortie}")


if __name__ == "__main__":
    main()
