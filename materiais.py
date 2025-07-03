
class Materiais:
    """
    Gerencia as propriedades dos materiais utilizados no cálculo estrutural.
    Apenas a tensão admissível do solo é fornecida por entrada; o restante é fixo.
    """
    def __init__(self):
        self.concreto = {
            'fck': 30,                   # MPa
            'gamma': 25,                 # kN/m³
            'modulo_elasticidade': 30672.46  # MPa
        }
        self.aco = {
            'fyk': 250,                  # MPa
            'modulo_elasticidade': 200000    # MPa
        }
        self.solo = {
            'tensao_admissivel': None,       # kN/m² → fornecido via entrada
            'coeficiente_reacao': 10000,     # kN/m³
            'modulo_elasticidade': 20000     # kN/m²
        }

    def definir_tensao_admissivel(self, valor: float):
        self.solo['tensao_admissivel'] = valor

    def validar_materiais(self):
        if None in self.concreto.values():
            raise ValueError("Todos os parâmetros do concreto devem ser definidos.")
        if None in self.aco.values():
            raise ValueError("Todos os parâmetros do aço devem ser definidos.")
        if self.solo['tensao_admissivel'] is None:
            raise ValueError("Tensão admissível do solo deve ser definida.")
