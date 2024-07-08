import Database as db
from Database import *
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(layout="wide")
col1, col2, col3 = st.columns(3)

with col1:
    st.write("")

with col2:
    st.title("🐾 Rede de Atenção Animal")

with col3:
    st.write("")

connection = get_connection()

if connection is None:
    st.error("Erro ao conectar com o banco de dados. Verifique as configurações e tente novamente.")
else:
    db.create_all_tables(connection)
    db.create_audit_procedure(connection)

bairrosJgua = [
    "Água Verde", "Águas Claras", "Amizade", "Barra do Rio Cerro", "Barra do Rio Molha",
    "Boa Vista", "Braço Ribeirão Cavalo", "Centenário", "Centro", "Chico de Paulo",
    "Czerniewicz", "Estrada Nova", "Ilha da Figueira", "Jaraguá 84", "Jaraguá 99",
    "Jaraguá Esquerdo", "João Pessoa", "Nereu Ramos", "Nova Brasília",
    "Rau", "Ribeirão Cavalo", "Rio Cerro I", "Rio Cerro II", "Rio da Luz",
    "Rio Molha", "Santa Luzia", "Santo Antônio", "São Luís",
    "Tifa Martins", "Tifa Monos", "Três Rios do Norte", "Três Rios do Sul", "Vieira",
    "Vila Baependi", "Vila Lalau", "Vila Lenzi", "Vila Nova"
]

causas = ["Atropelamento", "Miiase", "Dermatite", "Tumor", "Lesão Ocular", "Lesões de Pele Ulcerada", "Outros"]

def get_clinicas():
    with connection.cursor() as cursor:
        cursor.execute("SELECT NOME_CLINICA FROM CLINICA")
        return [cli[0] for cli in cursor.fetchall()]

global clinicas
clinicas = get_clinicas()

def main():

    page = option_menu(
        "Navegação",
        ["Página Inicial", "Programa Emergencial Cães e Gatos", "Resgate Fauna", "Controle Populacional/Castração"],
        icons=['house', 'check', 'check', 'check'],
        menu_icon="globe",
        default_index=0,
        orientation="vertical"
    )

    if page == "Página Inicial":
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("")

        with col2:
            st.subheader("Integrantes do Grupo:")
            st.subheader("Luciano Zimmermann")
            st.subheader("Luiz Uber")
            st.subheader("Matheus Lorenzetti")
            st.subheader("Rafael Gadotti")
            st.subheader("Yuri Pereira")
            st.write("Bem-vindo à Página Inicial do Fujama")
            st.image("https://assets.infra.grancursosonline.com.br/projeto/fujama-sc-1685036431.jpg")

        with col3:
            st.write("")

    elif page == "Programa Emergencial Cães e Gatos":

        subpage = option_menu(
            "Atendimento Emergencial",
            ["Cadastrar Atendimento", "Filtrar Atendimentos", "Deletar Atendimentos"],
            icons=['house', 'check', 'check'],
            menu_icon="menu",
            default_index=0,
            orientation="vertical"
        )

        if subpage == "Cadastrar Atendimento":
            st.title("Cadastrar Atendimento")
            with st.form("atendimento_form"):
                st.subheader("Cadastrar Animal")
                nomeAnimal = st.text_input(label="Nome do Animal", key="nomeAnimal")
                sexo = st.selectbox(label="Sexo [Obrigatório]", options=["M", "F"], key="sexo")
                especie = st.selectbox(label="Espécie [Obrigatório]", options=["CACHORRO", "GATO"], key="especie")
                porte = st.selectbox(label="Porte [Obrigatório]", options=["PEQUENO", "MÉDIO", "GRANDE"], key="porte")
                obs = st.text_area(label="Observações", key="obs")

                st.subheader("Motivo do Atendimento")
                causa = st.selectbox(label="Causas [Obrigatório]", options=causas, key="causa")

                st.subheader("Cadastrar Clínica")
                clinica_choice = st.selectbox(
                    label="Nome da Clínica [Obrigatório]",
                    options=["Selecionar existente"] + clinicas
                )

                if clinica_choice == "Selecionar existente":
                    nomeClinica = st.text_input("Nome da nova clínica", key="nomeNovaClinica")
                    cadastrar_nova_clinica = True
                else:
                    nomeClinica = clinica_choice
                    cadastrar_nova_clinica = False

                st.subheader("Local da Ocorrência")
                rua = st.text_input(label="Rua")
                bairro = st.selectbox(label="Bairro [Obrigatório]", options=bairrosJgua, key="bairro")

                st.subheader("Data do Atendimento")
                data_atendimento = st.date_input("Data do Atendimento [Obrigatório]", key="data_atendimento")

                submit = st.form_submit_button("Salvar")

                if submit:
                    if all([sexo, especie, porte, nomeClinica, causa, bairro]):
                        try:
                            with connection.cursor() as cursor:
                                if cadastrar_nova_clinica:
                                    cursor.execute("INSERT INTO CLINICA (NOME_CLINICA) VALUES (%s)", (nomeClinica,))
                                    connection.commit()
                                    cli_id = cursor.lastrowid
                                    clinicas.append(nomeClinica)
                                else:
                                    cursor.execute("SELECT IDCLINICA FROM CLINICA WHERE NOME_CLINICA = %s",
                                                   (nomeClinica,))
                                    result = cursor.fetchone()
                                    if result:
                                        cli_id = result[0]
                                    else:
                                        st.error("Erro: Clínica selecionada não encontrada.")
                                        cli_id = None

                                if cli_id:
                                    animal_sql = "INSERT INTO ANIMAL (NOME_ANIMAL, SEXO, ESPECIE, PORTE, CAUSA, OBS) VALUES (%s, %s, %s, %s, %s, %s)"
                                    animal_params = (nomeAnimal, sexo, especie, porte, causa, obs)
                                    cursor.execute(animal_sql, animal_params)
                                    animal_id = cursor.lastrowid

                                    endereco_sql = "INSERT INTO ENDERECO (RUA, BAIRRO) VALUES (%s, %s)"
                                    bairro_params = (rua, bairro)
                                    cursor.execute(endereco_sql, bairro_params)
                                    endereco_id = cursor.lastrowid

                                    atendimento_sql = "INSERT INTO ATENDIMENTO (DATA, ANIMAL_ID, CLINICA_ID, ENDERECO_ID) VALUES (%s, %s, %s, %s)"
                                    atendimento_params = (data_atendimento, animal_id, cli_id, endereco_id)
                                    cursor.execute(atendimento_sql, atendimento_params)
                                    cursor.callproc('sp_audit_atendimento', ('INSERT', cursor.lastrowid))
                                    db.create_audit_trigger(connection)
                                    connection.commit()

                                    st.success("Atendimento cadastrado com sucesso!")
                        except Exception as e:
                            connection.rollback()
                            st.error(f"Erro ao inserir dados no banco de dados: {e}")
                    else:
                        st.warning("Por favor, preencha todos os campos obrigatórios.")

        elif subpage == "Filtrar Atendimentos":
            st.subheader("Filtrar Atendimentos")
            filtro = st.selectbox(label="Filtrar Atendimentos", options=["Dia", "Mês", "Ano", "Filtrar Todos"])

            if filtro == "Ano":
                year = datetime.now().year
                ano_filtro = st.text_input(label="Ano:", key="ano_filtro", value=year)
                query_atendimento = f"""
                SELECT 
                    a.IDATENDIMENTO, a.DATA, 
                    an.NOME_ANIMAL, an.ESPECIE, an.PORTE, an.SEXO, an.CAUSA,
                    c.NOME_CLINICA,
                    e.RUA, e.BAIRRO,
                    an.OBS AS OBS_ANIMAL
                FROM atendimento a
                JOIN animal an ON a.ANIMAL_ID = an.IDANIMAL
                JOIN clinica c ON a.CLINICA_ID = c.IDCLINICA
                JOIN endereco e ON a.ENDERECO_ID = e.IDENDERECO
                WHERE YEAR(a.DATA) = '{ano_filtro}'
                AND a.DELETED = FALSE
                """

            elif filtro == "Dia":
                dia_filtro = st.date_input("Data do Atendimento [Obrigatório]", key="data_atendimento")
                query_atendimento = f"""
                SELECT 
                    a.IDATENDIMENTO, a.DATA, 
                    an.NOME_ANIMAL, an.ESPECIE, an.PORTE, an.SEXO, an.CAUSA,
                    c.NOME_CLINICA,
                    e.RUA, e.BAIRRO,
                    an.OBS AS OBS_ANIMAL
                FROM atendimento a
                JOIN animal an ON a.ANIMAL_ID = an.IDANIMAL
                JOIN clinica c ON a.CLINICA_ID = c.IDCLINICA
                JOIN endereco e ON a.ENDERECO_ID = e.IDENDERECO
                WHERE a.DATA = '{dia_filtro}'
                AND a.DELETED = FALSE
                """

            elif filtro == "Mês":
                year = datetime.now().year
                ano_filtro = st.number_input(label="Ano:", key="ano_filtro_mes", format='%d', step=1, min_value=1900,value=year)
                if ano_filtro != 0:
                    mes_filtro = st.selectbox("Mês:", options=[datetime(ano_filtro, i, 1).strftime('%B') for i in range(1, 13)],key="mes_filtro")
                    mes_num = datetime.strptime(mes_filtro, '%B').month
                    query_atendimento = f"""
                                    SELECT 
                                        a.IDATENDIMENTO, a.DATA, 
                                        an.NOME_ANIMAL, an.ESPECIE, an.PORTE, an.SEXO, an.CAUSA,
                                        c.NOME_CLINICA,
                                        e.RUA, e.BAIRRO,
                                        an.OBS AS OBS_ANIMAL
                                    FROM atendimento a
                                    JOIN animal an ON a.ANIMAL_ID = an.IDANIMAL
                                    JOIN clinica c ON a.CLINICA_ID = c.IDCLINICA
                                    JOIN endereco e ON a.ENDERECO_ID = e.IDENDERECO
                                    WHERE MONTH(a.DATA) = '{mes_num}'
                                    AND YEAR(a.DATA) = '{ano_filtro}'
                                    AND a.DELETED = FALSE
                                    """
                else:
                    st.error("Por favor, insira um ano válido.")

            elif filtro == "Filtrar Todos":
                query_atendimento = """
                SELECT 
                    a.IDATENDIMENTO, a.DATA, 
                    an.NOME_ANIMAL, an.ESPECIE, an.PORTE, an.SEXO, an.CAUSA,
                    c.NOME_CLINICA,
                    e.RUA, e.BAIRRO,
                    an.OBS AS OBS_ANIMAL
                FROM atendimento a
                JOIN animal an ON a.ANIMAL_ID = an.IDANIMAL
                JOIN clinica c ON a.CLINICA_ID = c.IDCLINICA
                JOIN endereco e ON a.ENDERECO_ID = e.IDENDERECO
                WHERE a.DELETED = FALSE
                """

            if st.button("Filtrar Atendimentos"):
                result_atendimento = db.select_table(connection, query_atendimento)

                data_atendimento = pd.DataFrame(result_atendimento,
                                                columns=['ID Atendimento', 'Data', 'Nome Animal', 'Espécie', 'Porte',
                                                         'Sexo', 'Causa', 'Nome Clinica', 'Rua', 'Bairro',
                                                         'Obs Animal'])
                st.write(data_atendimento)

        elif subpage == "Deletar Atendimentos":
            st.subheader("Deletar Atendimentos")

            with st.form("delete_form"):
                id = st.text_input(label="ID:", key="id")
                consultar = st.form_submit_button("Consultar")

                sql_consulta = f"""
                                SELECT 
                                    a.IDATENDIMENTO, a.DATA, 
                                    an.NOME_ANIMAL, an.ESPECIE, an.PORTE, an.SEXO, an.CAUSA,
                                    c.NOME_CLINICA,
                                    e.RUA, e.BAIRRO,
                                    an.OBS AS OBS_ANIMAL
                                FROM atendimento a
                                JOIN animal an ON a.ANIMAL_ID = an.IDANIMAL
                                JOIN clinica c ON a.CLINICA_ID = c.IDCLINICA
                                JOIN endereco e ON a.ENDERECO_ID = e.IDENDERECO
                                WHERE a.DELETED = FALSE
                                AND a.IDATENDIMENTO = '{id}'
                                """

                if consultar:
                    result_atendimento = db.select_table(connection, sql_consulta)

                    data_atendimento = pd.DataFrame(result_atendimento,
                                                    columns=['ID Atendimento', 'Data', 'Nome Animal', 'Espécie',
                                                             'Porte',
                                                             'Sexo', 'Causa', 'Nome Clinica', 'Rua', 'Bairro',
                                                             'Obs Animal'])
                    st.write(data_atendimento)

                deletar = st.form_submit_button("Deletar")

                if deletar:
                    try:
                        soft_delete_record_atendimento(connection, 'ATENDIMENTO', record_id=id)

                        with connection.cursor() as cursor:
                            cursor.callproc('sp_audit_atendimento', ('DELETE', id))
                            connection.commit()

                        st.success(f"Atendimento ID {id} deletado com sucesso!")
                    except Exception as e:
                        connection.rollback()
                        st.error(f"Erro ao deletar o atendimento ID {id}: {e}")

                deleter_def = st.form_submit_button("Deletar em definitivo")

                if deleter_def:
                    real_delete_atendimento(connection, 'ATENDIMENTO', record_id=id)

    elif page == "Resgate Fauna":
        subpage = option_menu(
            "Fauna",
            ["Cadastrar Resgate", "Filtrar Resgates", "Deletar Resgates"],
            icons=['check', 'check'],
            menu_icon="globe",
            default_index=0,
            orientation="vertical"
        )

        if subpage == "Cadastrar Resgate":
            st.subheader("Resgate Fauna")
            with st.form("fauna_form"):
                st.subheader("Cadastrar Animal Silvestre")
                especie = st.text_input(label="Espécie do Animal", key="especie")
                bairro = st.selectbox(label="Bairro", options=bairrosJgua)
                data_atendimento = st.date_input("Data do Atendimento", key="data_atendimento")
                obs = st.text_area(label="Observações", key="obs")

                submit = st.form_submit_button("Salvar")

                if submit:
                    if all([especie, bairro, data_atendimento]):
                        try:
                            with connection.cursor() as cursor:
                                silvestre_sql = "INSERT INTO SILVESTRE (ESPECIE, BAIRRO, DATA, OBS) VALUES (%s, %s, %s, %s)"
                                silvestre_params = (especie, bairro, data_atendimento, obs)
                                cursor.execute(silvestre_sql, silvestre_params)
                                connection.commit()
                                st.success("Resgate de fauna cadastrado com sucesso!")
                        except Exception as e:
                            connection.rollback()
                            st.error(f"Erro ao inserir dados no banco de dados: {e}")
                    else:
                        st.warning("Por favor, preencha todos os campos obrigatórios.")

        elif subpage == "Filtrar Resgates":
            st.subheader("Filtrar Resgates")
            filtro = st.selectbox(label="Filtrar Resgate", options=["Dia","Mês","Ano", "Filtrar Todos"])

            if filtro == "Ano":
                year = datetime.now().year
                ano_filtro = st.text_input(label="Ano:", key="ano_filtro", value=year)
                query_silvestre = (f"SELECT IDSILVESTRE, DATA, ESPECIE, BAIRRO, OBS "
                                   f"FROM SILVESTRE "
                                   f"WHERE YEAR(DATA) = '{ano_filtro}'"
                                   f"AND DELETED = FALSE")


            elif filtro == "Dia":
                dia_filtro = st.date_input("Data do Atendimento [Obrigatório]", key="data_atendimento")
                query_silvestre = (f"SELECT IDSILVESTRE, DATA, ESPECIE, BAIRRO, OBS "
                                   f"FROM SILVESTRE "
                                   f"WHERE DATA = '{dia_filtro}'"
                                   f"AND DELETED = FALSE")


            elif filtro == "Mês":
                ano_filtro = st.number_input(label="Ano:", key="ano_filtro_mes", format='%d', step=1, min_value=1900, value=2024)
                if ano_filtro != 0:
                    mes_filtro = st.selectbox("Mês:",
                                              options=[datetime(ano_filtro, i, 1).strftime('%B') for i in range(1, 13)],key="mes_filtro")
                    mes_num = datetime.strptime(mes_filtro, '%B').month

                    query_silvestre = f"""
                        SELECT IDSILVESTRE, DATA, ESPECIE, BAIRRO, OBS
                        FROM SILVESTRE
                        WHERE MONTH(DATA) = '{mes_num}' 
                        AND YEAR(DATA) = '{ano_filtro}'
                        AND DELETED = FALSE
                        """
                else:
                    st.error("Por favor, insira um ano válido.")

            elif filtro == "Filtrar Todos":
                    query_silvestre = ("SELECT IDSILVESTRE, DATA, ESPECIE, BAIRRO, OBS "
                                       "FROM SILVESTRE "
                                       "WHERE DELETED = FALSE")

            if st.button("Filtrar Atendimentos"):
                result_atendimento = db.select_table(connection, query_silvestre)

                data_atendimento = pd.DataFrame(result_atendimento,
                                                columns=['ID', 'Data', 'Espécie', 'Bairro', 'OBS'])
                st.write(data_atendimento)

        elif subpage == "Deletar Resgates":
            st.subheader("Deletar Resgates")
            with st.form("delete_form"):
                id = st.text_input(label="ID:", key="id")
                consultar = st.form_submit_button("Consultar")
                sql_consulta = f"""
                                            SELECT IDSILVESTRE, DATA, ESPECIE, BAIRRO, OBS 
                                            FROM SILVESTRE 
                                            WHERE IDSILVESTRE = '{id}'
                                            AND DELETED = FALSE
                                            """
                if consultar:
                    result_atendimento = db.select_table(connection, sql_consulta)
                    data_atendimento = pd.DataFrame(result_atendimento,
                                                    columns=['ID', 'Data', 'Espécie', 'Bairro', 'OBS'])
                    st.write(data_atendimento)
                deletar = st.form_submit_button("Deletar")
                if deletar:
                    soft_delete_record_silvestre(connection, 'SILVESTRE', record_id=id)

                deleter_def = st.form_submit_button("Deletar em definitivo")

                if deleter_def:
                    real_delete_silvestre(connection, 'SILVESTRE', record_id=id)

    elif page == "Controle Populacional/Castração":
        subpage = option_menu(
            "Controle Populacional/Castração",
            ["Relatórios Anuais", "Relatórios Mensais"],
            icons=['check', 'check'],
            menu_icon="menu",
            default_index=0,
            orientation="vertical"
        )

        if subpage == "Relatórios Anuais":
            subpage = option_menu(
                "Cadastrar Dados",
                ["Dados cadastrados", "Cadastrar Relatório Anual", "Deletar Relatório"],
                icons=['house', 'check', 'check'],
                menu_icon="menu",
                default_index=0,
                orientation="vertical"
            )

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT ANO FROM ANUAL WHERE ANO IN ('2019', '2020', '2021', '2022', '2023')")
                    existing_records = cursor.fetchall()
                    existing_years = {record['ANO'] for record in existing_records}

                    #inicia o banco com dados fornecidos pelo FUJAMA

                    data_to_insert = [
                        ('2019', 443),
                        ('2020', 1115),
                        ('2021', 1484),
                        ('2022', 2281),
                        ('2023', 2475)
                    ]

                    for record in data_to_insert:
                        if record[0] not in existing_years:
                            sql = "INSERT INTO ANUAL (ANO, ATENDIMENTOS) VALUES (%s, %s)"
                            cursor.execute(sql, record)
                    connection.commit()
            except Exception as e:
                connection.rollback()

            if subpage == "Dados cadastrados":
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT ANO, ATENDIMENTOS FROM ANUAL WHERE DELETED = FALSE")
                        records = cursor.fetchall()

                    df = pd.DataFrame(records, columns=['Ano', 'Atendimentos'])

                    st.subheader("Dados Cadastrados")
                    st.write(df)

                    st.subheader("Gráfico de Pizza dos Atendimentos por Ano")
                    pie_chart = alt.Chart(df).mark_arc().encode(
                        theta=alt.Theta(field="Atendimentos", type="quantitative"),
                        color=alt.Color(field="Ano", type="nominal"),
                        tooltip=["Ano", "Atendimentos"]
                    ).properties(
                        width=400,
                        height=400
                    )

                    st.write(pie_chart)

                    st.subheader("Gráfico de Barras Horizontais dos Atendimentos por Ano")

                    bar_chart = alt.Chart(df).mark_bar().encode(
                        x=alt.X('Atendimentos:Q', title='Número de Atendimentos'),
                        y=alt.Y('Ano:N', title='Ano'),
                        tooltip=['Ano', 'Atendimentos'],
                        color=alt.Color('Ano:N')
                    ).properties(
                        width=600,
                        height=400
                    )
                    st.write(bar_chart)

                except Exception as e:
                    st.error(f"Erro ao consultar dados do banco de dados: {e}")

            elif subpage == "Cadastrar Relatório Anual":
                try:
                    with connection.cursor() as cursor:
                        ano = datetime.today().year

                        st.write(f"Próximo ano: {ano}")

                        ano_input = st.text_input(label="Ano", value=str(ano))

                        sql_consulta_ano = "SELECT ANO FROM ANUAL WHERE ANO = %s AND DELETED = FALSE"
                        cursor.execute(sql_consulta_ano, (ano_input,))
                        result = cursor.fetchone()

                        if result is None:
                            atendimentos = int(st.number_input(label="Número de Atendimentos"))

                            sql_anual = "INSERT INTO ANUAL (ANO, ATENDIMENTOS) VALUES (%s, %s)"
                            sql_anual_params = (ano_input, atendimentos)

                            if st.button("Enviar"):
                                cursor.execute(sql_anual, sql_anual_params)
                                connection.commit()
                                st.write("Dados inseridos com sucesso!")
                        else:
                            st.write("Ano já cadastrado")

                except Exception as e:
                    connection.rollback()
                    st.error(f"Erro ao inserir dados no banco de dados: {e}")

            elif subpage == "Deletar Relatório":

                st.subheader("Deletar Resgates")

                with st.form("delete_form"):

                    ano = st.text_input(label="Ano:", key="ano")

                    consultar = st.form_submit_button("Consultar")

                    sql_consulta = f"""
                                        SELECT ANO, ATENDIMENTOS FROM ANUAL 
                                        WHERE ANO = '{ano}' 
                                        AND DELETED = FALSE
                                        """

                    if consultar:
                        result_atendimento = db.select_table(connection, sql_consulta)

                        data_atendimento = pd.DataFrame(result_atendimento,
                                                        columns=['Ano', 'Atendimentos'])
                        st.write(data_atendimento)

                    deletar = st.form_submit_button("Deletar")

                    if deletar:
                        soft_delete_record_anual(connection, 'ANUAL', record_id=ano)

                    deleter_def = st.form_submit_button("Deletar em definitivo")

                    if deleter_def:
                        real_delete_anual(connection, 'ANUAL', record_id=ano)

        elif subpage == "Relatórios Mensais":
            subpage = option_menu(
                "Cadastrar Dados",
                ["Cadastrar Relatório Mensal", "Filtrar Relatório Mensal", "Deletar Relatório Mensal"],
                icons=['house', 'check', 'check'],
                menu_icon="menu",
                default_index=0,
                orientation="vertical"
            )

            if subpage == "Cadastrar Relatório Mensal":
                st.title("Cadastrar Relatório Mensal")
                with st.form("mensal_form"):
                    st.subheader("Informações da Clínica")
                    clinica_choice = st.selectbox(
                        label="Nome da Clínica [Obrigatório]",
                        options=["Selecionar existente"] + clinicas
                    )

                    if clinica_choice == "Selecionar existente":
                        nomeClinica = st.text_input("Nome da nova clínica", key="nomeNovaClinica")
                        cadastrar_nova_clinica = True
                    else:
                        nomeClinica = clinica_choice
                        cadastrar_nova_clinica = False

                    st.subheader("Informações do Relatório Mensal")
                    data_relatorio = st.date_input("Data do Relatório [Obrigatório]")
                    atendimentos_cao = st.number_input("Número de Atendimentos de Cães [Obrigatório]", min_value=0,
                                                       step=1)
                    atendimentos_gato = st.number_input("Número de Atendimentos de Gatos [Obrigatório]", min_value=0,
                                                        step=1)

                    submit = st.form_submit_button("Cadastrar")

                    if submit:
                        if nomeClinica and data_relatorio and atendimentos_cao is not None and atendimentos_gato is not None:
                            try:
                                with connection.cursor() as cursor:
                                    if cadastrar_nova_clinica:
                                        cursor.execute("INSERT INTO CLINICA (NOME_CLINICA) VALUES (%s)", (nomeClinica,))
                                        connection.commit()
                                        cli_id = cursor.lastrowid
                                        clinicas.append(nomeClinica)
                                    else:
                                        cursor.execute("SELECT IDCLINICA FROM CLINICA WHERE NOME_CLINICA = %s",
                                                       (nomeClinica,))
                                        result = cursor.fetchone()
                                        if result:
                                            cli_id = result[0]
                                        else:
                                            st.error("Erro: Clínica selecionada não encontrada.")
                                            cli_id = None

                                    if cli_id:
                                        cursor.execute("""
                                            INSERT INTO mes (CLINICA_ID, MOMENT, DELETED, ATENDIMENTOS_CAO, ATENDIMENTOS_GATO)
                                            VALUES (%s, %s, 0, %s, %s)
                                        """, (cli_id, data_relatorio, atendimentos_cao, atendimentos_gato))
                                        connection.commit()
                                        st.success("Relatório mensal cadastrado com sucesso!")
                            except pymysql.MySQLError as e:
                                connection.rollback()
                                st.error(f"Erro ao inserir dados no banco de dados: {e}")
                        else:
                            st.warning("Por favor, preencha todos os campos obrigatórios.")

            elif subpage == "Filtrar Relatório Mensal":
                st.subheader("Filtrar Relatórios Mensais")
                filtro = st.selectbox(label="Filtrar Relatório", options=["Clinica", "Mês", "Ano", "Filtrar Todos"])

                if filtro == "Ano":
                    year = datetime.now().year
                    ano_filtro = st.text_input(label="Ano:", key="ano_filtro", value=year)
                    query_mes = f"""
                            SELECT IDMES, MOMENT, c.NOME_CLINICA, ATENDIMENTOS_CAO, ATENDIMENTOS_GATO 
                            FROM mes 
                            JOIN clinica c
                            ON mes.CLINICA_ID = c.IDCLINICA
                            WHERE YEAR(MOMENT) = '{ano_filtro}' 
                            AND mes.DELETED = FALSE
                        """

                elif filtro == "Clinica":
                    clinica_filtro = st.selectbox("Clinica", key="clinica", options=clinicas)
                    query_mes = f"""
                                SELECT IDMES, MOMENT, c.NOME_CLINICA, ATENDIMENTOS_CAO, ATENDIMENTOS_GATO 
                                FROM mes 
                                JOIN clinica c
                                ON mes.CLINICA_ID = c.IDCLINICA
                                WHERE c.NOME_CLINICA = '{clinica_filtro}' 
                                AND mes.DELETED = FALSE
                            """

                elif filtro == "Mês":
                    ano_filtro = st.number_input(label="Ano:", key="ano_filtro_mes", format='%d', step=1,
                                                 min_value=1900, value=datetime.now().year)
                    if ano_filtro != 0:
                        mes_filtro = st.selectbox("Mês:", options=[datetime(ano_filtro, i, 1).strftime('%B') for i in
                                                                   range(1, 13)], key="mes_filtro")
                        mes_num = datetime.strptime(mes_filtro, '%B').month

                        query_mes = f"""
                                SELECT IDMES, MOMENT, c.NOME_CLINICA, ATENDIMENTOS_CAO, ATENDIMENTOS_GATO 
                                FROM mes 
                                JOIN clinica c
                                ON mes.CLINICA_ID = c.IDCLINICA
                                WHERE MONTH(MOMENT) = '{mes_num}' 
                                AND YEAR(MOMENT) = '{ano_filtro}' 
                                AND mes.DELETED = FALSE
                            """
                    else:
                        st.error("Por favor, insira um ano válido.")

                elif filtro == "Filtrar Todos":
                    query_mes = """
                            SELECT IDMES, MOMENT, c.NOME_CLINICA, ATENDIMENTOS_CAO, ATENDIMENTOS_GATO 
                            FROM mes 
                            JOIN clinica c
                            ON mes.CLINICA_ID = c.IDCLINICA
                            WHERE mes.DELETED = FALSE
                        """

                if st.button("Filtrar Atendimentos"):
                    result_atendimento = db.select_table(connection, query_mes)

                    data_atendimento = pd.DataFrame(result_atendimento,
                                                    columns=['ID', 'Data', 'Nome da Clínica', 'Atendimentos Cão', 'Atendimentos Gato'])
                    st.write(data_atendimento)

            elif subpage == "Deletar Relatório Mensal":
                st.subheader("Deletar Relatório Mensal")
                with st.form("delete_form"):
                    id = st.text_input(label="ID do Relatório:", key="id")
                    consultar = st.form_submit_button("Consultar")

                    if consultar:
                        sql_consulta = (f"""
                                SELECT m.IDMES, m.MOMENT, c.NOME_CLINICA, m.ATENDIMENTOS_CAO, m.ATENDIMENTOS_GATO 
                                FROM mes m
                                INNER JOIN CLINICA c ON m.CLINICA_ID = c.IDCLINICA
                                WHERE m.IDMES = '{id}'
                                AND m.DELETED = FALSE
                            """)

                        try:
                            with connection.cursor() as cursor:
                                cursor.execute(sql_consulta)
                                result_atendimento = cursor.fetchall()

                            if result_atendimento:
                                data_atendimento = pd.DataFrame(result_atendimento,
                                                                columns=['ID', 'Data', 'Nome da Clínica',
                                                                         'Atendimentos Cão', 'Atendimentos Gato'])
                                st.write(data_atendimento)
                            else:
                                st.warning("Nenhum relatório encontrado com esse ID.")
                        except pymysql.MySQLError as e:
                            st.error(f"Erro ao consultar o banco de dados: {e}")

                    deletar = st.form_submit_button("Deletar")
                    if deletar:
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute("UPDATE mes SET DELETED = TRUE WHERE IDMES = %s", (id,))
                                connection.commit()
                                st.success("Relatório deletado com sucesso!")
                        except pymysql.MySQLError as e:
                            connection.rollback()
                            st.error(f"Erro ao deletar o relatório: {e}")

                    deletar_def = st.form_submit_button("Deletar em definitivo")

                    if deletar_def:
                        real_delete_mensal(connection, 'MES', record_id=id)


if __name__ == "__main__":
    main()



