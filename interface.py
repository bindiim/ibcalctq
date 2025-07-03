import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
from relatorio import Relatorio
from dados_entrada import EntradaDados
from materiais import Materiais
from calculos import executar_calculo

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Base de Tanque - IBcalc")
        self.geometry("800x800")
        self.entrada = EntradaDados()
        self.materiais = Materiais()
        self.tela_inicial()

    def tela_inicial(self):
        for widget in self.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self, text="IBcalc - Base de Tanque", font=("Arial", 24)).pack(pady=50)
        ctk.CTkButton(self, text="Iniciar", command=self.tela_entrada_dados).pack(pady=10)

    def tela_entrada_dados(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.inputs = {}
        canvas = ctk.CTkCanvas(self, width=780, height=700)
        scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def add_campos(titulo, campos, valores_padrao=None):
            frame = ctk.CTkFrame(scrollable_frame)
            frame.pack(pady=10, padx=10, fill="both", expand=False)
            ctk.CTkLabel(frame, text=titulo, font=("Arial", 18, "bold")).pack(pady=5)
            for label, key in campos:
                ctk.CTkLabel(frame, text=label).pack()
                entry = ctk.CTkEntry(frame)
                if valores_padrao and key in valores_padrao:
                    entry.insert(0, str(valores_padrao[key]))
                entry.pack()
                self.inputs[key] = entry

        add_campos("Materiais", [
            ("fck (MPa)", "fck"),
            ("γ (kN/m³)", "gamma"),
            ("E Concreto (MPa)", "E_conc"),
            ("fyk (MPa)", "fyk"),
            ("E Aço (MPa)", "E_aco")
        ], {
            "fck": self.materiais.concreto['fck'],
            "gamma": self.materiais.concreto['gamma'],
            "E_conc": self.materiais.concreto['modulo_elasticidade'],
            "fyk": self.materiais.aco['fyk'],
            "E_aco": self.materiais.aco['modulo_elasticidade']
        })

        add_campos("Geometria", [
            ("Altura do tanque (m)", "altura"),
            ("Diâmetro do tanque (m)", "diametro"),
            ("Diâmetro da base (m)", "diametro_base"),
            ("Altura da base (m)", "altura_base"),
            ("Base 1 (m)", "lado_a_m"),
            ("Base 2 (m)", "lado_b_m"),
            ("Altura camada 1 (m)", "h1"),
            ("Altura camada 2 (m)", "h2"),
            ("Altura camada 3 (m)", "h3")
        ])
        add_campos("Solo", [
            ("Tipo de solo", "tipo"),
            ("Tensão admissível (kgf/cm²)", "tensao_adm_kgfcm2"),
            ("Coeficiente de reação (kN/m³)", "k_reac"),
            ("E solo (kN/m²)", "Esolo"),
            ("ν solo", "poisson")
        ])
        add_campos("Cargas do tanque", [
            ("Peso do tanque vazio (kN)", "peso_tanque_vazio"),
            ("Densidade fluido (kN/m³)", "densidade_fluido"),
            ("Pressão interna (kN/m²)", "pressao_interna")
        ])
        add_campos("Esforços de vento", [
            ("Velocidade básica do vento (m/s)", "vento_v0"),
            ("Fator topográfico", "vento_s1"),
            ("Fator de direção", "vento_s2"),
            ("Fator estatístico", "vento_s3")
        ])
        
        self.texto_resultado = ctk.CTkTextbox(scrollable_frame, width=700, height=400)
        self.texto_resultado.pack(pady=20)
        ctk.CTkButton(scrollable_frame, text="Calcular", command=self.calcular).pack(pady=10)
        ctk.CTkButton(scrollable_frame, text="Salvar Dados (JSON)", command=self.salvar_json).pack(pady=5)
        ctk.CTkButton(scrollable_frame, text="Carregar Dados (JSON)", command=self.carregar_json).pack(pady=5)
        ctk.CTkButton(scrollable_frame, text="Voltar", command=self.tela_inicial).pack(pady=10)

    def atualizar_dados_entrada(self):
      for key, entry in self.inputs.items():
        valor = entry.get().strip()
        if valor != "":
            try:
                valor_float = float(valor.replace(",", "."))
                # Primeiro verifica se são campos especiais do tanque
                if key in ['peso_tanque_vazio', 'densidade_fluido']:
                    self.entrada.dados_tanque[key] = valor_float
                elif key in self.entrada.dados_tanque:
                    self.entrada.dados_tanque[key] = valor_float
                elif key in self.entrada.geometria:
                    self.entrada.geometria[key] = valor_float
                elif key in self.entrada.solo:
                    self.entrada.solo[key] = valor_float
                elif key in self.entrada.cargas:
                    self.entrada.cargas[key] = valor_float
                else:
                    self.entrada.geometria[key] = valor_float
            except ValueError:
                self.entrada.geometria[key] = valor

    def calcular(self):
        try:
            executar_calculo(self.entrada, self.materiais, self.inputs)

            # Ler o HTML gerado e extrair texto
            from bs4 import BeautifulSoup
            with open("relatorio.html", "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                texto = soup.body.get_text(separator="\n")

            # Mostrar o resultado no TextBox
            self.texto_resultado.delete("1.0", "end")
            self.texto_resultado.insert("1.0", texto)

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def salvar_json(self):
        self.atualizar_dados_entrada()
        caminho = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if caminho:
            dados = {
                'geometria': self.entrada.geometria,
                'solo': self.entrada.solo,
                'cargas': self.entrada.cargas,
                'dados_tanque': self.entrada.dados_tanque
            }
            with open(caminho, 'w') as f:
                json.dump(dados, f, indent=4)
            messagebox.showinfo("Salvo", "Dados salvos com sucesso.")

    def carregar_json(self):
        caminho = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if caminho:
            self.entrada.ler_dados(caminho)
            for key, entry in self.inputs.items():
                if key in self.entrada.geometria:
                   valor = self.entrada.geometria[key]
                elif key in self.entrada.solo:
                   valor = self.entrada.solo[key]
                elif key in self.entrada.cargas:
                   valor = self.entrada.cargas[key]
                elif key in self.entrada.dados_tanque:
                   valor = self.entrada.dados_tanque[key]
                else:
                   valor = None

                if valor is not None:
                   entry.delete(0, 'end')
                   entry.insert(0, str(valor))
        messagebox.showinfo("Carregado", "Dados carregados. Clique em Calcular para continuar.")

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()