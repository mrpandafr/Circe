#!/usr/bin/env python3
"""
validateur.py -- vérifie qu'un fichier respecte NoeudJSON.

Accepte le format courant (clé "noeuds", liens en tableaux, cible en
tête, longueur 1 à n) et les anciens VectorJSON (clé "citoyens",
champ "seen", cible en dernier ou liens en objets).

Aucune dépendance hors la bibliothèque standard.

Usage :
    python3 validateur.py fichier.vjson
"""
import sys
import json


def valider(texte_json: str):
    """Retourne (erreurs, avertissements). Erreurs vides = valide."""
    erreurs, avertissements = [], []
    try:
        data = json.loads(texte_json)
    except json.JSONDecodeError as e:
        return [f"JSON invalide : {e}"], []

    if isinstance(data, list):
        liste = data
    elif isinstance(data, dict) and ("noeuds" in data or "citoyens" in data):
        liste = data.get("noeuds") or data["citoyens"]
        if not isinstance(liste, list):
            return ["Le champ 'noeuds' doit être une liste."], []
    else:
        return ["Le fichier doit être une liste, ou un objet avec un "
                "champ 'noeuds'."], []

    noms = set()
    for i, item in enumerate(liste):
        if not isinstance(item, dict):
            erreurs.append(f"Élément {i} : doit être un objet.")
            continue

        if "name" not in item:
            erreurs.append(f"Élément {i} : champ 'name' manquant (obligatoire).")
        elif not isinstance(item["name"], str) or not item["name"]:
            erreurs.append(f"Élément {i} : 'name' doit être une chaîne non vide.")
        else:
            noms.add(item["name"])

        if "links" not in item:
            erreurs.append(f"Élément {i} : champ 'links' manquant (obligatoire).")
        elif not isinstance(item["links"], list):
            erreurs.append(f"Élément {i} : 'links' doit être une liste.")
        else:
            for j, lien in enumerate(item["links"]):
                if isinstance(lien, list):
                    if len(lien) < 1:
                        erreurs.append(
                            f"Élément {i}, lien {j} : tableau vide -- un lien "
                            f"porte au moins sa cible.")
                    elif not all(isinstance(x, str) and x for x in lien):
                        erreurs.append(
                            f"Élément {i}, lien {j} : tous les nœuds d'un lien "
                            f"doivent être des chaînes non vides.")
                elif isinstance(lien, dict):        # ancien VectorJSON
                    for champ in ("temps", "cible"):
                        if champ not in lien:
                            erreurs.append(
                                f"Élément {i}, lien {j} : champ '{champ}' manquant.")
                else:
                    erreurs.append(
                        f"Élément {i}, lien {j} : doit être un tableau.")

    # Cible absente du fichier : avertissement, pas erreur -- un lien
    # peut légitimement viser un nœud d'un autre fichier.
    for item in liste:
        if not isinstance(item, dict) or not isinstance(item.get("links"), list):
            continue
        for lien in item["links"]:
            cible = (lien[0] if isinstance(lien, list) and lien
                     else lien.get("cible") if isinstance(lien, dict) else None)
            if cible is not None and cible not in noms:
                avertissements.append(
                    f"Cible '{str(cible)[:50]}' absente de ce fichier.")

    return erreurs, avertissements


def main():
    if len(sys.argv) < 2:
        print("Usage : python3 validateur.py fichier.vjson")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        texte = f.read()

    erreurs, avertissements = valider(texte)
    try:
        brut = json.loads(texte)
    except json.JSONDecodeError:
        brut = None

    if erreurs:
        print(f"❌ {len(erreurs)} erreur(s) :")
        for e in erreurs:
            print(f"  - {e}")
        sys.exit(1)

    fmt = brut.get("format", "format brut") if isinstance(brut, dict) else "format brut"
    print(f"✅ Fichier valide ({fmt}).")
    if avertissements:
        print(f"\n{len(avertissements)} avertissement(s) non bloquants :")
        for a in avertissements[:5]:
            print(f"  - {a}")


if __name__ == "__main__":
    main()
