class Vector:
    """TOUT. Trois champs. Rien de plus."""

    def __init__(self, name: str):
        self.name = name
        self.links: list[tuple] = []      # [(temps, voisin), ...]
        self.seen: list["Vector"] = []    # vecteurs temps traversés
