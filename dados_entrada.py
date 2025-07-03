from typing import Dict

class EntradaDados:
    def __init__(self):
        self.geometria: Dict = {}
        self.cargas: Dict = {}
        self.dados_tanque: Dict = {}
        self.solo: Dict = {}

    def ler_dados(self, arquivo: str = None):
        import json
        if arquivo:
            with open(arquivo, 'r') as f:
                dados = json.load(f)
                self.geometria = dados.get('geometria', {})
                self.cargas = dados.get('cargas', {})
                self.dados_tanque = dados.get('dados_tanque', {})
                if 'dens_fluido' in self.dados_tanque and 'densidade_fluido' not in self.dados_tanque:
                    self.dados_tanque['densidade_fluido'] = self.dados_tanque['dens_fluido']
                self.solo = dados.get('solo', {})
        else:
            self.geometria['altura'] = float(input("Altura do tanque (m): "))
            self.geometria['diametro'] = float(input("Diâmetro do tanque (m): "))
            self.solo['tipo'] = input("Tipo de solo: ")

    def validar_dados(self):
        if not self.geometria or not self.solo:
            raise ValueError("Dados de geometria e solo são obrigatórios.")
        if 'altura' not in self.geometria or self.geometria['altura'] <= 0:
            raise ValueError("Altura do tanque deve ser maior que zero.")
        if 'diametro' not in self.geometria or self.geometria['diametro'] <= 0:
            raise ValueError("Diâmetro do tanque deve ser maior que zero.")
        if 'tipo' not in self.solo:
            raise ValueError("Tipo de solo deve ser informado.")
