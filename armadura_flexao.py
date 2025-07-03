import math

def calcular_armadura_flexao(
    Md_pos_kNm, Md_neg_kNm,
    h_m, base1_m, base2_m,
    fck=30, fyk=500
):
    # Constantes e conversões
    bw = (base1_m + base2_m) * 1000  # largura em mm
    h = h_m * 1000  # altura em mm
    cobrimento = 40  # mm
    d = h - cobrimento  # mm
    fcd = fck / 1.4  # MPa
    fyd = fyk / 1.15  # MPa

    def calcular_As(Md_kNm):
        if Md_kNm <= 0:
            return 0.0, 0.0
        
        Md_Nmm = Md_kNm * 1e6  # kNm para Nmm
        z = 0.68 * d  # mm
        
        # Cálculo direto da armadura As pela NBR 6118
        As_mm2 = Md_Nmm / (fyd * z)
        y_d = As_mm2 / (bw * d)  # razão geométrica (para referência)
        
        As_cm2 = As_mm2 / 100  # conversão correta para cm²
        
        return y_d, As_cm2

    y_d_pos, As_pos = calcular_As(Md_pos_kNm)
    y_d_neg, As_neg = calcular_As(abs(Md_neg_kNm)) if Md_neg_kNm < 0 else (0.0, 0.0)

    # Armadura mínima conforme NBR 6118
    As_min = 0.0015 * bw * h / 100  # cm²
    As_pele = 0.001 * bw * h / 100  # cm²

    return {
        "armadura_minima_cm2": round(As_min, 2),
        "armadura_pele_cm2": round(As_pele, 2),
        "armadura_positiva_cm2": round(max(As_pos, As_min), 2),
        "y_d_positivo": round(y_d_pos, 4),
        "armadura_negativa_cm2": round(max(As_neg, As_min) if Md_neg_kNm < 0 else 0, 2),
        "y_d_negativo": round(y_d_neg, 4) if Md_neg_kNm < 0 else 0.0
    }
