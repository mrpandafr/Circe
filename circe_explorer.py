#!/usr/bin/env python3
"""
circe_explorer.py -- guide à travers un graphe VectorJSON déjà
tissé. Circé éclaire le chemin : elle ne transforme plus, elle
montre comment naviguer sans se perdre dans le savoir accumulé.

L'angle sémantique (BGE-M3) est OPTIONNEL -- activé seulement si un
fichier de vecteurs existe. Jamais requis pour que Circé fonctionne.
Sans lui : bibliothèque standard uniquement.

Usage :
    python3 circe_explorer.py corpus.vjson [vecteurs.npy]
"""
import sys
import json
from vector_json import json_vers_registre

def charger_angle_semantique(chemin_vecteurs, noms_ordre):
    """Optionnel : ne s'active QUE si numpy et le fichier existent.
    Circé fonctionne parfaitement sans -- c'est un angle en plus,
    jamais une dépendance."""
    try:
        import numpy as np
        vecteurs = np.load(chemin_vecteurs)
        return vecteurs, np
    except (ImportError, FileNotFoundError):
        return None, None


def repl(reg, vecteurs=None, np=None, noms_ordre=None):
    print(f"Circé explore -- {len(reg)} citoyens dans le graphe.")
    angle_actif = "activé" if vecteurs is not None else "non activé (optionnel)"
    print(f"Angle sémantique : {angle_actif}")
    print("Commandes : /texte MOT_CLE  /voisins MOT_CLE"
          f"{'  /near TEXTE_EXACT' if vecteurs is not None else ''}  /quit\n")
    while True:
        try:
            ligne = input("circe> ").strip()
        except EOFError:
            break
        if not ligne or ligne in ("/quit", "/exit"):
            break
        parts = ligne.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "/texte":
            trouves = [n for n in reg if arg.lower() in n.lower()]
            for n in trouves[:10]:
                print(f"  {n[:150]}")
        elif cmd == "/voisins":
            trouves = [n for n in reg if arg.lower() in n.lower()]
            if not trouves:
                print("  Aucun citoyen trouvé.")
                continue
            v = reg[trouves[0]]
            print(f"  Citoyen : {trouves[0][:100]}")
            print(f"  links ({len(v.links)}) :")
            for T, src, cible in v.links:
                print(f"    [{T.name}] {src.name} -> {cible.name[:80]}")
            print(f"  seen ({len(v.seen)} fois cité)")
        elif cmd == "/near" and vecteurs is not None:
            if arg not in noms_ordre:
                print(f"  '{arg[:60]}...' introuvable dans les vecteurs.")
                print(f"  (utilise /texte pour trouver le nom exact d'abord)")
                continue
            idx = noms_ordre.index(arg)
            scores = vecteurs @ vecteurs[idx]
            tri = np.argsort(-scores)
            print(f"  [Angle sémantique -- un modèle, pas une preuve]")
            compte = 0
            for i in tri:
                if noms_ordre[i] == arg:
                    continue
                print(f"  {scores[i]:.4f} -- {noms_ordre[i][:120]}")
                compte += 1
                if compte >= 5:
                    break
        elif cmd == "/near":
            print("  /near indisponible -- angle sémantique non chargé "
                  "(fournis un fichier vecteurs.npy en second argument).")
def main():
    if len(sys.argv) < 2:
        print("Usage : python3 circe_explorer.py corpus.vjson [vecteurs.npy]")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        reg = json_vers_registre(f.read())

    vecteurs, np = None, None
    noms_ordre = list(reg.keys())
    if len(sys.argv) > 2:
        vecteurs, np = charger_angle_semantique(sys.argv[2], noms_ordre)
        if vecteurs is None:
            print(f"(angle sémantique demandé mais indisponible -- "
                  f"numpy ou {sys.argv[2]} manquant, on continue sans)")

    repl(reg, vecteurs, np, noms_ordre)

if __name__ == "__main__":
    main()
