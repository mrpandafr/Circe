"""
tissage_semantique.py -- BGE-M3 utilisé pour TISSER, pas seulement
pour chercher après coup. Un lien créé ainsi porte une source
honnête : "BGE-M3 (similarité sémantique)" -- jamais confondu avec
un renvoi explicitement affirmé par un humain ou un texte source.

Le score est gardé dans le nom du temps -- traçable, jamais caché.
"""
from noeud_json import tisser


def tisser_par_similarite(reg: dict, textes: list[str], seuil: float = 0.7,
                           modele_nom: str = "BGE-M3"):
    """Ajoute des liens automatiques entre textes sémantiquement
    proches (score >= seuil). Chaque lien est honnêtement sourcé
    comme venant du modèle, pas d'une citation humaine.

    Nécessite sentence-transformers -- absent : lève une erreur claire
    plutôt que d'échouer silencieusement."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError(
            "sentence-transformers requis pour le tissage sémantique. "
            "pip install sentence-transformers --break-system-packages\n"
            "Sans lui, utilise tisser_generique() pour les liens explicites."
        )
    import numpy as np

    modele = SentenceTransformer("BAAI/bge-m3")
    vecteurs = modele.encode(textes, normalize_embeddings=True,
                              show_progress_bar=True)

    n_liens_crees = 0
    for i, texte_a in enumerate(textes):
        scores = vecteurs @ vecteurs[i]
        for j, score in enumerate(scores):
            if i == j or score < seuil:
                continue
            temps_trace = f"{modele_nom}_score={score:.4f}"
            tisser(reg, texte_a, textes[j],
                   temps_trace, f"{modele_nom} (similarité sémantique)")
            n_liens_crees += 1
    return n_liens_crees


if __name__ == "__main__":
    # Test minimal : deux textes proches, un éloigné.
    reg = {}
    textes = [
        "Les contrats légalement formés tiennent lieu de loi à ceux qui les ont faits.",
        "Les contrats doivent être négociés, formés et exécutés de bonne foi.",
        "Le chat dort sur le canapé.",
    ]
    n = tisser_par_similarite(reg, textes, seuil=0.5)
    print(f"\n{n} liens sémantiques créés.")
    v = reg[textes[0]]
    print(f"\nLiens sortants du premier texte :")
    for T, src, cible in v.links:
        print(f"  [{T.name}] {src.name} -> {cible.name[:60]}")
