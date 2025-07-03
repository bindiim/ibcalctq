# utils.py

import math


def converter_unidades(valor, unidade_origem, unidade_destino):
    """
    Converte valor entre unidades de medida comuns usadas em engenharia estrutural.
    """
    fatores_conversao = {
        ('kNm', 'kNcm'): 100,
        ('kNcm', 'kNm'): 0.01,
        ('MPa', 'kN/cm2'): 0.01,
        ('kN/cm2', 'MPa'): 100,
        ('tf', 'kN'): 9.80665,
        ('kN', 'tf'): 1/9.80665
    }

    chave = (unidade_origem, unidade_destino)

    if unidade_origem == unidade_destino:
        return valor

    if chave in fatores_conversao:
        return valor * fatores_conversao[chave]
    
    raise ValueError(f"Conversão de {unidade_origem} para {unidade_destino} não suportada.")


def calcular_area_circular(diametro_m):
    """
    Calcula a área de uma base circular em metros quadrados.
    """
    return math.pi * (diametro_m / 2) ** 2


def calcular_volume_cilindro(diametro_m, altura_m):
    """
    Calcula o volume de um cilindro (ex: tanque) em metros cúbicos.
    """
    return math.pi * (diametro_m / 2) ** 2 * altura_m


def obter_fator_influencia(L, B):
    """
    Retorna o fator de influência I para cálculo de recalque com base em L/B.
    (implementação simples, pode ser refinada com interpolação futura).
    """
    L_B = L / B
    if L_B < 1.0:
        L_B = 1.0
    elif L_B > 3.0:
        L_B = 3.0

    # Valores aproximados baseados em tabelas típicas
    tabela_I = {
        1.0: 1.10,
        2.0: 1.20,
        3.0: 1.30
    }

    return tabela_I.get(round(L_B), 1.15)  # interpolação futura opcional


def arredondar_para_multiplo(valor, base=5):
    """
    Arredonda o valor para o múltiplo mais próximo da base fornecida.
    Ex: base=5 → múltiplos de 5 mm para bitolas.
    """
    return base * round(valor / base)
