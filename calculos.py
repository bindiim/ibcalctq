# calculos.py

from relatorio import Relatorio
from tkinter import messagebox

def executar_calculo(entrada, materiais, inputs):
    try:
        for key, entry in inputs.items():
            valor = entry.get()
            if valor.strip() != "":
                try:
                    valor_float = float(valor.replace(",", "."))
                    if key.startswith("vento_"):
                        entrada.cargas[key] = valor_float
                    elif key in entrada.geometria:
                        entrada.geometria[key] = valor_float
                    elif key in entrada.solo:
                        entrada.solo[key] = valor_float
                    elif key in entrada.cargas:
                        entrada.cargas[key] = valor_float
                    elif key in entrada.dados_tanque:
                        entrada.dados_tanque[key] = valor_float
                    else:
                        entrada.geometria[key] = valor_float
                except ValueError:
                    entrada.geometria[key] = valor

        if 'tensao_adm_kgfcm2' in inputs:
            sigma_adm = float(inputs['tensao_adm_kgfcm2'].get().replace(",", ".")) * 98.0665
            materiais.definir_tensao_admissivel(sigma_adm)

        entrada.validar_dados()
        relatorio = Relatorio(entrada, materiais)
        relatorio.gerar_html()
        messagebox.showinfo("Sucesso", "Cálculo realizado com sucesso. Relatório salvo como 'relatorio.html'.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))
