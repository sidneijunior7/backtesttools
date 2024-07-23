import streamlit as st
import streamlit_authenticator as stauth
import os
from database import create_connection, create_table, insert_backtest, get_user_backtests, delete_backtest
from backtest import save_csv, visualize_backtest
from main_dashboard import create_dash
from users import users

# Inicializar a autenticação
authenticator = stauth.Authenticate(
    credentials=users(),
    cookie_name='cookie_name',
    cookie_key='signature_key',
    cookie_expiry_days=30
)
# Tela de login
name, authentication_status, username = authenticator.login('main')

def logo_theme():
    logo_light="img/logo-white.webp"
    logo_dark="img/logo-dark.png"
    # JavaScript para detectar o tema e definir o logo
    st.markdown(
        f"""
            <script>
            const setLogo = () => {{
                const theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                const logo = theme === 'dark' ? '{logo_dark}' : '{logo_light}';
                document.getElementById('logo').src = logo;
            }};
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', setLogo);
            window.addEventListener('DOMContentLoaded', setLogo);
            </script>
            """,
        unsafe_allow_html=True
    )

    return 'img/logo-white.webp'  # Logo padrão, será substituído pelo JavaScript


if authentication_status:
    st.write(logo_theme)
    st.sidebar.write(f"Bem-vindo, {name} :smile:")
    # Adicionar o botão de logout na sidebar
    authenticator.logout('Sair','sidebar',None)

    conn = create_connection("backtests.db")
    create_table(conn)

    # Adicionar as opções pós-login na sidebar
    st.sidebar.header("Opções")
    if get_user_backtests(conn, username):
        selected_option = st.sidebar.radio("Escolha uma opção", ["Novo Backtest", "Abrir Backtest Existente"])
    else:
        selected_option = st.sidebar.radio("Escolha uma opção", ["Novo Backtest"])

    # Área principal
    #st.title("Dashboard")

    if selected_option == "Novo Backtest":
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
        if uploaded_file is not None:
            backtest_name = st.text_input("Nome do Backtest")
            if st.button("Salvar Backtest"):
                file_path = save_csv(uploaded_file, username, backtest_name)
                backtest = (username, backtest_name, file_path)
                insert_backtest(conn, backtest)
                st.success("Backtest Carregado com Sucesso!")

    elif selected_option == "Abrir Backtest Existente":
        backtests = get_user_backtests(conn, username)
        backtest_names = [bt[2] for bt in backtests]
        st.sidebar.divider()
        selected_backtest = st.sidebar.radio("Escolha um backtest", backtest_names)

        if selected_backtest:
            for bt in backtests:
                if bt[2] == selected_backtest:
                    file_path = bt[3]
                    df = visualize_backtest(file_path)
                    if df is not None:
                        st.title(selected_backtest)
                        create_dash(df)
                    break

        if st.button("Apagar Backtest :no_entry:"):
            for bt in backtests:
                if bt[2] == selected_backtest:
                    delete_backtest(conn, bt[0])
                    os.remove(bt[3])
                    st.success("Backtest apagado com sucesso!")
                    st.experimental_rerun()

elif authentication_status == False:
    st.error("Nome de usuário/senha incorretos")
elif authentication_status == None:
    st.warning("Por favor, insira seu nome de usuário e senha")
