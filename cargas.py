class Cargas:
    """
    Classe para calcular as cargas atuantes na estrutura do tanque.
    """
    def __init__(self, dados_entrada, materiais):
        """
        Inicializa a classe com os dados de entrada e materiais.

        :param dados_entrada: Instância de EntradaDados contendo informações de geometria, cargas e solo
        :param materiais: Instância de Materiais contendo propriedades dos materiais
        """
        self.dados = dados_entrada
        self.materiais = materiais
        self._fv_cache = None  # força do vento calculada
        self._q_cache = None   # pressão dinâmica calculada

    def calcular_peso_proprio(self):
        """
        Calcula o peso próprio do tanque considerando geometria e densidade do material do tanque.

        :return: peso próprio (float)
        """
        altura = self.dados.geometria.get('altura', 0)
        diametro = self.dados.geometria.get('diametro', 0)
        gamma_concreto = self.materiais.concreto.get('gamma', 0)

        volume = 3.1416 * (diametro / 2) ** 2 * altura
        peso_proprio = volume * gamma_concreto

        return peso_proprio

    def calcular_cargas_tanque(self):
        """
        Calcula as cargas resultantes do fluido armazenado no tanque.

        :return: carga do fluido (float)
        """
        altura = self.dados.geometria.get('altura', 0)
        diametro = self.dados.geometria.get('diametro', 0)
        densidade_fluido = self.dados.dados_tanque.get('densidade_fluido', 0)

        volume_fluido = 3.1416 * (diametro / 2) ** 2 * altura
        carga_fluido = volume_fluido * densidade_fluido

        return carga_fluido

    def calcular_vento(self):
        """
        Calcula a carga de vento atuante na superfície do tanque com base na NBR 6123.

        :return: carga de vento total (kN)
        """
        if self._fv_cache is not None:
            return self._fv_cache

        # Parâmetros de entrada
        V0 = self.dados.cargas.get('vento_v0', 0)         # velocidade básica (m/s)
        S1 = self.dados.cargas.get('vento_s1', 1.0)
        S2 = self.dados.cargas.get('vento_s2', 1.0)
        S3 = self.dados.cargas.get('vento_s3', 1.0)

        altura = self.dados.geometria.get('altura', 0)
        diametro = self.dados.geometria.get('diametro', 0)

        # Etapas conforme NBR 6123
        Vk = V0 * S1 * S2 * S3                              # Velocidade característica
        q = ((Vk ** 2) / 16) * 0.00980665                   # Pressão dinâmica (kN/m²)
        area_proj = diametro * altura                      # Área projetada do tanque

        Ca = 0.5  # Coeficiente de arrasto fixo conforme solicitação
        carga_vento = Ca * q * area_proj                   # Força total de vento

        self._fv_cache = carga_vento
        self._q_cache = q
        self.dados.cargas['pressao_vento'] = q

        return carga_vento
