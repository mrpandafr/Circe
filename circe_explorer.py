#!/usr/bin/env python3
"""
circe_explorer.py -- naviguer un graphe Nœud déjà tissé.

  /texte MOT            -- les nœuds dont le nom contient MOT
  /voisins MOT          -- ses liens sortants et ses occurrences
  /contexte MOT POS     -- la phrase autour de cette occurrence, exacte
  /near NOM             -- proximité sémantique (optionnel, BGE-M3)
  /quit

Rien n'est stocké en double : les occurrences d'un glyphe ne sont pas
un champ, ce sont les liens qui le visent. On les indexe au chargement
pour la vitesse, jamais dans le fichier.

Usage :
    python3 circe_explorer.py corpus.vjson [vecteurs.npy]
"""
import sys
import json
from noeud_json import json_vers_registre


def est_position(nom):
    """Accepte les deux formes : '@doc:12' (multi-documents) et '@12'
    (ancienne, mono-document). Rien de ce qui a été tissé ne devient
    illisible."""
    if not nom.startswith("@"):
        return False
    reste = nom.rsplit(":", 1)[-1] if ":" in nom else nom[1:]
    return reste.isdigit()


def decomposer(nom_position):
    """-> (préfixe, rang). '@a:12' -> ('@a', 12) ; '@12' -> ('@', 12)."""
    if ":" in nom_position:
        prefixe, rang = nom_position.rsplit(":", 1)
        return prefixe, int(rang)
    return "@", int(nom_position[1:])


def indexer(reg):
    """Index de lecture, construit en mémoire, jamais persisté.

    suivant[(nom, position)]  -> glyphe à cette position
    occurrences[nom]          -> positions où ce glyphe est atteint
    documents[nom]            -> documents où ce glyphe apparaît
    contenu[doc]              -> glyphes distincts de ce document"""
    suivant, precedent = {}, {}
    occurrences, documents, contenu = {}, {}, {}
    for v in reg.values():
        for lien in v.links:
            cible = lien[0]
            pos = next((q.name for q in lien[1:] if est_position(q.name)), None)
            doc = next((q.name for q in lien[1:] if not est_position(q.name)), None)
            if doc is not None:
                documents.setdefault(cible.name, set()).add(doc)
                contenu.setdefault(doc, set()).add(cible.name)
            if pos is None:
                continue
            occurrences.setdefault(cible.name, []).append(pos)
            if cible is v:
                # Un lien vers soi dit « j'existe ici », pas « ceci mène
                # à cela ». L'inclure dans la chaîne créerait une boucle
                # qui casserait la reconstruction.
                continue
            suivant[(v.name, pos)] = cible.name
            precedent[(cible.name, pos)] = v.name
    return suivant, precedent, occurrences, documents, contenu


FINS = {".", "!", "?"}

def reconstruire(suivant, precedent, mot, position, borne=FINS, maxi=400):
    """position est un nom complet, ex '@alice:142'."""
    """La suite exacte autour d'une occurrence, reconstruite depuis le
    graphe seul. Rien n'est dupliqué en stockage.

    L'encodeur ne segmente pas -- c'est ce qui garantit la fidélité au
    caractère près. La frontière de phrase est donc une décision de
    LECTURE : on avance jusqu'à une ponctuation forte, on recule jusqu'à
    la précédente. La ponctuation est un nœud du graphe comme un autre ;
    l'observateur choisit de s'y arrêter, le stockage ne l'impose pas."""
    prefixe, p = decomposer(position)

    apres, courant, c = [], mot, p
    sep = ":" if ":" in position else ""
    while (courant, f"{prefixe}{sep}{c + 1}") in suivant and len(apres) < maxi:
        courant = suivant[(courant, f"{prefixe}{sep}{c + 1}")]
        c += 1
        apres.append(courant)
        if courant in borne:
            break

    avant, courant, c = [], mot, p
    while (courant, f"{prefixe}{sep}{c}") in precedent and len(avant) < maxi:
        precedent_nom = precedent[(courant, f"{prefixe}{sep}{c}")]
        if precedent_nom in borne:
            break
        courant, c = precedent_nom, c - 1
        avant.insert(0, courant)

    return "".join(avant + [mot] + apres).strip()


def charger_semantique(chemin, noms):
    try:
        import numpy as np
        return np.load(chemin), np
    except (ImportError, FileNotFoundError):
        return None, None


def poids(nom, occurrences):
    """Ce qu'un mot partagé pèse dans un recoupement.

    Aucun seuil, aucun filtre : la fréquence décide seule. Un glyphe
    qui revient partout (l'espace, « le », « de ») pèse presque rien ;
    un mot rare pèse lourd. C'est Zipf appliqué tel quel — le sens
    émerge de la fréquence, on ne le force pas en écartant d'avance
    ce qu'on croit être du bruit.

    Les versions précédentes filtraient par seuils (60 %, trois
    documents, cinq documents). Chaque seuil décidait à la place de
    la fréquence, et le premier corpus venu le prenait en défaut."""
    n = len(occurrences.get(nom, ())) or 1
    return 1.0 / n


def repl(reg, vecteurs=None, np=None, ordre=None):
    suivant, precedent, occurrences, documents, contenu = indexer(reg)
    docs = sorted(contenu)
    print(f"Circé -- {len(reg)} nœuds, {len(docs)} document(s), "
          f"{len(suivant)} transitions.")
    print(f"Angle sémantique : {'activé' if vecteurs is not None else 'non activé'}")
    print()
    print("  1. lire        /docs                    /extrait DOC")
    print("  2. recouper    /recoupe DOC             /partage DOC1 DOC2")
    print("  3. explorer    /texte MOT   /voisins MOT   /contexte MOT POSITION"
          f"{'   /near NOM' if vecteurs is not None else ''}")
    print("     /quit\n")

    while True:
        try:
            ligne = input("circe> ").strip()
        except EOFError:
            break
        if not ligne or ligne in ("/quit", "/exit"):
            break
        parts = ligne.split(maxsplit=1)
        cmd, arg = parts[0], (parts[1] if len(parts) > 1 else "")

        # ── Niveau 1 : lire ──────────────────────────────────────
        if cmd == "/docs":
            print(f"  {len(docs)} document(s) :")
            for d in docs:
                glyphes = contenu[d]
                mots = [g for g in glyphes if len(g) >= 3 and g.strip()]
                n_pos = sum(1 for n in occurrences
                            for p in occurrences[n] if p.startswith(f"@{d}:"))
                print(f"    {d:24s} {n_pos:7d} glyphes  "
                      f"{len(glyphes):5d} distincts  {len(mots):5d} mots")

        elif cmd == "/extrait":
            if arg not in contenu:
                print(f"  Document inconnu. Essaie /docs.")
                continue
            debut = [n for n, ls in ((v.name, v.links) for v in reg.values())
                     for l in ls if len(l) == 2 and l[0].name == n
                     and l[1].name == arg]
            if not debut:
                print("  Début introuvable.")
                continue
            print(f"  {reconstruire(suivant, precedent, debut[0], f'@{arg}:0', maxi=60)!r}")

        # ── Niveau 2 : recouper ──────────────────────────────────
        elif cmd == "/recoupe":
            if arg not in contenu:
                print("  Document inconnu. Essaie /docs.")
                continue
            scores = []
            for autre in docs:
                if autre == arg:
                    continue
                communs = contenu[arg] & contenu[autre]
                communs = [c for c in communs if c.strip()]
                if not communs:
                    continue
                total = sum(poids(c, occurrences) for c in communs)
                # les plus lourds d'abord : les plus rares
                communs.sort(key=lambda c: -poids(c, occurrences))
                scores.append((total, autre, communs))
            if not scores:
                print("  Aucun glyphe en commun.")
                continue
            scores.sort(reverse=True)
            print(f"  '{arg}' recoupe :")
            for total, autre, communs in scores[:8]:
                apercu = ", ".join(f"{c}({len(occurrences.get(c,()))})"
                                   for c in communs[:6])
                print(f"    poids {total:6.2f}  {len(communs):4d} en commun avec "
                      f"{autre:16s} : {apercu}"
                      f"{' ...' if len(communs) > 6 else ''}")

        elif cmd == "/partage":
            a = arg.split()
            if len(a) != 2 or any(d not in contenu for d in a):
                print("  Usage : /partage DOC1 DOC2  (voir /docs)")
                continue
            communs = [c for c in contenu[a[0]] & contenu[a[1]] if c.strip()]
            communs.sort(key=lambda c: -poids(c, occurrences))
            print(f"  {len(communs)} en commun, du plus rare au plus fréquent :")
            for m in communs[:20]:
                pos = [p for p in occurrences.get(m, []) if p.startswith(f"@{a[0]}:")]
                n = len(occurrences.get(m, ()))
                if pos:
                    print(f"    {m:16s} ×{n:<4d} {reconstruire(suivant, precedent, m, pos[0])!r}")

        # ── Niveau 3 : explorer ──────────────────────────────────
        elif cmd == "/texte":
            for n in [n for n in reg if arg.lower() in n.lower()][:12]:
                print(f"  {n[:150]}")

        elif cmd == "/voisins":
            trouves = [n for n in reg if arg.lower() in n.lower()]
            if not trouves:
                print("  Aucun nœud trouvé.")
                continue
            nom = trouves[0]
            v = reg[nom]
            print(f"  Nœud : {nom[:100]}")
            print(f"  documents : {sorted(documents.get(nom, []))}")
            print(f"  links ({len(v.links)}) :")
            for lien in v.links[:12]:
                q = " ".join(f"[{x.name}]" for x in lien[1:]) or "[sans qualificateur]"
                print(f"    -> {lien[0].name[:50]!r}  {q}")
            if len(v.links) > 12:
                print(f"    ... {len(v.links) - 12} de plus")
            occ = occurrences.get(nom, [])
            print(f"  occurrences ({len(occ)}) : {occ[:8]}{' ...' if len(occ) > 8 else ''}")

        elif cmd == "/contexte":
            a = arg.rsplit(maxsplit=1)
            if len(a) != 2:
                print("  Usage : /contexte MOT POSITION  (position vue via /voisins)")
                continue
            mot, pos = a
            if mot not in reg:
                print(f"  Nœud '{mot}' inconnu.")
                continue
            if pos not in occurrences.get(mot, []):
                print(f"  '{mot}' n'est pas attesté à {pos}.")
                continue
            print(f"  {reconstruire(suivant, precedent, mot, pos)!r}")

        elif cmd == "/near" and vecteurs is not None:
            if arg not in ordre:
                print("  Nom exact introuvable (essaie /texte).")
                continue
            i = ordre.index(arg)
            scores = vecteurs @ vecteurs[i]
            for j in np.argsort(-scores)[:6]:
                if ordre[j] != arg:
                    print(f"  {scores[j]:.4f} -- {ordre[j][:120]}")

        elif cmd == "/near":
            print("  /near indisponible -- fournis un fichier vecteurs.npy.")

        else:
            print("  Commande inconnue. /docs /extrait /recoupe /partage "
                  "/texte /voisins /contexte /quit")


def main():
    if len(sys.argv) < 2:
        print("Usage : python3 circe_explorer.py corpus.vjson [vecteurs.npy]")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        reg = json_vers_registre(f.read())
    ordre = list(reg.keys())
    vecteurs, np = (None, None)
    if len(sys.argv) > 2:
        vecteurs, np = charger_semantique(sys.argv[2], ordre)
        if vecteurs is None:
            print(f"(angle sémantique indisponible -- on continue sans)")
    repl(reg, vecteurs, np, ordre)


if __name__ == "__main__":
    main()
