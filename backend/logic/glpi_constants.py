"""
Constantes de campos e status do GLPI centralizadas.

Somente os campos e status usados no dashboard foram definidos.
"""

# Campos de Ticket
FIELD_LEVEL = 8
FIELD_STATUS = 12
FIELD_CREATED = 15
FIELD_TECH = 5

# Campos de User (para buscas auxiliares)
FIELD_USER_ACTIVE = 8
FIELD_GROUP = 13

# Status de Ticket
STATUS = {
    "NEW": 1,
    "ASSIGNED": 2,
    "PLANNED": 3,
    "IN_PROGRESS": 4,
    "SOLVED": 5,
    "CLOSED": 6,
}