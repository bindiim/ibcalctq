# recalque.py

from dados_entrada import EntradaDados
from materiais import Materiais
from dimensionamento_base import DimensionamentoBase


class Recalque:
    """
    Classe responsável pelo cálculo do recalque imediato da base do tanque.
    """
    def __init__(self, dados_entrada: EntradaDados, materiais: Materiais, dimensao_base: DimensionamentoBase):
        self.dados = dados_entrada
        self.materiais = materiais
        self.dimensao_base = dimensao_base

    def calcular_recalque(self):
        """
        Calcula o recalque imediato da fundação do tanque baseado na teoria da elasticidade.

        Fórmula:
            Se = [(1 - μ²) / E] * [q * sqrt(B * L)] / I

        Onde:
            Se = recalque estimado (m)
            μ = coeficiente de Poisson do solo
            E = módulo de elasticidade do solo (kN/m²)
            q = tensão média aplicada (kN/m²)
            B = menor dimensão da base (m)
            L = maior dimensão da base (m)
            I = fator de influência de forma e posição (função de L/B)

        :return: dicionário com resultados do recalque
        """
        resultados_base = self.dimensao_base.dimensionar()
        q = resultados_base['esforco_total_vertical'] / resultados_base['area_minima_base_m2']  # tensão média

        # Dimensões da base (em metros)
        lado_a = self.dados.geometria.get('lado_a_m', 0.5)
        lado_b = self.dados.geometria.get('lado_b_m', 1.0)

        if lado_a <= 0 or lado_b <= 0:
            raise ValueError("Dimensões da base inválidas.")

        B = min(lado_a, lado_b)
        L = max(lado_a, lado_b)

        L_B = L / B
        I = 1.10  # Valor padrão; pode ser ajustado com interpolação ou tabela, se necessário

        E = self.materiais.solo.get('modulo_elasticidade', 20000)  # kN/m²
        mu = self.dados.solo.get('poisson', 0.4)

        if E <= 0:
            raise ValueError("Módulo de elasticidade do solo inválido.")

        recalque = ((1 - mu ** 2) / E) * (q * (B * L) ** 0.5) / I

        return {
            'tensao_media_kN_m2': q,
            'modulo_elasticidade_kN_m2': E,
            'coef_poisson': mu,
            'dimensoes_base_m': {'B': B, 'L': L, 'L/B': L_B},
            'fator_influencia': I,
            'recalque_estimado_m': recalque,
            'recalque_estimado_mm': recalque * 1000
        }
