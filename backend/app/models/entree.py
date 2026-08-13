"""
Entrée — objet central de Matrice. Quatre natures : Décision, Constat, Contrainte, Jalon.

Sensibilité (décision 11/08/2026) : une Entrée est sensible si `sensible`
(marquage manuel direct) est vrai, OU si au moins un axe qui lui est
rattaché est marqué `sensible` (héritage). Le calcul combiné se fait via
la propriété `sensible_effective` — jamais stocké en double pour éviter
toute désynchronisation entre le flag direct et l'héritage.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

NATURES_ENTREE = ("Decision", "Constat", "Contrainte", "Jalon")
STATUTS_ENTREE = ("Active", "Perimee")  # modèle binaire — pas de troisième état (décision de conception)


class Entree(Base):
    __tablename__ = "entree"
    __table_args__ = (
        CheckConstraint(f"nature IN {NATURES_ENTREE}", name="ck_entree_nature"),
        CheckConstraint(f"statut IN {STATUTS_ENTREE}", name="ck_entree_statut"),
        UniqueConstraint("projet_id", "code_lecture", name="uq_entree_projet_code_lecture"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    projet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projet.id"), nullable=False)

    # {PROJET}-{NNNN} — attribué une fois, jamais réattribué.
    code_lecture: Mapped[str] = mapped_column(String, nullable=False)

    nature: Mapped[str] = mapped_column(String, nullable=False)
    statut: Mapped[str] = mapped_column(String, nullable=False, default="Active")

    # FK circulaire avec `version` — résolue via use_alter (voir migration 0002).
    version_active_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("version.id", use_alter=True, name="fk_entree_version_active"),
        nullable=True,
    )

    # Pense-bête non bloquant — n'affecte jamais un workflow.
    phase_alerte_id: Mapped[int | None] = mapped_column(SmallInteger, ForeignKey("phase.id"), nullable=True)

    # Marquage manuel direct. Décision 11/08/2026 : combiné en OR avec l'héritage des axes
    # (voir `sensible_effective`) — jamais l'un sans l'autre.
    sensible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())

    versions: Mapped[list["Version"]] = relationship(  # noqa: F821
        "Version",
        back_populates="entree",
        foreign_keys="Version.entree_id",
    )
