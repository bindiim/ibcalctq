from cargas import Cargas

class AnaliseEstrutural:
    """
    Classe responsável por executar a análise estrutural do tanque.
    """
    def __init__(self, cargas: Cargas):
        """
        Inicializa a análise estrutural com uma instância de Cargas.

        :param cargas: Instância da classe Cargas com métodos de cálculo das cargas atuantes
        """
        self.cargas = cargas

    def verificar_estabilidade(self):
        """
        Verifica a estabilidade global do tanque considerando as cargas atuantes.

        :return: dicionário com fatores de segurança e resultados da verificação
        """
        peso_proprio = self.cargas.calcular_peso_proprio()
        carga_vento = self.cargas.calcular_vento()

        # Exemplo simplificado: fator de segurança ao tombamento
        momento_estabilizante = peso_proprio * (self.cargas.dados.geometria.get('diametro', 0) / 2)
        momento_desestabilizante = carga_vento * (self.cargas.dados.geometria.get('altura', 0) / 2)

        fator_seguranca = momento_estabilizante / momento_desestabilizante if momento_desestabilizante != 0 else float('inf')

        return {
            'momento_estabilizante': momento_estabilizante,
            'momento_desestabilizante': momento_desestabilizante,
            'fator_seguranca': fator_seguranca
        }

    def calcular_esforcos(self):
        """
        Calcula esforços de compressão vertical na base do tanque.

        :return: dicionário com esforços calculados
        """
        peso_proprio = self.cargas.calcular_peso_proprio()
        carga_fluido = self.cargas.calcular_cargas_tanque()

        esforco_total_vertical = peso_proprio + carga_fluido

        return {
            'peso_proprio': peso_proprio,
            'carga_fluido': carga_fluido,
            'esforco_total_vertical': esforco_total_vertical
        }
