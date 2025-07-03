# dimensionamento_base.py

from analise_estrutural import AnaliseEstrutural
from dados_entrada import EntradaDados
from materiais import Materiais
import math

class DimensionamentoBase:
    """
    Classe responsável pelo dimensionamento da base do tanque (diâmetro, altura, área de apoio, etc.)
    """
    def __init__(self, analise_estrutural: AnaliseEstrutural, dados_entrada: EntradaDados, materiais: Materiais):
        self.analise = analise_estrutural
        self.dados = dados_entrada
        self.materiais = materiais

    def dimensionar(self):
        esforcos = self.analise.calcular_esforcos()
        esforco_vertical = esforcos['esforco_total_vertical']  # kN
        tensao_admissivel = self.materiais.solo.get('tensao_admissivel', 0)  # kN/m²

        if tensao_admissivel <= 0:
            raise ValueError("Tensão admissível do solo deve ser maior que zero.")

        area_minima_base = esforco_vertical / tensao_admissivel  # m²
        diametro_sugerido = (4 * area_minima_base / 3.1416) ** 0.5  # base circular

        return {
            'esforco_total_vertical': esforco_vertical,
            'tensao_admissivel': tensao_admissivel,
            'area_minima_base_m2': area_minima_base,
            'diametro_base_sugerido_m': diametro_sugerido
        }

    def verificar_tensao_solo_compactado(self):
        hT = self.dados.geometria.get('altura', 0)
        h1 = self.dados.geometria.get('h1', 0.4)
        h2 = self.dados.geometria.get('h2', 0.5)
        h3 = self.dados.geometria.get('h3', 0.0)

        rhoT = 18.0
        rhoL = self.dados.dados_tanque.get('densidade_fluido', 9.96)
        rhoh = 16.0

        sigma_adm = self.materiais.solo.get('tensao_admissivel', 0)

        p1 = round(rhoT * h1, 2)
        p2 = round(rhoL * hT, 2)
        p3 = round(rhoh * (h2 + h3), 2)

        p_total = round(p1 + p2 - p3, 2)

        return {
            'formula': 'p = p1 + p2 - p3',
            'p1_expressao': f"p1 = ρT · h = {rhoT} · {h1} = {p1} kN/m²",
            'p2_expressao': f"p2 = ρL · hT = {rhoL} · {hT} = {p2} kN/m²",
            'p3_expressao': f"p3 = ρh · (h2 + h3) = {rhoh} · ({h2} + {h3}) = {p3} kN/m²",
            'p_total': p_total,
            'tensao_admissivel_kN_m2': sigma_adm,
            'comparacao': f"p = {p_total} kN/m² {'<=' if p_total <= sigma_adm else '>'} τ_adm = {sigma_adm} kN/m²",
            'verificacao': "ok!" if p_total <= sigma_adm else "NÃO ATENDE"
        }

    def calcular_espessura_anel(self):
        PTV = (
            self.dados.dados_tanque.get('peso_tanque_vazio')
            or self.dados.dados_tanque.get('PTV')
            or self.dados.geometria.get('peso_tanque_vazio')
        )
        if not PTV:
             PTV = self.dados.dados_tanque.get('PTV')
        if not PTV:
            PTV = self.dados.geometria.get('peso_tanque_vazio')
        if not PTV:
           raise ValueError("Peso do tanque vazio (PTV) não encontrado nos dados.")
       
        dT = self.dados.geometria.get('diametro', 0)
        h = self.dados.geometria.get('altura_base', 0.9)
        hT = self.dados.geometria.get('altura', 0)

        rhoT = 18.0
        rhoh = 16.0
        rhoL = self.dados.dados_tanque.get('densidade_fluido', 9.96)
        rhoConc = self.materiais.concreto.get('gamma', 25)

        h1 = self.dados.geometria.get('h1', 0.4)
        h2 = self.dados.geometria.get('h2', 0.5)
        h3 = self.dados.geometria.get('h3', 0.0)

        phi = PTV / (math.pi * dT) if dT > 0 else 0
        p1 = rhoT * h1
        p2 = rhoL * hT
        p4 = rhoL * hT / 2
        p5 = rhoConc * h
        p6 = p1 + p2 - p4 - p5
        b_calc = phi / p6 if phi > 0 else 0

        return {
            "phi_kN_m": round(phi,3),
            "p1_kN_m2": round(p1, 2),
            "p2_kN_m2": round(p2, 2),
            "p4_kN_m2": round(p4, 2),
            "p5_kN_m2": round(p5, 2),
            "p6_kN_m2": round(p6, 2),
            "b_calc_m": round(b_calc, 3)
        }

    def calcular_resistencia_anel(self):
        ØB = self.dados.geometria.get('diametro_base', 0)
        if ØB <= 1:
            return {
                "ØB_m": ØB,
                "Ø_m": None,
                "WA_m3": 0,
                "mensagem": "ØB deve ser maior que 1 metro para cálculo ser válido."
            }

        Ø = ØB - 1
        WA = (math.pi / 32) * ((ØB ** 4 - Ø ** 4) / ØB)

        return {
            "ØB_m": round(ØB, 3),
            "Ø_m": round(Ø, 3),
            "WA_m3": round(WA, 6)
        }

    def calcular_tensao_sobre_anel(self):
        resultados_anel = self.calcular_espessura_anel()
        resultados_wa = self.calcular_resistencia_anel()

        phi = resultados_anel["phi_kN_m"]
        p4 = resultados_anel["p4_kN_m2"]
        p5 = resultados_anel["p5_kN_m2"]

        base1 = self.dados.geometria.get("lado_a_m", 0)
        base2 = self.dados.geometria.get("lado_b_m", 0)
        WA = resultados_wa["WA_m3"]

        fv = self.analise.cargas.calcular_vento()
        hT = self.dados.geometria.get("altura", 0)
        h1 = self.dados.geometria.get("h1", 0)
        h2 = self.dados.geometria.get("h2", 0)
        h3 = self.dados.geometria.get("h3", 0)
        mvf = ((hT + h1) / 2 + h2 + h3) * fv

        denominador = base1 + base2
        p7 = phi / denominador if denominador > 0 else 0
        p8 = mvf / WA if WA > 0 else 0
        P_total = p4 + p5 + p7 + p8

        return {
            "p7_kN_m2": round(p7, 2),
            "p8_kN_m2": round(p8, 2),
            "p_total_kN_m2": round(P_total, 2)
        }
    def verificar_arrancamento_concreto(self):
        resultados_anel = self.calcular_espessura_anel()
        """
        Verifica a segurança ao arrancamento do concreto da base do tanque.

        Fórmulas envolvidas:
        - Pg = γ_c · (base1 + base2) · h
        - ps1 = ρT · k0 · h
        - E1 = ps1 · h / 2
        - Pf = E1 · tan(35°)
        - ϕ = PTV / (π · dT)
        - Mvt = (hT / 2) · Fv
        - Ta = ϕ - Mvt / (π · dT² / 4)
        - Verificação: Pg + Pf + ϕ ≥ Ta

        :return: dicionário com todos os termos e resultado da verificação
        """
        import math

        # Parâmetros
        gamma_concreto = self.materiais.concreto.get('gamma', 25)  # kN/m³
        rhoT = 18.0  # peso específico do solo compactado (kN/m³)
        k0 = 0.5     # coeficiente de empuxo em repouso
        angulo = math.radians(35)  # convertendo para radianos

        # Geometria
        base1 = self.dados.geometria.get("lado_a_m", 0)
        base2 = self.dados.geometria.get("lado_b_m", 0)
        h = self.dados.geometria.get("altura_base", 0)
        dT = self.dados.geometria.get("diametro", 0)
        hT = self.dados.geometria.get("altura", 0)

        # Cargas
        PTV = self.dados.dados_tanque.get('peso_tanque_vazio', 0)
        Fv = self.analise.cargas.calcular_vento()

        # Cálculos
        Pg = gamma_concreto * (base1 + base2) * h
        ps1 = rhoT * k0 * h
        E1 = ps1 * h / 2
        Pf = E1 * math.tan(angulo)
        phi = resultados_anel["phi_kN_m"]
        Mvt = ((hT / 2) * Fv) / (math.pi * dT**2 / 4)
        Ta = phi - Mvt  if dT > 0 else 0
        resistencia_total = Pg + Pf + phi
        atende = resistencia_total >= Ta

        return {
            'Pg': round(Pg, 2),
            'ps1': round(ps1, 2),
            'E1': round(E1, 2),
            'Pf': round(Pf, 2),
            'ϕ': round(phi, 2),
            'Mvt': round(Mvt, 2),
            'Ta': round(Ta, 2),
            'resistencia_total': round(resistencia_total, 2),
            'verificacao': "OK" if atende else "NÃO ATENDE"
        }
   
    def verificar_pressao_maxima_apoio(self):
        import math

        resultados_anel = self.calcular_espessura_anel()
        phi = resultados_anel["phi_kN_m"]

        dT = self.dados.geometria.get('diametro', 0)
        base_1 = self.dados.geometria.get('lado_a_m', 0.25)  # largura efetiva de apoio (Base 1)
        hT = self.dados.geometria.get('altura', 0)

        Fv = self.analise.cargas.calcular_vento()

        Mvt = (hT / 2) * Fv

        area_base = (math.pi * dT ** 2) / 4 if dT > 0 else 0

        if area_base == 0 or base_1 == 0:
            raise ValueError("Área da base ou largura efetiva (Base 1) não podem ser zero.")
        
        print(f"[DEBUG] base_1 (lado_a_m) usado na verificação da pressão máxima de apoio: {base_1} m")

        termo_Mvt = Mvt / area_base

        sigma_cmax = (phi + termo_Mvt) / base_1
        sigma_adm = self.materiais.solo.get('tensao_admissivel', 0)  # kN/m²
        fck = self.materiais.concreto.get('fck', 30)
        fcd = (fck / 1.4) * 1000

        atende_adm = sigma_cmax <= sigma_adm
        atende_fcd = sigma_cmax <= fcd
        
        return {
            'phi_kN_m': round(phi, 3),
            'Mvt_kNm': round(Mvt, 2),
            'area_base_m2': round(area_base, 3),
            'termo_Mvt_kN_m': round(termo_Mvt, 2),
            'numerador_kN_m': round(phi + termo_Mvt, 2),
            'largura_efetiva_apoio_m': round(base_1, 3),
            'tensao_maxima_kN_m2': round(sigma_cmax, 2),
            'tensao_admissivel_kN_m2': round(sigma_adm, 2),
            'fcd_kN_m2': round(fcd, 2),
            'verificacao_adm': "OK" if atende_adm else "NÃO ATENDE",
            'verificacao_fcd': "OK" if atende_fcd else "NÃO ATENDE"
        }

    def calcular_momento_torsor(self):
         """
         Calcula o Momento Torsor por metro de perímetro da base do tanque.

         Fórmula:
             MT = ρL · hT · b2 · ((b/2) - (b2/2)) - φ · ((b/2) - b1)

         Retorna:
             dicionário com cada termo e o valor final de MT.
         """
         resultados_anel = self.calcular_espessura_anel()
         phi = resultados_anel.get("phi_kN_m", 0)

         rhoL = self.dados.dados_tanque.get('densidade_fluido', 0)
         hT = self.dados.geometria.get('altura', 0)
         b1 = self.dados.geometria.get('lado_a_m', 0)
         b2 = self.dados.geometria.get('lado_b_m', 0)
         b = b1 + b2

         termo1 = rhoL * hT * b2 * ((b / 2) - (b2 / 2)) if b > 0 and b2 > 0 else 0
         termo2 = phi * ((b / 2) - b1) if b > 0 and b1 > 0 else 0

         MT = termo1 - termo2

         return {
             "rhoL_kN_m3": rhoL,
             "hT_m": hT,
             "b_m": round(b, 3),
             "b1_m": b1,
             "b2_m": b2,
             "termo1": round(termo1, 3),
             "termo2": round(termo2, 3),
             "MT_kN_m_por_m": round(MT, 3)
         }

    def calcular_momento_fletor(self):
        """
         Calcula o Momento Fletor na base por metro de perímetro.

    Fórmula:
        MF = MT * (Ø + b) / 2

    Onde:
        MT = Momento Torsor (kN·m/m)
        Ø  = Ø_m (m) → diâmetro interno útil da base (ØB - 1)
        b  = base1 + base2 (m)

    :return: dicionário com MT, Ø, b e MF
    """
        resultado_mt = self.calcular_momento_torsor()
        resultado_anel = self.calcular_resistencia_anel()

        MT = resultado_mt.get("MT_kN_m_por_m", 0)
        Ø = resultado_anel.get("Ø_m", 0)

        b1 = self.dados.geometria.get('lado_a_m', 0)
        b2 = self.dados.geometria.get('lado_b_m', 0)
        b = b1 + b2

        MF = MT * ((Ø + b) / 2)

        return {
         "MT_kN_m_por_m": round(MT, 3),
         "b1_m": round(b1, 3),
         "b2_m": round(b2, 3),
         "b_total_m": round(b, 3),
         "Ø_m": round(Ø, 3),
         "MF_kN_m_por_m": round(MF, 3)
         }

    def calcular_esforco_cortante_perimetro(self):
        """
            Calcula o esforço cortante por metro de perímetro da base do tanque.

            Fórmulas:
            qi = PTV / [(π ⋅ (Ø + b2)) ⋅ b2]
            V = qi ⋅ b2

            :return: dicionário com qi e V
         """
        ØB = self.dados.geometria.get('diametro_base', 0)
        b2 = self.dados.geometria.get('lado_b_m', 0)
        PTV = (
            self.dados.dados_tanque.get('peso_tanque_vazio')
            or self.dados.dados_tanque.get('PTV')
            or self.dados.geometria.get('peso_tanque_vazio')
        )

        if not PTV:
            return {"mensagem": "Peso do tanque vazio não informado."}

        if ØB <= 1 or b2 <= 0:
            return {"mensagem": "Valores insuficientes para cálculo de esforço cortante."}

        Ø = ØB - 1  # diâmetro útil
        denom = math.pi * (Ø + b2) * b2
        qi = PTV / denom if denom > 0 else 0
        V = qi * b2

        return {
            "PTV_kN": PTV,
            "ØB_m": round(ØB, 3),
            "Ø_m": round(Ø, 3),
            "b2_m": round(b2, 3),
            "qi_kN_m2": round(qi, 3),
            "V_kN_m": round(V, 3)
        }
    def calcular_tracao_anel(self):
        """
        Calcula a altura h0 de tração no anel.
        Fórmula: h0 = p2 / ρL
       """
        resultados = self.calcular_espessura_anel()
        p2 = resultados.get('p2_kN_m2', 0)
        rhoL = self.dados.dados_tanque.get('densidade_fluido', 9.96)

        h0 = p2 / rhoL if rhoL > 0 else 0

        return {
        'p2_kN_m2': p2,
        'rhoL_kN_m3': rhoL,
        'h0_m': round(h0, 3)
        }

    def calcular_ps2(self):
        """
         Calcula o empuxo horizontal ps₂ = k₀ · ρT · h₀
         Sendo h₀ = p₂ / ρL = altura líquida considerada.
        """
        k0 = 0.5  # já utilizado no programa
        rhoT = 18.0  # peso específico do solo compactado (kN/m³)
        rhoL = self.dados.dados_tanque.get('densidade_fluido', 0)
        hT = self.dados.geometria.get('altura', 0)
        p2 = rhoL * hT
        h0 = p2 / rhoL if rhoL > 0 else 0  # cálculo direto como solicitado
        ps2 = k0 * rhoT * h0

        return {
         "k0": k0,
         "rhoT_kN_m3": rhoT,
         "rhoL_kN_m3": rhoL,
         "p2_kN_m2": p2,
         "h0_m": h0,
         "ps2_kN_m2": round(ps2, 2)
        }
        
    def calcular_altura_total_H(self):
        """
        Calcula a altura total H = h + h₀
        h  = altura da base
        h₀ = altura de tração (calculada via p₂ / ρL)
        """
        h = self.dados.geometria.get('altura_base', 0)
        h0_dict = self.calcular_tracao_anel()
        h0 = h0_dict.get('h0_m', 0)

        H = h + h0

        return {
            'h_base_m': h,
            'h0_m': h0,
            'H_m': round(H, 3)
        }
    def calcular_ps3(self):
        """
        Calcula o empuxo horizontal ps₃ = k₀ · ρT · H
        """
        k0 = 0.5  # coeficiente de empuxo em repouso
        rhoT = 18.0  # peso específico do solo compactado (kN/m³)
        H_dict = self.calcular_altura_total_H()
        H = H_dict.get('H_m', 0)

        ps3 = k0 * rhoT * H

        return {
         "k0": k0,
         "rhoT_kN_m3": rhoT,
         "H_m": H,
         "ps3_kN_m2": round(ps3, 2)
        }

    def calcular_E2(self):
        """
        Calcula E2 = (ps2 + ps3) * h / 2
        """
        ps2_dict = self.calcular_ps2()
        ps3_dict = self.calcular_ps3()
        h = self.dados.geometria.get('altura_base', 0)

        ps2 = ps2_dict.get('ps2_kN_m2', 0)
        ps3 = ps3_dict.get('ps3_kN_m2', 0)

        E2 = (ps2 + ps3) * h / 2

        return {
            "ps2_kN_m2": ps2,
            "ps3_kN_m2": ps3,
            "h_base_m": h,
            "E2_kN": round(E2, 2)
        }
              
    def calcular_torcao_conjugada(self):
        """
        Calcula o esforço de torção conjugada (Tc) na base do anel:
        Tc = E2 * (Ø + b)/2
        """
        Ø_resultado = self.calcular_resistencia_anel()
        Ø = Ø_resultado.get("Ø_m", 0)

        b1 = self.dados.geometria.get("lado_a_m", 0)
        b2 = self.dados.geometria.get("lado_b_m", 0)
        b = b1 + b2

    # E2 = (ps2 + ps3) * h / 2
        ps2 = self.calcular_ps2().get("ps2_kN_m2", 0)
        ps3 = self.calcular_ps3().get("ps3_kN_m2", 0)
        h = self.dados.geometria.get("altura_base", 0)

        E2 = (ps2 + ps3) * h / 2
        Tc = E2 * (Ø + b) / 2

        return {
        "ps2_kN_m2": ps2,
        "ps3_kN_m2": ps3,
        "h_m": h,
        "E2_kN_m": round(E2, 2),
        "Ø_m": round(Ø, 3),
        "b_m": round(b, 3),
        "Tc_kN_m": round(Tc, 2)
        }
                        
          
    def calcular_armadura_tracao_lateral(self):
        resultados_anel = self.calcular_espessura_anel()

        rhoT = 18.0
        k0 = 0.5
        h = self.dados.geometria.get('altura_base', 0)
        hT = self.dados.geometria.get('altura', 0)
        ØB = self.dados.geometria.get('diametro_base', 0)
        Ø = ØB - 1 if ØB > 1 else 0
        b1 = self.dados.geometria.get('lado_a_m', 0)
        b2 = self.dados.geometria.get('lado_b_m', 0)
        b = b1 + b2

    # Altura líquida h0 = p2 / rhoL
        rhoL = self.dados.dados_tanque.get('densidade_fluido', 9.96)
        p2 = rhoL * hT
        h0 = p2 / rhoL if rhoL > 0 else 0
        H = h + h0

        ps2 = k0 * rhoT * h0
        ps3 = k0 * rhoT * H
        E2 = (ps2 + ps3) * h / 2
        Tc = E2 * (Ø + b) / 2

        fyk = self.materiais.aco.get('fyk', 250)  # MPa
        gamma_s = 1.4
        sigma_ac = fyk / gamma_s  # MPa
        As = (Tc * gamma_s) / (fyk / 10)  # convertendo kN → N → cm²

        return {
        'ps2_kN_m2': round(ps2, 2),
        'ps3_kN_m2': round(ps3, 2),
        'E2_kN_m': round(E2, 2),
        'Tc_kN': round(Tc, 2),
        'sigma_aco_MPa': round(fyk, 2),
        'As_tracao_cm2': round(As, 2)
         }

    def calcular_linha_neutra(self):
        """
         Calcula a profundidade da linha neutra (y) para seção retangular.
         Equação implícita: (Md / (0.85 * fcd * bw * d^2)) = (y/d) * (1 - 0.5 * y/d)
         Usa método iterativo para encontrar y/d, limitado a máximo de 0.45.
        """
        resultado_mf = self.calcular_momento_fletor()
        Md = resultado_mf.get("MF_kN_m_por_m", 0) * 1000  # kN.m/m → N.m/m

        fck = self.materiais.concreto.get("fck", 30)  # MPa
        # fck é fornecido em MPa (N/mm²). Para utilizar na equação em N/m² é
        # necessário multiplicar por 1e6.
        fcd = (fck / 1.4) * 1e6  # MPa → N/m²

        b1 = self.dados.geometria.get("lado_a_m", 0)
        b2 = self.dados.geometria.get("lado_b_m", 0)
        bw = b1 + b2

        h = self.dados.geometria.get("altura_base", 0)
        d = h - 0.04  # cobrimento de 4 cm

        if d <= 0 or bw <= 0:
            raise ValueError("Dimensões inválidas para cálculo da linha neutra.")

        lado_esquerdo = Md / (0.85 * fcd * bw * d**2)

        from scipy.optimize import fsolve

        def func(r):
            return r * (1 - 0.5 * r) - lado_esquerdo

        r_sol = fsolve(func, 0.4)[0]
        r_sol = min(r_sol, 0.45)  # Limita ao Domínio 3 da NBR 6118

        y = r_sol * d

        return {
            "Md_kNm_m": round(Md / 1000, 3),
            "fcd_kN_m2": round(fcd, 2),
            "bw_m": round(bw, 3),
            "d_m": round(d, 3),
            "y_m": round(y, 4),
            "y_d_ratio": round(r_sol, 4)
        }
        
    def calcular_taxa_armadura_rho(self):
        """
        Calcula a taxa de armadura (ρ) a partir da razão y/d:
        ρ = (y/d) ⋅ (0,85 ⋅ fcd) / fyd
        """
        dados_linha_neutra = self.calcular_linha_neutra()
        y_d = dados_linha_neutra.get('y_d_ratio', 0)

        fck = self.materiais.concreto.get('fck', 30)  # MPa
        # Conversão correta de MPa para N/m²
        fcd = (fck / 1.4) * 1e6

        fyk = self.materiais.aco.get('fyk', 500)  # MPa
        # Conversão de MPa para N/m²
        fyd = (fyk / 1.15) * 1e6

        if fyd == 0:
            raise ValueError("fyd não pode ser zero.")

        rho = (y_d * 0.85 * fcd) / fyd

        return {
         "y_d": round(y_d, 4),
         "fcd_kN_m2": round(fcd, 2),
         "fyd_kN_m2": round(fyd, 2),
         "rho_taxa_armadura": round(rho, 5)
         }

    def calcular_area_aco_via_taxa_armadura(self):
        """
        Calcula a área de armadura As a partir da taxa de armadura ρ:
        As = ρ ⋅ bw ⋅ d
        """
        dados_taxa = self.calcular_taxa_armadura_rho()
        rho = dados_taxa.get("rho_taxa_armadura", 0)  # adimensional

        b1 = self.dados.geometria.get("lado_a_m", 0)
        b2 = self.dados.geometria.get("lado_b_m", 0)
        bw = b1 + b2  # largura da seção (m)

        h = self.dados.geometria.get("altura_base", 0)
        d = h - 0.04  # cobrimento de 4 cm

        As = rho * bw * d  # área de aço (m²)
        As_cm2 = As * 10000  # m² → cm²

        return {
            "rho": round(rho, 5),
            "bw_m": round(bw, 3),
            "d_m": round(d, 3),
            "As_cm2": round(As_cm2, 2)
        }
        
    def calcular_armadura_minima(self):
        """
        Calcula a armadura mínima conforme NBR 6118:
        As_min = 0.0015 ⋅ b_w ⋅ d
        """
        b1 = self.dados.geometria.get("lado_a_m", 0)
        b2 = self.dados.geometria.get("lado_b_m", 0)
        bw = b1 + b2
        h = self.dados.geometria.get("altura_base", 0)
        d = h - 0.04  # cobrimento

        rho_min = 0.0015
        As_min = rho_min * bw * d * 10000  # m² → cm²

        return {
         "rho_min": rho_min,
         "bw_m": round(bw, 3),
         "d_m": round(d, 3),
         "As_min_cm2": round(As_min, 2)
        }
