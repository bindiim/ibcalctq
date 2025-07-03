# dimensionamento_armaduras.py

from analise_estrutural import AnaliseEstrutural
from dados_entrada import EntradaDados
from materiais import Materiais

class DimensionamentoArmaduras:
    """
    Classe responsável pelo cálculo da armadura da base do tanque.
    """
    def __init__(self, analise_estrutural: AnaliseEstrutural, dados_entrada: EntradaDados, materiais: Materiais):
        self.analise = analise_estrutural
        self.dados = dados_entrada
        self.materiais = materiais

    def dimensionar_armaduras(self):
        """
        Dimensiona a armadura mínima da base considerando esforço vertical e geometria circular.

        :return: dicionário com a área de aço calculada, taxa mínima e bitola sugerida
        """
        # Geometria e propriedades do material
        diametro_base = self.dados.geometria.get('diametro_base', 0)  # m
        altura_base = self.dados.geometria.get('altura_base', 0.3)  # m (espessura base)

        fyk = self.materiais.aco.get('fyk', 500)  # MPa
        fcd = self.materiais.concreto.get('fck', 30) / 1.4  # MPa

        if diametro_base <= 0 or altura_base <= 0:
            raise ValueError("Dimensões da base inválidas para o cálculo da armadura.")

        # Área da seção da base
        area_secao = 3.1416 * (diametro_base / 2) ** 2  # m²
        area_secao_cm2 = area_secao * 10000  # cm²

        # Armadura mínima segundo NBR 6118 (0,15% da seção)
        taxa_minima = 0.0015
        area_aco_minima = taxa_minima * area_secao_cm2  # cm²

        # Sugestão de bitola e espaçamento (ex: Ø10 c/ 20cm)
        diametros_comerciais = [5, 6.3, 8, 10, 12.5, 16, 20, 25]
        bitola_sugerida = None
        espacamento = 20  # cm

        for d in diametros_comerciais:
            area_barra = 3.1416 * (d / 10) ** 2 / 4  # cm²
            num_barras_por_m = 100 / espacamento
            area_total_por_m = area_barra * num_barras_por_m
            if area_total_por_m >= area_aco_minima / (diametro_base * 100):  # por metro linear
                bitola_sugerida = d
                break

        return {
            'area_secao_cm2': area_secao_cm2,
            'taxa_minima': taxa_minima,
            'area_aco_minima_cm2': area_aco_minima,
            'bitola_sugerida_mm': bitola_sugerida,
            'espacamento_cm': espacamento
        }
