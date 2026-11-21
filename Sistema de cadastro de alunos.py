import sqlite3
from datetime import datetime
from pathlib import Path

import FreeSimpleGUI as sg


PASTA_PROGRAMA = Path(__file__).resolve().parent
BANCO_DADOS = PASTA_PROGRAMA / "alunos.db"


def conectar():
    conexao = sqlite3.connect(BANCO_DADOS)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabela():
    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS alunos (
                matricula TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                endereco TEXT NOT NULL,
                data_nasc TEXT NOT NULL
            )
            """
        )


def validar_data(data):
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def formatar_nome(nome):
    partes = nome.strip().split()
    return " ".join(
        parte[:1].upper() + parte[1:].lower()
        for parte in partes
        if parte
    )


def listar_alunos(busca=""):
    with conectar() as conexao:
        if busca:
            termo = f"%{busca.lower()}%"
            registros = conexao.execute(
                """
                SELECT matricula, nome, endereco, data_nasc
                FROM alunos
                WHERE lower(matricula) LIKE ? OR lower(nome) LIKE ?
                ORDER BY nome
                """,
                (termo, termo),
            ).fetchall()
        else:
            registros = conexao.execute(
                """
                SELECT matricula, nome, endereco, data_nasc
                FROM alunos
                ORDER BY nome
                """
            ).fetchall()
    return registros


def buscar_matricula(matricula):
    with conectar() as conexao:
        return conexao.execute(
            """
            SELECT matricula, nome, endereco, data_nasc
            FROM alunos
            WHERE matricula = ?
            """,
            (matricula,),
        ).fetchone()


def cadastrar(matricula, nome, endereco, data_nasc):
    with conectar() as conexao:
        conexao.execute(
            "INSERT INTO alunos (matricula, nome, endereco, data_nasc) VALUES (?, ?, ?, ?)",
            (matricula, nome, endereco, data_nasc),
        )


def alterar(matricula_antiga, matricula_nova, nome, endereco, data_nasc):
    with conectar() as conexao:
        conexao.execute(
            """
            UPDATE alunos
            SET matricula = ?, nome = ?, endereco = ?, data_nasc = ?
            WHERE matricula = ?
            """,
            (matricula_nova, nome, endereco, data_nasc, matricula_antiga),
        )


def excluir(matricula):
    with conectar() as conexao:
        conexao.execute("DELETE FROM alunos WHERE matricula = ?", (matricula,))


def limpar_campos(window):
    for chave in ("-MATRICULA-", "-NOME-", "-ENDERECO-", "-DATA-"):
        window[chave].update("")
    window["-MATRICULA-"].set_focus()


def criar_janela():
    sg.theme("DarkBlue3")
    sg.set_options(
        font=("Segoe UI", 10),
        element_padding=(8, 6),
    )

    cabecalho = [
        [sg.Text("Sistema de Cadastro de Alunos",
                 font=("Segoe UI", 18, "bold"),
                 text_color="#FFFFFF",
                 pad=((0, 0), (8, 18)))]
    ]

    formulario = [
        [sg.Text("Matrícula", size=(18, 1)),
         sg.Input(key="-MATRICULA-", size=(31, 1),
                  enable_events=True)],
        [sg.Text("Nome", size=(18, 1)),
         sg.Input(key="-NOME-", size=(31, 1),
                  enable_events=True)],
        [sg.Text("Endereço", size=(18, 1)),
         sg.Input(key="-ENDERECO-", size=(31, 1))],
        [sg.Text("Data de nascimento", size=(18, 1)),
         sg.Input(key="-DATA-", size=(31, 1),
                  tooltip="Formato: DD/MM/AAAA")],
    ]

    botoes = [
        sg.Button("Cadastrar", key="-CADASTRAR-", size=(12, 1),
                  button_color=("white", "#2E7D32")),
        sg.Button("Alterar", key="-ALTERAR-", size=(12, 1),
                  button_color=("white", "#1565C0")),
        sg.Button("Excluir", key="-EXCLUIR-", size=(12, 1),
                  button_color=("white", "#C62828")),
        sg.Button("Limpar", key="-LIMPAR-", size=(12, 1),
                  button_color=("white", "#455A64")),
    ]

    tabela = sg.Table(
        values=[],
        headings=["Matrícula", "Nome", "Endereço", "Data de nascimento"],
        key="-TABELA-",
        display_row_numbers=False,
        auto_size_columns=False,
        col_widths=[14, 22, 32, 20],
        justification="left",
        num_rows=12,
        alternating_row_color="#18375A",
        selected_row_colors=("white", "#2979FF"),
        enable_events=True,
        expand_x=True,
        header_font=("Segoe UI", 10, "bold"),
    )

    layout = [
        *cabecalho,
        [sg.Column(formulario, vertical_alignment="top"),
         sg.VerticalSeparator(),
         sg.Column([
             [sg.Text("Pesquisar por matrícula ou nome", font=("Segoe UI", 11, "bold"))],
             [sg.Input(key="-BUSCA-", size=(38, 1), expand_x=True),
              sg.Button("Buscar", key="-BUSCAR-", size=(10, 1),
                        button_color=("white", "#6A1B9A")),
              sg.Button("Mostrar tudo", key="-MOSTRAR-", size=(12, 1),
                        button_color=("white", "#455A64"))],
             [tabela],
             [*botoes],
         ], expand_x=True, expand_y=True)]
    ]

    return sg.Window(
        "Cadastro de Alunos",
        layout,
        size=(1050, 620),
        resizable=True,
        finalize=True,
        element_justification="left",
        modal=False,
    )


def atualizar_tabela(window, registros):
    window["-TABELA-"].update(values=registros)


def coletar_campos(values):
    return (
        values["-MATRICULA-"].strip(),
        values["-NOME-"].strip(),
        values["-ENDERECO-"].strip(),
        values["-DATA-"].strip(),
    )


def validar_campos(matricula, nome, endereco, data_nasc):
    if not matricula or not nome or not endereco or not data_nasc:
        sg.popup_error("Todos os campos são obrigatórios.", title="Dados incompletos")
        return False
    if not matricula.isdigit():
        sg.popup_error(
            "A matrícula deve conter apenas números.",
            title="Matrícula inválida",
        )
        return False
    if not all(caractere.isalpha() or caractere.isspace() for caractere in nome):
        sg.popup_error(
            "O nome deve conter apenas letras e espaços.",
            title="Nome inválido",
        )
        return False
    if not validar_data(data_nasc):
        sg.popup_error(
            "Informe uma data válida no formato DD/MM/AAAA.",
            title="Data inválida",
        )
        return False
    return True


def main():
    criar_tabela()
    window = criar_janela()
    atualizar_tabela(window, listar_alunos())
    matricula_selecionada = None

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "-SAIR-"):
            break

        if event == "-MATRICULA-" :
            texto_filtrado = "".join(
                caractere
                for caractere in values["-MATRICULA-"]
                if caractere.isdigit()
            )
            if texto_filtrado != values["-MATRICULA-"]:
                window["-MATRICULA-"].update(texto_filtrado)

        elif event == "-NOME-" :
            texto_filtrado = "".join(
                caractere
                for caractere in values["-NOME-"]
                if caractere.isalpha() or caractere.isspace()
            )
            if texto_filtrado != values["-NOME-"]:
                window["-NOME-"].update(texto_filtrado)

        elif event == "-TABELA-":
            linhas = values["-TABELA-"]
            if linhas:
                linha = linhas[0]
                registros = listar_alunos(values["-BUSCA-"].strip())
                if linha < len(registros):
                    aluno = registros[linha]
                    matricula_selecionada = aluno[0]
                    window["-MATRICULA-"].update(aluno[0])
                    window["-NOME-"].update(aluno[1])
                    window["-ENDERECO-"].update(aluno[2])
                    window["-DATA-"].update(aluno[3])

        elif event == "-CADASTRAR-":
            matricula, nome, endereco, data_nasc = coletar_campos(values)
            if not validar_campos(matricula, nome, endereco, data_nasc):
                continue
            nome = formatar_nome(nome)
            if buscar_matricula(matricula):
                sg.popup_error(
                    "Já existe um aluno com essa matrícula.",
                    title="Matrícula duplicada",
                )
                continue
            try:
                cadastrar(matricula, nome, endereco, data_nasc)
                sg.popup("Aluno cadastrado com sucesso!", title="Sucesso")
                limpar_campos(window)
                atualizar_tabela(window, listar_alunos())
                matricula_selecionada = None
            except sqlite3.IntegrityError:
                sg.popup_error(
                    "Não foi possível cadastrar. Matrícula duplicada.",
                    title="Erro",
                )

        elif event == "-ALTERAR-":
            matricula, nome, endereco, data_nasc = coletar_campos(values)
            if not validar_campos(matricula, nome, endereco, data_nasc):
                continue
            nome = formatar_nome(nome)
            if not matricula_selecionada:
                sg.popup_error(
                    "Selecione um aluno na tabela antes de alterar.",
                    title="Nenhum aluno selecionado",
                )
                continue
            if matricula != matricula_selecionada and buscar_matricula(matricula):
                sg.popup_error(
                    "Já existe um aluno com essa matrícula.",
                    title="Matrícula duplicada",
                )
                continue
            try:
                alterar(matricula_selecionada, matricula, nome, endereco, data_nasc)
                sg.popup("Aluno alterado com sucesso!", title="Sucesso")
                limpar_campos(window)
                atualizar_tabela(window, listar_alunos())
                matricula_selecionada = None
            except sqlite3.IntegrityError:
                sg.popup_error("Não foi possível alterar os dados.", title="Erro")

        elif event == "-EXCLUIR-":
            if not matricula_selecionada:
                sg.popup_error(
                    "Selecione um aluno na tabela antes de excluir.",
                    title="Nenhum aluno selecionado",
                )
                continue
            resposta = sg.popup_yes_no(
                f"Deseja realmente excluir o aluno de matrícula {matricula_selecionada}?",
                title="Confirmar exclusão",
            )
            if resposta == "Yes":
                excluir(matricula_selecionada)
                sg.popup("Aluno excluído com sucesso!", title="Sucesso")
                limpar_campos(window)
                atualizar_tabela(window, listar_alunos())
                matricula_selecionada = None

        elif event == "-LIMPAR-":
            limpar_campos(window)
            window["-BUSCA-"].update("")
            window["-TABELA-"].update(selected_rows=[])
            atualizar_tabela(window, listar_alunos())
            matricula_selecionada = None

        elif event in ("-BUSCAR-",):
            atualizar_tabela(window, listar_alunos(values["-BUSCA-"].strip()))

        elif event == "-MOSTRAR-":
            window["-BUSCA-"].update("")
            atualizar_tabela(window, listar_alunos())

    window.close()


if __name__ == "__main__":
    main()
