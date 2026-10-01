"""
Gerador de relatórios para o Google Sheets

O programa:
1. Permite escolher o CSV de entrada;
2. Recebe o link/nome da planilha Google;
3. Gera todos os relatórios;
4. Envia cada DataFrame diretamente para uma aba;
5. Não cria CSVs intermediários;
6. Mantém valores numéricos como números no Google Sheets.
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import gspread
import pandas as pd

from google.oauth2.service_account import Credentials

# ============================================================
# IMPORTAÇÕES DOS RELATÓRIOS
# ============================================================

from relatorios import gerar_todos_relatorios
# ============================================================
# CONFIGURAÇÕES
# ============================================================

NOME_ARQUIVO_CREDENCIAIS = "credenciais.json"

ESCOPOS = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def conectar_google_sheets():

    if not os.path.exists(NOME_ARQUIVO_CREDENCIAIS):
        raise FileNotFoundError(
            f"Não encontrei o arquivo '{NOME_ARQUIVO_CREDENCIAIS}' nesta pasta.\n\n"
            "Verifique se o arquivo está na mesma pasta deste programa."
        )

    credenciais = Credentials.from_service_account_file(
        NOME_ARQUIVO_CREDENCIAIS,
        scopes=ESCOPOS
    )

    return gspread.authorize(credenciais)
def montar_dados_gerais(relatorios, espaco_colunas=1):


    blocos = []
    nomes = list(relatorios.items())

    for indice, (nome_aba, df) in enumerate(nomes):

        bloco = df.reset_index(drop=True).copy()
        blocos.append(bloco)

        # coluna(s) em branco entre um relatório e outro
        if espaco_colunas and indice < len(nomes) - 1:
            for i in range(espaco_colunas):
                nome_coluna_vazia = f"__espaco_{indice}_{i}"
                blocos.append(
                    pd.DataFrame({nome_coluna_vazia: [""] * len(bloco)})
                )

    dados_gerais = pd.concat(blocos, axis=1)


    dados_gerais.columns = [
        "" if str(c).startswith("__espaco_") else c
        for c in dados_gerais.columns
    ]

    return dados_gerais

def abrir_planilha(cliente, identificador_planilha):

    try:
        if identificador_planilha.startswith("http"):
            return cliente.open_by_url(identificador_planilha)

        return cliente.open(identificador_planilha)

    except gspread.SpreadsheetNotFound:
        raise RuntimeError(
            "Planilha não encontrada.\n\n"
            "Confira se:\n"
            "- o link/nome está correto;\n"
            "- a planilha foi compartilhada com o e-mail da conta de serviço."
        )


def obter_ou_criar_aba(
    planilha,
    nome_aba,
    linhas,
    colunas
):

    try:
        return planilha.worksheet(nome_aba)

    except gspread.WorksheetNotFound:
        return planilha.add_worksheet(
            title=nome_aba,
            rows=linhas,
            cols=colunas
        )


def enviar_dataframe_para_sheets(
    df,
    identificador_planilha,
    nome_aba,
    substituir=True
):


    if df is None:
        raise ValueError(
            f"O relatório '{nome_aba}' retornou None."
        )

    if df.empty:
        raise ValueError(
            f"O relatório '{nome_aba}' está vazio."
        )

    cliente = conectar_google_sheets()

    planilha = abrir_planilha(
        cliente,
        identificador_planilha
    )

    aba = obter_ou_criar_aba(
        planilha,
        nome_aba,
        linhas=len(df) + 10,
        colunas=len(df.columns) + 2
    )


    cabecalho = df.columns.tolist()

    linhas_dados = df.astype(object).where(
        pd.notna(df),
        ""
    ).values.tolist()

    dados = [cabecalho] + linhas_dados

    if substituir:
        aba.clear()
        aba.update(dados, value_input_option="USER_ENTERED")
    else:
        if not aba.get_all_values():
            linhas_para_enviar = [cabecalho] + linhas_dados
        else:
            linhas_para_enviar = linhas_dados

        if linhas_para_enviar:
            aba.append_rows(linhas_para_enviar, value_input_option="USER_ENTERED")

        for linha in linhas_dados:

            aba.append_row(
                linha,
                value_input_option="USER_ENTERED"
            )

    return (
        f"Aba '{nome_aba}' enviada com sucesso: "
        f"{len(linhas_dados)} linhas."
    )


# ============================================================
# GERAÇÃO DOS RELATÓRIOS
# ============================================================

def gerar_e_enviar_relatorios(caminho_csv, identificador_planilha, atualizar_status):
    atualizar_status("Gerando os relatórios...")
    relatorios = gerar_todos_relatorios(caminho_csv)

    resultados = []
    erros = []

    for nome_aba, df in relatorios.items():
        atualizar_status(f"Enviando relatório '{nome_aba}' para o Google Sheets...")
        try:
            resultado = enviar_dataframe_para_sheets(
                df=df,
                identificador_planilha=identificador_planilha,
                nome_aba=nome_aba,
                substituir=True
            )
            resultados.append(resultado)
        except Exception as erro:
            erros.append(f"'{nome_aba}': {erro}")

    # ----------------------------------------------------
    # NOVA ABA: "dados gerais" com todos os relatórios
    # colocados um ao lado do outro
    # ----------------------------------------------------
    atualizar_status("Montando aba 'dados gerais'...")
    try:
        dados_gerais = montar_dados_gerais(relatorios)
        resultado = enviar_dataframe_para_sheets(
            df=dados_gerais,
            identificador_planilha=identificador_planilha,
            nome_aba="dados gerais",
            substituir=True
        )
        resultados.append(resultado)
    except Exception as erro:
        erros.append(f"'dados gerais': {erro}")

    mensagem = "Relatórios enviados:\n" + "\n".join(resultados)
    if erros:
        mensagem += "\n\n⚠️ Falharam:\n" + "\n".join(erros)

    return mensagem


class AppRelatorios:

    def __init__(self, raiz):

        self.raiz = raiz

        raiz.title(
            "Gerador de relatórios - Google Sheets"
        )

        raiz.geometry("560x380")
        raiz.resizable(False, False)

        espaco = {
            "padx": 12,
            "pady": 8
        }

 
        tk.Label(
            raiz,
            text="CSV de entrada:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            **espaco
        )

        self.campo_csv = tk.Entry(
            raiz,
            width=42
        )

        self.campo_csv.grid(
            row=0,
            column=1,
            **espaco
        )

        tk.Button(
            raiz,
            text="Escolher...",
            command=self.escolher_csv
        ).grid(
            row=0,
            column=2,
            **espaco
        )


        tk.Label(
            raiz,
            text="Tipo:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            **espaco
        )

        self.tipo_relatorio = tk.StringVar(
            value="Idiomas"
        )

        self.combo_tipo = ttk.Combobox(
            raiz,
            textvariable=self.tipo_relatorio,
            values=[
                "Idiomas",
                "Tecnologia"
            ],
            state="readonly",
            width=39
        )

        self.combo_tipo.grid(
            row=1,
            column=1,
            columnspan=2,
            **espaco
        )



        tk.Label(
            raiz,
            text="Planilha:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            **espaco
        )

        self.campo_planilha = tk.Entry(
            raiz,
            width=42
        )

        self.campo_planilha.grid(
            row=2,
            column=1,
            columnspan=2,
            **espaco
        )



        self.botao_enviar = tk.Button(
            raiz,
            text="Gerar e enviar relatórios",
            width=28,
            command=self.iniciar_envio
        )

        self.botao_enviar.grid(
            row=3,
            column=0,
            columnspan=3,
            pady=18
        )



        self.barra_progresso = ttk.Progressbar(
            raiz,
            mode="indeterminate",
            length=500
        )

        self.barra_progresso.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=12,
            pady=6
        )

        self.barra_progresso.grid_remove()



        self.rotulo_status = tk.Label(
            raiz,
            text="",
            fg="gray20",
            justify="left",
            wraplength=520
        )

        self.rotulo_status.grid(
            row=5,
            column=0,
            columnspan=3,
            padx=12,
            pady=10,
            sticky="w"
        )

    def escolher_csv(self):

        caminho = filedialog.askopenfilename(
            title="Escolha o CSV de entrada",
            filetypes=[
                ("Arquivos CSV", "*.csv"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if caminho:

            self.campo_csv.delete(
                0,
                tk.END
            )

            self.campo_csv.insert(
                0,
                caminho
            )



    def definir_status(
        self,
        texto,
        cor="gray20"
    ):

        self.rotulo_status.config(
            text=texto,
            fg=cor
        )

    def iniciar_envio(self):

        caminho_csv = (
            self.campo_csv
            .get()
            .strip()
        )

        identificador_planilha = (
            self.campo_planilha
            .get()
            .strip()
        )

        if not caminho_csv:
            messagebox.showwarning(
                "Campo faltando",
                "Escolha o CSV de entrada."
            )
            return

        if not identificador_planilha:
            messagebox.showwarning(
                "Campo faltando",
                "Informe o link ou nome da planilha."
            )
            return

        if not os.path.exists(caminho_csv):
            messagebox.showerror(
                "Arquivo não encontrado",
                "O arquivo CSV selecionado não existe."
            )
            return

        self.botao_enviar.config(
            state="disabled"
        )

        self.definir_status(
            "Gerando relatórios e enviando para o Google Sheets..."
        )

        self.barra_progresso.grid()
        self.barra_progresso.start(12)

        thread = threading.Thread(
            target=self.executar_envio,
            args=(
                caminho_csv,
                identificador_planilha
            ),
            daemon=True
        )

        thread.start()  

    def executar_envio(
        self,
        caminho_csv,
        identificador_planilha
    ):
        try:

            mensagem = gerar_e_enviar_relatorios(
                caminho_csv,
                identificador_planilha,
                self.definir_status
            )
            self.definir_status("Acionando gatilho no Google Sheets...")
            url_do_script = ""
            requests.get(url_do_script)

            self.raiz.after(0, self.envio_concluido, True, mensagem)
            self.raiz.after(
                0,
                self.envio_concluido,
                True,
                mensagem
            )

        except Exception as erro:

            self.raiz.after(
                0,
                self.envio_concluido,
                False,
                str(erro)
            )


    def envio_concluido(
        self,
        sucesso,
        mensagem
    ):

        self.barra_progresso.stop()

        self.barra_progresso.grid_remove()

        self.botao_enviar.config(
            state="normal"
        )

        if sucesso:

            self.definir_status(
                mensagem,
                cor="green4"
            )

            messagebox.showinfo(
                "Sucesso",
                mensagem
            )

        else:

            self.definir_status(
                f"Erro: {mensagem}",
                cor="red3"
            )

            messagebox.showerror(
                "Erro",
                mensagem
            )




def main():

    raiz = tk.Tk()

    AppRelatorios(raiz)

    raiz.mainloop()


if __name__ == "__main__":
    main()