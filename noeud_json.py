"""
noeud_json.py -- sérialisation JSON d'un registre de nœuds.

Format NoeudJSON : fidèle au modèle, sans rien inventer.

Un lien est une liste dont le PREMIER élément est la cible ; tout ce
qui suit qualifie. On le sérialise donc comme un tableau JSON,
positionnel, tel quel. Pas de clés "temps"/"source" : elles
inventeraient des types que le modèle n'a pas.

Un lien peut porter 1 nœud (la cible seule) ou n, et plusieurs
longueurs coexistent dans le même fichier.

Portable (tout langage), sûr (JSON n'exécute jamais de code),
insérable dans PostgreSQL JSONB, MongoDB, Elasticsearch.
"""
import json
from noeud import Noeud

FORMAT_COURANT = "NoeudJSON-v1"


def registre_vers_json(reg: dict, compact: bool = True) -> str:
    """Tout le registre en NoeudJSON.

    Aucune factorisation d'un qualificateur constant : gzip le fait
    mieux, et un format qui ne triche pas vaut mieux qu'un format qui
    économise quelques pourcents avant compression."""
    separateurs = (",", ":") if compact else None
    return json.dumps(
        {
            "format": FORMAT_COURANT,
            "noeuds": [
                {"name": v.name,
                 "links": [[x.name for x in lien] for lien in v.links]}
                for v in reg.values()
            ],
        },
        ensure_ascii=False,
        separators=separateurs,
    )


def json_vers_registre(texte_json: str) -> dict:
    """Reconstruit un registre depuis du NoeudJSON.

    Lit aussi les anciens formats VectorJSON (clé 'citoyens', champ
    'seen', liens en objets temps/source/cible ou en tableaux avec la
    cible en DERNIER). Rien de ce qui a été écrit ne devient illisible."""
    data = json.loads(texte_json)
    reg = {}

    def V(nom):
        if nom not in reg:
            reg[nom] = Noeud(nom)
        return reg[nom]

    if isinstance(data, list):
        liste, source_defaut, ancien = data, None, True
    else:
        liste = data.get("noeuds") or data["citoyens"]
        source_defaut = data.get("source_defaut")
        ancien = "noeuds" not in data

    for item in liste:
        v = V(item["name"])
        for lien in item.get("links", []):
            if isinstance(lien, list):
                noms = list(lien)
                if ancien:                  # VectorJSON : cible en dernier
                    noms = [noms[-1]] + noms[:-1]
                v.links.append([V(x) for x in noms])
            else:                            # VectorJSON v1.x : objet à clés
                src = lien.get("source", source_defaut)
                qualificateurs = [lien["temps"]] + ([src] if src else [])
                v.links.append([V(lien["cible"])] + [V(q) for q in qualificateurs])
        for t in item.get("seen", []):       # ancien champ : devient un lien
            v.links.append([v, V(t)])
    return reg


def tisser(reg: dict, sujet: str, cible: str, *qualificateurs):
    """Ajoute un lien [cible, qualificateur, ...] au sujet, et le
    retourne pour qu'on puisse l'enrichir plus tard."""
    def V(nom):
        if nom not in reg:
            reg[nom] = Noeud(nom)
        return reg[nom]

    lien = [V(cible)] + [V(q) for q in qualificateurs]
    V(sujet).links.append(lien)
    return lien
