import streamlit as st
import streamlit_authenticator as stauth
import os
from database import create_connection, create_table, insert_backtest, get_user_backtests, delete_backtest
from backtest import save_csv, visualize_backtest
import hashlib
from main_dashboard import create_dash


# Função para gerar hash de senhas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Configuração de autenticação
credentials = {
    'usernames': {
        'sidneijunior': {
            'name': 'Junior',
            'password': 'sssj170795'
        },
        'user2': {
            'name': 'User Two',
            'password': hash_password('password2')
        }
    }
}

# Inicializar a autenticação
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name='cookie_name',
    cookie_key='signature_key',
    cookie_expiry_days=30
)

# Tela de login
name, authentication_status, username = authenticator.login('main')


# Função para verificar a senha
def verify_password(username, password, credentials):
    hashed_password = hash_password(password)
    if username in credentials['usernames']:
        stored_password = credentials['usernames'][username]['password']
        return hashed_password == stored_password
    return False


if authentication_status:
    st.sidebar.success(f"Bem-vindo, {name}")
    conn = create_connection("backtests.db")
    create_table(conn)

    # Opções após login
    st.header("O que você deseja fazer?")
    options = ["Novo Backtest", "Abrir Backtest Existente"]
    if get_user_backtests(conn, username):
        selected_option = st.selectbox("Escolha uma opção", options)
    else:
        selected_option = st.selectbox("Escolha uma opção", ["Novo Backtest"])

    if selected_option == "Novo Backtest":
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
        if uploaded_file is not None:
            backtest_name = st.text_input("Nome do Backtest")
            if st.button("Salvar Backtest"):
                file_path = save_csv(uploaded_file, username, backtest_name)
                backtest = (username, backtest_name, file_path)
                insert_backtest(conn, backtest)
                st.success("Backtest salvo com sucesso!")


    elif selected_option == "Abrir Backtest Existente":
        backtests = get_user_backtests(conn, username)
        backtest_names = [bt[2] for bt in backtests]
        selected_backtest = st.selectbox("Escolha um backtest", backtest_names)

        if selected_backtest:
            for bt in backtests:
                if bt[2] == selected_backtest:
                    file_path = bt[3]
                    df = visualize_backtest(file_path)
                    if df is not None:
                        st.write(df)
                        create_dash(df)
                    break

        if st.button("Apagar Backtest"):
            for bt in backtests:
                if bt[2] == selected_backtest:
                    delete_backtest(conn, bt[0])
                    os.remove(bt[3])
                    st.error("Backtest apagado com sucesso!")
                    st.experimental_rerun()

elif authentication_status == False:
    st.error("Nome de usuário/senha incorretos")
elif authentication_status == None:
    st.warning("Por favor, insira seu nome de usuário e senha")
