#!/usr/bin/env python3
"""
circe_encoder.py -- transforme un ou plusieurs textes en graphe Nœud.

Chaque glyphe devient un nœud, la chaîne ne s'interrompt jamais, aucune
segmentation : la concaténation des nœuds reproduit chaque fichier au
caractère près.

Un lien porte [cible, position, document]. Le document remplace l'ancien
qualificateur "lecture" : celui-ci était constant, donc ne portait aucune
information. Le document, lui, est partagé par tous les liens qu'il
contient -- un qualificateur ne mérite d'être un nœud que s'il est
partagé.

Plusieurs fichiers peuvent être tissés dans le MÊME graphe. Les glyphes
communs se rejoignent naturellement : c'est ce qui rend les recoupements
lisibles.

Usage :
    python3 circe_encoder.py corpus.txt
    python3 circe_encoder.py a.txt b.txt c.txt -o corpus.vjson
"""
import sys
import os
import re
from noeud import Noeud
from noeud_json import registre_vers_json


def decouper(texte: str) -> list[str]:
    """CHAQUE glyphe, sans exception -- espaces, retours à la ligne,
    ponctuation. La concaténation reproduit le texte au caractère près."""
    return re.findall(
        r"[\wàâäéèêëïîôöùûüçÀÂÄÉÈÊËÏÎÔÖÙÛÜÇ\-']+|[.!?;:]|.",
        texte,
        re.DOTALL,
    )


def nom_document(chemin: str) -> str:
    return os.path.basename(chemin).rsplit(".", 1)[0]


def encoder(chemins: list[str]) -> dict:
    """Tisse un ou plusieurs fichiers dans un seul registre."""
    reg = {}
    def V(nom):
        if nom not in reg:
            reg[nom] = Noeud(nom)
        return reg[nom]

    for chemin in chemins:
        with open(chemin, encoding="utf-8") as f:
            texte = f.read()
        doc = V(nom_document(chemin))
        prec = None
        for position, glyphe in enumerate(decouper(texte)):
            g = V(glyphe)
            # La position est nommée par son document : la position 12
            # d'Alice n'est pas la position 12 du Code civil.
            T = V(f"@{doc.name}:{position}")
            if prec is None:
                g.links.append([g, doc])        # genèse : exister ici
            else:
                prec.links.append([g, T, doc])  # [cible, où, dans quoi]
            prec = g
    return reg


def main():
    args = [a for a in sys.argv[1:] if a != "-o"]
    if not args:
        print("Usage : python3 circe_encoder.py fichier.txt [autre.txt ...] [-o sortie.vjson]")
        sys.exit(1)

    if "-o" in sys.argv:
        i = sys.argv.index("-o")
        sortie = sys.argv[i + 1]
        chemins = [a for a in sys.argv[1:i]]
    else:
        chemins = args
        sortie = chemins[0].rsplit(".", 1)[0] + ".vjson"

    print(f"Tissage de {len(chemins)} document(s)...")
    reg = encoder(chemins)
    print(f"{len(reg)} nœuds au total.")

    with open(sortie, "w", encoding="utf-8") as f:
        f.write(registre_vers_json(reg))
    print(f"Écrit : {sortie}")


if __name__ == "__main__":
    main()
