"""
Entidades de dominio (Core) para el proceso FOMTAN.

Ojo: aquí NO hay lógica de entrada/salida (sin BD, sin cámara, sin archivos).
Solo modelos de datos que representan el negocio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional

# Reutilizamos tipos de la capa core
# (asumiendo que ya existen en src/fomtan/core/types.py)
from fomtan.core.domain_types import Status, Prediction, Decision



# ---------------------------------------------------------------------------
# Defectos
# ---------------------------------------------------------------------------


class DefectType(Enum):
    """Tipo de defecto observado en una pieza de fruta o verdura."""

    FUNGUS = "hongo"               # moho en uvas, tomates, etc.
    BRUISE = "golpe"               # machucón en manzana, pera, palta
    CRACK = "rajadura"             # rajadura en cereza, tomate, durazno
    SUNBURN = "quemadura_solar"    # típico en manzana, uva, palta
    DEHYDRATION = "deshidratacion" # deshidratado / arrugado
    DEFORMATION = "deformacion"    # formas irregulares en papa, tomate, zanahoria
    SOFT_ROT = "pudricion_blanda"  # pudrición blanda en tomates, paltas
    OTHER = "otro"


@dataclass
class Defect:
    """
    Defecto puntual observado en una pieza individual (cereza, uva, manzana, palta, verdura, etc.).
    """

    type: DefectType
    severity: int  # 1 (leve) a 5 (grave)
    description: Optional[str] = None
    detected_at: Optional[datetime] = None
    detector_operator_id: Optional[str] = None

    # Ejemplo de uso:
    #   Defect(
    #       type=DefectType.BRUISE,
    #       severity=3,
    #       description="Golpe en manzana Royal Gala lado pedúnculo",
    #   )


# ---------------------------------------------------------------------------
# Material extraño
# ---------------------------------------------------------------------------


class ForeignMaterialType(Enum):
    """Tipo de material extraño encontrado en el flujo de proceso."""

    LEAF = "hoja"                   # hojas de parrón, de cerezo, etc.
    STICK = "palo"                  # ramitas
    SOIL = "tierra"                 # típico en papa, zanahoria, cebolla
    OTHER_FRUIT = "restos_otra_fruta"
    PLASTIC = "plastico"
    METAL = "metal"
    INSECT = "insecto"
    STRING = "cordel"
    OTHER = "otro"


@dataclass
class ForeignMaterial:
    """
    Registro de material extraño encontrado en un lote o en la línea de selección/embalaje.
    """

    type: ForeignMaterialType
    quantity: float  # cantidad aproximada (por ejemplo en gramos o unidades)
    unit: str = "unidad"
    description: Optional[str] = None
    detected_at: Optional[datetime] = None
    detector_operator_id: Optional[str] = None
    lot_code: Optional[str] = None

    # Ejemplo:
    #   ForeignMaterial(
    #       type=ForeignMaterialType.SOIL,
    #       quantity=300,
    #       unit="gramos",
    #       lot_code="L-UVA-2025-001",
    #       description="Tierra en sector ingreso de uva Red Globe",
    #   )


# ---------------------------------------------------------------------------
# Lote y pieza
# ---------------------------------------------------------------------------


@dataclass
class Lot:
    """
    Lote de fruta o verdura chilena: conjunto de piezas de un mismo origen/fecha.
    Ej: lote de cereza Santina de Curicó, uva Red Globe de Peralillo, papa Desirée de Osorno.
    """

    code: str
    species: str  # Ej: "Cereza", "Uva de mesa", "Manzana", "Palta", "Tomate", "Papa"
    variety: str  # Ej: "Santina", "Regina", "Red Globe", "Royal Gala", "Hass"
    harvest_date: date
    origin_field: str  # Huerto / campo de origen (ej: "Curicó - Fundo Los Álamos")
    region: Optional[str] = None  # Región chilena (ej: "Maule", "O'Higgins", "Ñuble")
    producer: str = ""  # Nombre del productor o empresa (ej: "Exportadora SurFruit")
    expected_quantity_kg: Optional[float] = None
    received_quantity_kg: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    crop_profile_id: Optional[str] = None  # Referencia al perfil de cultivo

    # Ejemplo:
    #   Lot(
    #       code="L-CER-2025-001",
    #       species="Cereza",
    #       variety="Santina",
    #       harvest_date=date(2025, 11, 25),
    #       origin_field="Curicó - Fundo Los Álamos",
    #       region="Maule",
    #       producer="Exportadora SurFruit",
    #       expected_quantity_kg=22000.0,
    #   )


@dataclass
class FruitItem:
    """
    Pieza individual de fruta o verdura chilena que se presenta al sistema.
    Ej: una cereza, una uva, una manzana, una palta, un tomate, una papa.
    """

    id: str  # identificador interno (por cámara, línea, etc.)
    lot_code: str
    species: str
    variety: str

    # Medidas físicas básicas (opcionales según sensores disponibles)
    weight_g: Optional[float] = None
    diameter_mm: Optional[float] = None  # calibre (cereza, uva, tomate)
    length_mm: Optional[float] = None    # largo (zanahoria, pepino, etc.)
    color_index: Optional[float] = None  # índice de color (rojo, verde, etc.)
    brix: Optional[float] = None         # grados brix / dulzor (uva, cereza, manzana)

    # Información de proceso
    captured_at: Optional[datetime] = None
    position_in_line: Optional[int] = None

    # Resultados de modelos / negocio
    prediction: Optional[Prediction] = None
    decision: Optional[Decision] = None
    status: Optional[Status] = None

    defects: List[Defect] = field(default_factory=list)
    foreign_materials: List[ForeignMaterial] = field(default_factory=list)

    # Ejemplo:
    #   pieza = FruitItem(
    #       id="CER-0000001",
    #       lot_code="L-CER-2025-001",
    #       species="Cereza",
    #       variety="Santina",
    #       weight_g=9.2,
    #       diameter_mm=28.5,
    #   )
    #   pieza.defects.append(
    #       Defect(type=DefectType.CRACK, severity=4, description="Rajadura en sutura")
    #   )


# ---------------------------------------------------------------------------
# Perfil de cultivo
# ---------------------------------------------------------------------------


@dataclass
class CropProfile:
    """
    Perfil de cultivo por especie/variedad (ej: Cereza Santina, Uva Red Globe, Palta Hass).
    Contiene umbrales de calidad y mensajes de negocio.
    """

    id: str
    species: str         # "Cereza", "Uva de mesa", "Manzana", "Palta", etc.
    variety: str         # "Santina", "Regina", "Red Globe", "Royal Gala", "Hass", etc.

    # Umbrales simples de ejemplo (pueden alinearse con thresholds.py)
    min_weight_first_kg: Optional[float] = None
    max_weight_first_kg: Optional[float] = None
    min_brix_first: Optional[float] = None
    max_defects_first: Optional[int] = None

    max_defects_second: Optional[int] = None

    # Mensajes a mostrar según decisión del sistema
    decision_messages: Dict[Decision, str] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True

    # Ejemplo:
    #   perfil = CropProfile(
    #       id="PF-CER-SANTINA",
    #       species="Cereza",
    #       variety="Santina",
    #       min_weight_first_kg=0.008,   # 8 gramos por fruta aprox.
    #       max_weight_first_kg=0.014,   # 14 gramos por fruta aprox.
    #       min_brix_first=18.0,
    #       max_defects_first=0,
    #       max_defects_second=1,
    #   )
    #   perfil.decision_messages[Decision.FIRST] = "Cereza Primera Exportación"
    #   perfil.decision_messages[Decision.SECOND] = "Cereza Segunda Local"
    #   perfil.decision_messages[Decision.REJECT] = "Descartar por defectos o calibre"


# ---------------------------------------------------------------------------
# Operarios
# ---------------------------------------------------------------------------


class OperatorRole(Enum):
    """Rol que cumple el operario en planta o en el campo."""

    SELECTOR = "selector"           # persona en mesa de selección
    PACKER = "embalador"           # persona que arma cajas/bins
    PLANNER = "planillero"         # quien registra en planillas o sistema
    SUPERVISOR = "supervisor"
    QUALITY = "control_calidad"
    HARVEST_CREW = "cuadrilla_cosecha"
    OTHER = "otro"


@dataclass
class Operator:
    """
    Operario que participa en el proceso (cosecha, selección, embalaje, planillas, supervisión, etc.).
    """

    id: str
    full_name: str
    role: OperatorRole
    rut: Optional[str] = None  # RUT chileno u otro identificador local
    shift: Optional[str] = None  # Ej: "Día", "Noche", "Turno A"
    station: Optional[str] = None  # puesto o línea (ej: "Línea 1 – Selección Cereza")
    started_at: Optional[datetime] = None
    active: bool = True
    notes: Optional[str] = None

    # Ejemplo:
    #   op = Operator(
    #       id="OP-001",
    #       full_name="Ana Pérez",
    #       role=OperatorRole.SELECTOR,
    #       shift="Día",
    #       station="Línea 1 – Selección Cereza",
    #   )


# ---------------------------------------------------------------------------
# __all__ para dejar claro qué exporta este módulo
# ---------------------------------------------------------------------------

__all__ = [
    "DefectType",
    "Defect",
    "ForeignMaterialType",
    "ForeignMaterial",
    "Lot",
    "FruitItem",
    "CropProfile",
    "OperatorRole",
    "Operator",
]


# ---------------------------------------------------------------------------
# Glosario rápido (comentario)
# ---------------------------------------------------------------------------

# Glosario de términos usados en el dominio FOMTAN (frutas y verduras chilenas):
#
# - Pieza (FruitItem): unidad individual de fruta o verdura que pasa por la línea,
#   por ejemplo una cereza, una uva, una manzana, una palta, un tomate o una papa.
# - Lote (Lot): conjunto de piezas de un mismo campo, productor y fecha de cosecha,
#   por ejemplo lote de Cereza Santina de Curicó o Uva Red Globe de Peralillo.
# - Defecto (Defect): problema visible en una pieza (hongo, golpe, rajadura,
#   quemadura de sol, pudrición blanda, deformación, etc.).
# - Tipo de defecto (DefectType): categoría estandarizada para registrar defectos
#   típicos en fruta y verdura chilena.
# - Material extraño (ForeignMaterial): objeto que no debería estar con la fruta/
#   verdura (hojas, palos, tierra, plástico, metal, insectos, trozos de otras frutas, etc.).
# - Primera: pieza que cumple los criterios de calibre, color, dulzor y defectos
#   para ir a categoría de mayor calidad/precio (exportación o primera local).
# - Segunda: pieza que cumple mínimos, pero con más defectos, menor calibre o
#   condición, generalmente para mercado local o industria.
# - Descartar: pieza que no cumple los mínimos de calidad o inocuidad y debe salir
#   del flujo (podrida, muy dañada, con hongo fuerte, con material extraño pegado, etc.).
# - Perfil de cultivo (CropProfile): parámetros (umbrales y mensajes) por especie/variedad
#   chilena, por ejemplo Cereza Santina, Uva Red Globe, Manzana Royal Gala, Palta Hass.
# - Operario (Operator): persona que participa en la cuadrilla de cosecha, selección
#   en planta, embalaje, registro en planillas o supervisión de calidad.
#
# ---------------------------------------------------------------------------
# Mini test manual (para probar en consola o REPL)
# ---------------------------------------------------------------------------
#
# 1) Crear un lote y una pieza de cereza:
#    >>> from datetime import date
#    >>> from fomtan.core.entities import Lot, FruitItem, Defect, DefectType
#    >>> lot = Lot(
#    ...     code="L-CER-2025-001",
#    ...     species="Cereza",
#    ...     variety="Santina",
#    ...     harvest_date=date(2025, 11, 25),
#    ...     origin_field="Curicó - Fundo Los Álamos",
#    ...     region="Maule",
#    ...     producer="Exportadora SurFruit",
#    ... )
#    >>> pieza = FruitItem(
#    ...     id="CER-0000001",
#    ...     lot_code=lot.code,
#    ...     species=lot.species,
#    ...     variety=lot.variety,
#    ...     weight_g=9.2,
#    ...     diameter_mm=28.5,
#    ... )
#
# 2) Registrar un defecto en la pieza:
#    >>> pieza.defects.append(
#    ...     Defect(type=DefectType.CRACK, severity=4, description="Rajadura en sutura")
#    ... )
#    >>> len(pieza.defects)
#    1
#
# 3) Crear un operario de selección:
#    >>> from fomtan.core.entities import Operator, OperatorRole
#    >>> op = Operator(
#    ...     id="OP-001",
#    ...     full_name="Ana Pérez",
#    ...     role=OperatorRole.SELECTOR,
#    ...     shift="Día",
#    ...     station="Línea 1 – Selección Cereza",
#    ... )
#    >>> op.role
#    <OperatorRole.SELECTOR: 'selector'>
#
# Si estas instrucciones se ejecutan sin error, las entidades básicas están bien definidas.
