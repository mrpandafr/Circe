class Noeud:
    """TOUT. Deux champs. Rien de plus."""

    def __init__(self, name: str):
        self.name = name
        self.links: list[list] = []   # [[cible, qualificateur, ...], ...]
                                       # Chaque lien est une liste VIVANTE :
                                       # la cible en tête, puis les
                                       # qualificateurs, dans l'ordre où on
                                       # les apprend. Un lien grandit ; il
                                       # ne se réécrit jamais.
