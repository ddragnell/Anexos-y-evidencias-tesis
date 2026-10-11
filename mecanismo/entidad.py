from dataclasses import dataclass, field, asdict


@dataclass
class Entidad:
    inicio: int
    fin: int
    etiqueta: str
    texto: str
    fuente: str = ""          # "regex", "ner", "presidio", "gold"
    puntaje: float = 1.0
    subtipo: str | None = None  # p. ej. CC, NIT, CE, PASAPORTE para ID_DOC
    extra: dict = field(default_factory=dict)

    def solapa(self, otra: "Entidad") -> bool:
        return self.inicio < otra.fin and otra.inicio < self.fin

    @property
    def largo(self) -> int:
        return self.fin - self.inicio

    def dict(self) -> dict:
        d = asdict(self)
        if not d["extra"]:
            d.pop("extra")
        return d
