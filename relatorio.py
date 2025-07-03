# relatorio.py

from dados_entrada import EntradaDados
from materiais import Materiais
from cargas import Cargas
from analise_estrutural import AnaliseEstrutural
from dimensionamento_base import DimensionamentoBase
from dimensionamento_armaduras import DimensionamentoArmaduras
from recalque import Recalque
from armadura_flexao import calcular_armadura_flexao

class Relatorio:
    def __init__(self, entrada: EntradaDados, materiais: Materiais):
        self.entrada = entrada
        self.materiais = materiais
        self.cargas = Cargas(entrada, materiais)
        self.analise = AnaliseEstrutural(self.cargas)
        self.base = DimensionamentoBase(self.analise, entrada, materiais)
        self.armadura = DimensionamentoArmaduras(self.analise, entrada, materiais)
        self.recalque = Recalque(entrada, materiais, self.base)
        

    def gerar_html(self, caminho_saida="relatorio.html"):
        dados_base = self.base.dimensionar()
        dados_armadura = self.armadura.dimensionar_armaduras()
        dados_recalque = self.recalque.calcular_recalque()
        dados_estabilidade = self.analise.verificar_estabilidade()
        dados_anel = self.base.calcular_espessura_anel()
        dados_resistencia_anel = self.base.calcular_resistencia_anel()
        tensao_fundacao = self.base.verificar_tensao_solo_compactado()
        dados_tensao_anel = self.base.calcular_tensao_sobre_anel()
        verificacao_arrancamento = self.base.verificar_arrancamento_concreto()
        verificacao_pressao_apoio = self.base.verificar_pressao_maxima_apoio()
        dados_momento_torsor = self.base.calcular_momento_torsor()
        dados_momento_fletor = self.base.calcular_momento_fletor()
        dados_esforco_cortante = self.base.calcular_esforco_cortante_perimetro()
        dados_tracao_anel = self.base.calcular_tracao_anel()
        dados_ps2 = self.base.calcular_ps2()
        dados_altura_total = self.base.calcular_altura_total_H()
        dados_ps3 = self.base.calcular_ps3()
        dados_E2 = self.base.calcular_E2()
        dados_tc = self.base.calcular_torcao_conjugada()
        dados_armadura_tracao = self.base.calcular_armadura_tracao_lateral()
        dados_linha_neutra = self.base.calcular_linha_neutra()
        dados_taxa_armadura = self.base.calcular_taxa_armadura_rho()
        dados_area_aco = self.base.calcular_area_aco_via_taxa_armadura()
        dados_armadura_minima = self.base.calcular_armadura_minima()     
       
       
        fv = self.cargas.calcular_vento()
        hT = self.entrada.geometria.get('altura', 0)
        h1 = self.entrada.geometria.get('h1', 0)
        h2 = self.entrada.geometria.get('h2', 0)
        h3 = self.entrada.geometria.get('h3', 0)
        Ca = 0.5

        mvf = ((hT + h1)/2 + h2 + h3) * fv
        mvt = (hT / 2) * fv

        html = f"""
        <html>
        <head><meta charset=\"utf-8\"><title>Relatório de Dimensionamento</title></head>
        <body>
            <h1>Relatório Técnico - Base de Tanque</h1>

            <h2>Dados de Entrada</h2>
            <ul>
                <li>Altura do Tanque: {self.entrada.geometria.get('altura', 'N/A')} m</li>
                <li>Diâmetro do Tanque: {self.entrada.geometria.get('diametro', 'N/A')} m</li>
                <li>Tipo de Solo: {self.entrada.solo.get('tipo', 'N/A')}</li>
            </ul>

            <h2>Esforços Devido ao Vento</h2>
            <ul>
                <li>V₀ (Velocidade básica): {self.entrada.cargas.get('vento_v0', 0)} m/s</li>
                <li>S₁ (Fator topográfico): {self.entrada.cargas.get('vento_s1', 1.0)}</li>
                <li>S₂ (Fator de direção): {self.entrada.cargas.get('vento_s2', 1.0)}</li>
                <li>S₃ (Fator estatístico): {self.entrada.cargas.get('vento_s3', 1.0)}</li>
                <li>Vₕ (Velocidade característica): {
                    self.entrada.cargas.get('vento_v0', 0) *
                    self.entrada.cargas.get('vento_s1', 1.0) *
                    self.entrada.cargas.get('vento_s2', 1.0) *
                    self.entrada.cargas.get('vento_s3', 1.0):.2f} m/s</li>
                <li>q (Pressão dinâmica): {self.entrada.cargas.get('pressao_vento', 0):.2f} kN/m²</li>
                <li>Área Projetada (Ae): {
                    self.entrada.geometria.get('altura', 0) *
                    self.entrada.geometria.get('diametro', 0):.2f} m²</li>
                <li>Coeficiente de Arrasto (Ca): {Ca}</li>
                <li>Força do Vento (Fv): {fv:.2f} kN</li>
                <li>Mvf = ((hT + h1)/2 + h2 + h3)⋅Fv = {mvf:.2f} kN⋅m</li>
                <li>Mvt = (hT/2)⋅Fv = {mvt:.2f} kN⋅m</li>
            </ul>

            <h2>Verificação das Tensões na Fundação</h2>
            <ul>
                <li>{tensao_fundacao['p1_expressao']}</li>
                <li>{tensao_fundacao['p2_expressao']}</li>
                <li>{tensao_fundacao['p3_expressao']}</li>
                <li><strong>p = {tensao_fundacao['p_total']} kN/m²</strong></li>
                <li>τₐdm = {tensao_fundacao['tensao_admissivel_kN_m2']} kN/m²</li>
                <li><strong>{tensao_fundacao['comparacao']}</strong> → {tensao_fundacao['verificacao']}</li>
            </ul>

            <h2>Pré-Dimensionamento da Espessura do Anel</h2>
            <ul>
                <li>ϕ = PTV / (π ⋅ dT) = {dados_anel['phi_kN_m']} kN/m</li>
                <li>p1 (solo compactado): {dados_anel['p1_kN_m2']} kN/m²</li>
                <li>p2 (fluido): {dados_anel['p2_kN_m2']} kN/m²</li>
                <li>p4 (pressão líquida): {dados_anel['p4_kN_m2']} kN/m²</li>
                <li>p5 (peso próprio do anel): {dados_anel['p5_kN_m2']} kN/m²</li>
                <li>p6 = p1 + p2 - p4 - p5 = {dados_anel['p6_kN_m2']} kN/m²</li>
                <li>Espessura Calculada do Anel: {dados_anel['b_calc_m']} m</li>
            </ul>

            <h2>Tensões Sobre o Anel de Concreto</h2>
            <ul>
                <li>p7 = φ / (base1 + base2) = {dados_tensao_anel['p7_kN_m2']} kN/m²</li>
                <li>p8 = Mvf / WA = {dados_tensao_anel['p8_kN_m2']} kN/m²</li>
                <li><strong>P = p4 + p5 + p7 + p8 = {dados_tensao_anel['p_total_kN_m2']} kN/m²</strong></li>
            </ul>

            <h2>Resistência à Flexão do Anel</h2>
            <ul>
                <li>ØB (Diâmetro da Base): {dados_resistencia_anel['ØB_m']} m</li>
                <li>Ø = ØB - 1: {dados_resistencia_anel['Ø_m']} m</li>
                <li><strong>WA = (π/32) ⋅ [(ØB⁴ - Ø⁴)/ØB] = {dados_resistencia_anel['WA_m3']} m³</strong></li>
            </ul>
            
            <h2>Verificação ao Arrancamento do Concreto</h2>
            <ul>
                <li><strong>ϕ = PTV / (π ⋅ dT)</strong> = {verificacao_arrancamento['ϕ']} kN/m</li>
                <li><strong>Pg = γc ⋅ (base1 + base2) ⋅ h</strong> = {verificacao_arrancamento['Pg']} kN</li>
                <li><strong>ps1 = ρT ⋅ k₀ ⋅ h</strong> = {verificacao_arrancamento['ps1']} kN/m²</li>
                <li><strong>E1 = ps1 ⋅ h / 2</strong> = {verificacao_arrancamento['E1']} kN</li>
                <li><strong>Pf = E1 ⋅ tg(35°)</strong> = {verificacao_arrancamento['Pf']} kN</li>
                <li><strong>Mvt = (hT / 2) ⋅ Fv</strong> = {verificacao_arrancamento['Mvt']} kN⋅m</li>
                <li><strong>Ta = ϕ - Mvt / (π ⋅ dT² / 4)</strong> = {verificacao_arrancamento['Ta']} kN/m</li>
                <li><strong>Resistência total: Pg + Pf + ϕ = {verificacao_arrancamento['resistencia_total']} kN</strong></li>
                <li><strong>Verificação: {verificacao_arrancamento['verificacao']}</strong></li>
            </ul>

            <h2>Verificação da Pressão Máxima de Apoio no Concreto</h2>
            <ul>
                <li>ϕ = PTV / (π ⋅ dT) = {verificacao_pressao_apoio['phi_kN_m']} kN/m</li>
                <li>Mvt = (hT / 2) ⋅ Fv = {verificacao_pressao_apoio['Mvt_kNm']} kN⋅m</li>
                <li>Área = π ⋅ dT² / 4 = {verificacao_pressao_apoio['area_base_m2']} m²</li>
                <li>Termo Mvt/Área = {verificacao_pressao_apoio['termo_Mvt_kN_m']} kN/m</li>
                <li>Numerador (ϕ + Mvt/Área): {verificacao_pressao_apoio['numerador_kN_m']} kN/m</li>
                <li>e (largura efetiva de apoio): {verificacao_pressao_apoio['largura_efetiva_apoio_m']} m</li>
                <li><strong>σC'máx = {verificacao_pressao_apoio['tensao_maxima_kN_m2']} kN/m²</strong></li>
                <li>σ<sub>adm</sub> (tensão admissível do apoio): {verificacao_pressao_apoio['tensao_admissivel_kN_m2']} kN/m² → <strong>{verificacao_pressao_apoio['verificacao_adm']}</strong></li>
                <li>f<sub>cd</sub> (resistência de cálculo do concreto): {verificacao_pressao_apoio['fcd_kN_m2']} kN/m² → <strong>{verificacao_pressao_apoio['verificacao_fcd']}</strong></li>
            </ul>

            <h2>Esforços Solicitantes</h2>
            <ul>
                <li>ρ<sub>L</sub> (Densidade do fluido): {dados_momento_torsor['rhoL_kN_m3']} kN/m³</li>
                <li>h<sub>T</sub> (Altura do tanque): {dados_momento_torsor['hT_m']} m</li>
                <li>b₁ (Base 1): {dados_momento_torsor['b1_m']} m</li>
                <li>b₂ (Base 2): {dados_momento_torsor['b2_m']} m</li>
                <li><strong>b = b₁ + b₂ = {dados_momento_torsor['b_m']} m</strong></li>
                <li>Termo 1 = ρL ⋅ hT ⋅ b₂ ⋅ (b/2 − b₂/2) = {dados_momento_torsor['termo1']} kN⋅m/m</li>
                <li>Termo 2 = ϕ ⋅ (b/2 − b₁) = {dados_momento_torsor['termo2']} kN⋅m/m</li>
                <li><strong>MT = Termo 1 − Termo 2 = {dados_momento_torsor['MT_kN_m_por_m']} kN⋅m/m</strong></li>
            </ul>
            <h2>Momento Fletor na Base</h2>
            <ul>
                <li>MT (Momento Torsor): {dados_momento_fletor['MT_kN_m_por_m']} kN⋅m/m</li>
                <li>Base 1 (b₁): {dados_momento_fletor['b1_m']} m</li>
                <li>Base 2 (b₂): {dados_momento_fletor['b2_m']} m</li>
                <li><strong>b = b₁ + b₂ = {dados_momento_fletor['b_total_m']} m</strong></li>
                <li><strong>MF = MT ⋅ (Ø + b)/2 = {dados_momento_fletor['MF_kN_m_por_m']} kN⋅m/m</strong></li>
            </ul>
            
            <h2>Esforço Cortante por Metro de Perímetro</h2>
            <ul>
               <li>Peso do Tanque Vazio: {dados_esforco_cortante.get('PTV_kN', 'N/A')} kN⋅m/m</li>
               <li>Diametro interno do anel = {dados_esforco_cortante.get('ØB_m', 'N/A')} m</li>
               <li>Diametro externo do anel = {dados_esforco_cortante.get('Ø_m', 'N/A')} m</li>
               <li>Base 2 (b₂): {dados_esforco_cortante.get('b2_m', 'N/A')} m</li>
               <li>qi: {dados_esforco_cortante.get('qi_kN_m2', 'N/A')} kN/m2</li>
               <li>V: {dados_esforco_cortante.get('V_kN_m', 'N/A')} kN/m</li>
            </ul>     
   
            <h2>Tração no Anel</h2>
            <ul>
               <li>p₂ = {dados_tracao_anel['p2_kN_m2']} kN/m²</li>
               <li>ρ<sub>L</sub> (Densidade do fluido) = {dados_tracao_anel['rhoL_kN_m3']} kN/m³</li>
               <li><strong>h₀ = p₂ / ρ<sub>L</sub> = {dados_tracao_anel['h0_m']} m</strong></li>
            </ul>
            
            <h2>Empuxo Horizontal ps₂</h2>
            <ul>
               <li>k₀ (Coeficiente de empuxo): {dados_ps2['k0']}</li>
               <li>ρ<sub>T</sub> (Solo compactado): {dados_ps2['rhoT_kN_m3']} kN/m³</li>
               <li>ρ<sub>L</sub> (Fluido): {dados_ps2['rhoL_kN_m3']} kN/m³</li>
               <li>p₂ = ρ<sub>L</sub> ⋅ h<sub>T</sub> = {dados_ps2['p2_kN_m2']} kN/m²</li>
               <li>h₀ = p₂ / ρ<sub>L</sub> = {dados_ps2['h0_m']} m</li>
               <li><strong>ps₂ = k₀ ⋅ ρ<sub>T</sub> ⋅ h₀ = {dados_ps2['ps2_kN_m2']} kN/m²</strong></li>
            </ul>  
            
            <h2>Altura Total H</h2>
           <ul>
               <li>h (Altura da base): {dados_altura_total['h_base_m']} m</li>
               <li>h₀ (Tração no anel): {dados_altura_total['h0_m']} m</li>
               <li><strong>H = h + h₀ = {dados_altura_total['H_m']} m</strong></li>
           </ul>
           
           <h2>Empuxo Horizontal ps₃</h2>
           <ul>
             <li>k₀ (Coeficiente de empuxo): {dados_ps3['k0']}</li>
             <li>ρ<sub>T</sub> (Peso específico do solo compactado): {dados_ps3['rhoT_kN_m3']} kN/m³</li>
             <li>H (Altura total considerada): {dados_ps3['H_m']} m</li>
             <li><strong>ps₃ = k₀ ⋅ ρ<sub>T</sub> ⋅ H = {dados_ps3['ps3_kN_m2']} kN/m²</strong></li>
           </ul>
           
            <h2>Força Horizontal Resultante E₂</h2>
            <ul>
               <li>ps₂ = {dados_E2['ps2_kN_m2']} kN/m²</li>
               <li>ps₃ = {dados_E2['ps3_kN_m2']} kN/m²</li>
               <li>h (Altura da base): {dados_E2['h_base_m']} m</li>
               <li><strong>E₂ = (ps₂ + ps₃) ⋅ h / 2 = {dados_E2['E2_kN']} kN</strong></li>
            </ul> 
            
            <h2>Torção Conjugada Tc</h2>
            <ul>
                <li>ps₂ = {dados_tc['ps2_kN_m2']} kN/m²</li>
                <li>ps₃ = {dados_tc['ps3_kN_m2']} kN/m²</li>
                <li>h (Altura da base) = {dados_tc['h_m']} m</li>
                <li>E₂ = (ps₂ + ps₃)⋅h / 2 = {dados_tc['E2_kN_m']} kN/m</li>
                <li>Ø (diâmetro útil da base) = {dados_tc['Ø_m']} m</li>
                <li>b = base1 + base2 = {dados_tc['b_m']} m</li>
                <li><strong>Tc = E₂ ⋅ (Ø + b) / 2 = {dados_tc['Tc_kN_m']} kN⋅m</strong></li>
            </ul>           

            <h2>Armadura Necessária para Tração Lateral</h2>
            <ul>
                <li>ps₂ = {dados_armadura_tracao['ps2_kN_m2']} kN/m²</li>
                <li>ps₃ = {dados_armadura_tracao['ps3_kN_m2']} kN/m²</li>
                <li>E₂ = {dados_armadura_tracao['E2_kN_m']} kN/m</li>
                <li>Tc = {dados_armadura_tracao['Tc_kN']} kN</li>
                <li>σ aço = {dados_armadura_tracao['sigma_aco_MPa']} MPa</li>
                <li><strong>Área de aço necessária (As): {dados_armadura_tracao['As_tracao_cm2']} cm²</strong></li>
            </ul>
             
             <h2>Cálculo da Linha Neutra</h2>
<ul>
    <li>Momento Fletor Md: {dados_linha_neutra['Md_kNm_m']} kN·m/m</li>
    <li>fcd (tensão de cálculo do concreto): {dados_linha_neutra['fcd_kN_m2']} kN/m²</li>
    <li>b<sub>w</sub> (base1 + base2): {dados_linha_neutra['bw_m']} m</li>
    <li>d (altura útil da seção): {dados_linha_neutra['d_m']} m</li>
    <li><strong>y (profundidade da linha neutra): {dados_linha_neutra['y_m']} m</strong></li>
    <li><strong>y/d: {dados_linha_neutra['y_d_ratio']}</strong></li>
</ul>
             
<h2>Cálculo da Taxa de Armadura (ρ)</h2>
<ul>
    <li>y/d: {dados_taxa_armadura['y_d']}</li>
    <li>f<sub>cd</sub>: {dados_taxa_armadura['fcd_kN_m2']} kN/m²</li>
    <li>f<sub>yd</sub>: {dados_taxa_armadura['fyd_kN_m2']} kN/m²</li>
    <li><strong>ρ = (y/d ⋅ 0,85 ⋅ f<sub>cd</sub>) / f<sub>yd</sub> = {dados_taxa_armadura['rho_taxa_armadura']}</strong></li>
</ul>               
                       
<h2>Cálculo da Área de Armadura pela Taxa</h2>
<ul>
  <li>ρ = {dados_area_aco['rho']}</li>
  <li>b<sub>w</sub> = base1 + base2 = {dados_area_aco['bw_m']} m</li>
  <li>d = altura_base - cobrimento = {dados_area_aco['d_m']} m</li>
  <li><strong>A<sub>s</sub> = ρ ⋅ b<sub>w</sub> ⋅ d = {dados_area_aco['As_cm2']} cm²</strong></li>
</ul>
                
                <h2>Armadura Mínima conforme NBR 6118</h2>
<ul>
    <li>ρ<sub>min</sub> = 0,0015</li>
    <li>b<sub>w</sub> = base1 + base2 = {dados_armadura_minima['bw_m']} m</li>
    <li>d = altura_base - cobrimento = {dados_armadura_minima['d_m']} m</li>
    <li><strong>A<sub>s,min</sub> = ρ<sub>min</sub> ⋅ b<sub>w</sub> ⋅ d = {dados_armadura_minima['As_min_cm2']} cm²</strong></li>
</ul>                   
                    
       
            <h2>Verificação de Estabilidade</h2>
            <ul>
                <li>Momento Estabilizante: {dados_estabilidade['momento_estabilizante']:.2f} kNm</li>
                <li>Momento Desestabilizante: {dados_estabilidade['momento_desestabilizante']:.2f} kNm</li>
                <li>Fator de Segurança: {dados_estabilidade['fator_seguranca']:.2f}</li>
            </ul>

            <h2>Recalque Estimado</h2>
            <ul>
                <li>Tensão Média Aplicada: {dados_recalque['tensao_media_kN_m2']:.2f} kN/m²</li>
                <li>Módulo de Elasticidade do Solo: {dados_recalque['modulo_elasticidade_kN_m2']} kN/m²</li>
                <li>Coeficiente de Poisson: {dados_recalque['coef_poisson']}</li>
                <li>Fator de Influência: {dados_recalque['fator_influencia']}</li>
                <li>Recalque Estimado: {dados_recalque['recalque_estimado_mm']:.2f} mm</li>
            </ul>

            <p><strong>Observação:</strong> Todos os cálculos seguem parâmetros típicos de projeto e devem ser validados com base nas condições reais de obra e normas aplicáveis.</p>
        </body>
        </html>
        """

        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(html)