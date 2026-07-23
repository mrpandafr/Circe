"""
vector_json.py -- sérialisation/désérialisation JSON du registre
Vector, générique : marche avec n'importe quel texte, n'importe
quelle source de liens. Pas lié au Code civil, pas lié à un domaine.

Portable (tout langage), sûr (JSON n'exécute jamais de code, contrairement
à pickle), insérable directement dans PostgreSQL JSONB, MongoDB, ES.
"""
import json
from vector import Vector


def vector_vers_dict(v: Vector, deja_vus: set = None, omettre_source: bool = False) -> dict:
    """Un citoyen Vector -> dict JSON-compatible. Gère les cycles
    (un lien qui reboucle) sans récursion infinie.

    `omettre_source` : si toutes les sources du fichier sont identiques,
    ne pas la répéter dans chaque lien -- gain mesuré de ~26% sur un
    corpus littéraire réel. La source reste connue (stockée une fois
    au niveau du fichier), jamais perdue."""
    if deja_vus is None:
        deja_vus = set()
    if id(v) in deja_vus:
        return {"ref": v.name}
    deja_vus.add(id(v))
    if omettre_source:
        links = [{"temps": T.name, "cible": cible.name} for T, src, cible in v.links]
    else:
        links = [{"temps": T.name, "source": src.name, "cible": cible.name}
                 for T, src, cible in v.links]
    return {"name": v.name, "links": links, "seen": [T.name for T in v.seen]}


def registre_vers_json(reg: dict, compact: bool = True) -> str:
    """Tout le registre en JSON. Si toutes les sources des liens sont
    identiques, elle est factorisée une seule fois ("source_defaut")
    plutôt que répétée à chaque lien -- v1.1 du format, rétrocompatible :
    un lecteur v1.0 ignore juste le champ 'source_defaut' s'il ne le
    connaît pas, mais devra alors relire 'source' par lien (absent ici) --
    d'où le champ explicite, jamais un silence ambigu."""
    sources = {src.name for v in reg.values() for T, src, c in v.links}
    source_unique = list(sources)[0] if len(sources) == 1 else None
    separateurs = None if not compact else (',', ':')

    if source_unique is not None:
        liste = [vector_vers_dict(v, omettre_source=True) for v in reg.values()]
        fichier = {"format": "VectorJSON-v1.1", "source_defaut": source_unique,
                   "citoyens": liste}
    else:
        liste = [vector_vers_dict(v, omettre_source=False) for v in reg.values()]
        fichier = {"format": "VectorJSON-v1.0", "citoyens": liste}

    return json.dumps(fichier, ensure_ascii=False, separators=separateurs)


def json_vers_registre(texte_json: str) -> dict:
    """Reconstruit un registre Vector complet depuis du JSON pur --
    lit v1.0 ET v1.1 (source factorisée ou non), ainsi que l'ancien
    format brut (liste nue, sans enveloppe 'format')."""
    data = json.loads(texte_json)
    reg = {}

    def V(name):
        if name not in reg:
            reg[name] = Vector(name)
        return reg[name]

    if isinstance(data, list):
        liste, source_defaut = data, None  # ancien format brut, pré-v1.1
    else:
        liste = data["citoyens"]
        source_defaut = data.get("source_defaut")

    for item in liste:
        v = V(item["name"])
        for l in item["links"]:
            src_name = l.get("source", source_defaut)
            if src_name is None:
                raise ValueError(
                    f"Lien sans source et sans 'source_defaut' au niveau "
                    f"du fichier -- fichier VectorJSON invalide.")
            v.links.append((V(l["temps"]), V(src_name), V(l["cible"])))
        for t_name in item["seen"]:
            v.seen.append(V(t_name))
    return reg


def tisser_generique(reg: dict, texte: str, source: str, temps: str,
                      cibles: list[str] = None):
    """Ajoute un texte au registre. `cibles` = liste de textes déjà
    dans le registre vers lesquels ce texte fait un lien explicite.
    Fonctionne sur N'IMPORTE QUEL texte -- pas de format imposé."""
    def V(name):
        if name not in reg:
            reg[name] = Vector(name)
        return reg[name]

    v = V(texte)
    T, src = V(temps), V(source)
    for cible_texte in (cibles or []):
        cible = V(cible_texte)
        v.links.append((T, src, cible))
        cible.seen.append(T)
    return v
