VARK_CHOICES = [
    ('V', 'Visual'),
    ('A', 'Aural'),
    ('R', 'Read/Write'),
    ('K', 'Kinesthetic'),
]

CHAPMAN_CHOICES = [
    ('A', 'Palabras de Afirmación'),
    ('B', 'Tiempo de Calidad'),
    ('C', 'Recibir Detalles o Regalos'),
    ('D', 'Actos de Servicio'),
    ('E', 'Contacto o Presencia Física y Emocional'),
]

ALL_CATEGORIES = list({c[0]: c for c in VARK_CHOICES + CHAPMAN_CHOICES}.values())