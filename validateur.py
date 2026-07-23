#!/usr/bin/env python3
"""
validateur.py -- vérifie qu'un fichier .vjson respecte le format
VectorJSON v1.0. Aucune dépendance hors la bibliothèque standard.

Usage :
    python3 validateur.py fichier.vjson
"""
import sys
import json


def valider(texte_json: str) -> list[str]:
    """Retourne (erreurs, avertissements). Accepte le format brut
    (liste nue, pré-v1.1) ET le format enveloppé v1.0/v1.1 avec
    'source_defaut' optionnelle."""
    erreurs = []
    try:
        data = json.loads(texte_json)
    except json.JSONDecodeError as e:
        return [f"JSON invalide : {e}"], []

    if isinstance(data, list):
        liste, source_defaut = data, None
    elif isinstance(data, dict) and "citoyens" in data:
        liste = data["citoyens"]
        source_defaut = data.get("source_defaut")
        if not isinstance(liste, list):
            return ["Le champ 'citoyens' doit être une liste."], []
    else:
        return ["Le fichier doit être une liste, ou un objet avec un "
                "champ 'citoyens'."], []

    data = liste  # la suite de la validation travaille sur la liste

    noms_connus = set()
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            erreurs.append(f"Élément {i} : doit être un objet, pas {type(item).__name__}.")
            continue
        if "name" not in item:
            erreurs.append(f"Élément {i} : champ 'name' manquant (obligatoire).")
        elif not isinstance(item["name"], str) or not item["name"]:
            erreurs.append(f"Élément {i} : 'name' doit être une chaîne non vide.")
        else:
            noms_connus.add(item["name"])

        if "links" in item:
            if not isinstance(item["links"], list):
                erreurs.append(f"Élément {i} : 'links' doit être une liste.")
            else:
                for j, lien in enumerate(item["links"]):
                    for champ in ("temps", "cible"):
                        if champ not in lien:
                            erreurs.append(
                                f"Élément {i}, lien {j} : champ '{champ}' manquant.")
                        elif not isinstance(lien[champ], str):
                            erreurs.append(
                                f"Élément {i}, lien {j} : '{champ}' doit être une chaîne.")
                    if "source" not in lien and source_defaut is None:
                        erreurs.append(
                            f"Élément {i}, lien {j} : 'source' manquant et "
                            f"aucune 'source_defaut' au niveau du fichier.")

        if "seen" in item:
            if not isinstance(item["seen"], list):
                erreurs.append(f"Élément {i} : 'seen' doit être une liste.")
            elif not all(isinstance(t, str) for t in item["seen"]):
                erreurs.append(f"Élément {i} : 'seen' doit contenir uniquement des chaînes.")

    # Vérification de cohérence : chaque cible référencée existe-t-elle
    # quelque part dans le fichier ? (avertissement, pas une erreur bloquante --
    # un lien peut légitimement pointer vers un citoyen d'un autre fichier)
    avertissements = []
    for item in data:
        if isinstance(item, dict) and "links" in item and isinstance(item["links"], list):
            for lien in item["links"]:
                if isinstance(lien, dict) and lien.get("cible") not in noms_connus:
                    avertissements.append(
                        f"Avertissement : cible '{str(lien.get('cible'))[:50]}...' "
                        f"non trouvée dans ce fichier (peut-être dans un autre .vjson).")

    return erreurs, avertissements


def main():
    if len(sys.argv) < 2:
        print("Usage : python3 validateur.py fichier.vjson")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        texte = f.read()

    erreurs, avertissements = valider(texte)
    try:
        data_brute = json.loads(texte)
    except json.JSONDecodeError:
        data_brute = None

    if erreurs:
        print(f"❌ {len(erreurs)} erreur(s) :")
        for e in erreurs:
            print(f"  - {e}")
        sys.exit(1)
    else:
        format_detecte = data_brute.get("format", "VectorJSON (format brut, pré-v1.1)") \
            if isinstance(data_brute, dict) else "VectorJSON (format brut, pré-v1.1)"
        print(f"✅ Fichier valide ({format_detecte}).")
        if avertissements:
            print(f"\n{len(avertissements)} avertissement(s) (non bloquants) :")
            for a in avertissements[:5]:
                print(f"  - {a}")


if __name__ == "__main__":
    main()
