import pandas as pd
import streamlit as st


# Função para calcular as métricas
def calculate_metrics(df, start_date, end_date):
    # Converter as datas para datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrar o DataFrame com base nas datas selecionadas
    filtered_df = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]

    # Calcular o máximo acumulado e drawdown
    filtered_df['DD_MAX'] = filtered_df['BALANCE'].cummax()
    dd_max = filtered_df['DD_MAX'] - filtered_df['BALANCE']

    # Adicionar uma coluna 'DATE_ONLY' apenas com a data
    filtered_df['DATE_ONLY'] = filtered_df['DATE'].dt.date
    daily_balance = filtered_df.groupby('DATE_ONLY')['BALANCE'].last().reset_index()

    # Filtrar os dias com saldo diário positivo
    positive_days = daily_balance[daily_balance['BALANCE'] > daily_balance['BALANCE'].shift(fill_value=0)]

    # Calcular as métricas
    metrics = {
        "Deposito": filtered_df['BALANCE'].iloc[0],
        "Lucro Bruto": filtered_df['BALANCE'].iloc[-1] - filtered_df['BALANCE'].iloc[0],
        "Lucro Máximo": filtered_df['BALANCE'].max() - filtered_df['BALANCE'].iloc[0],
        "Drawdown Relativo": filtered_df['BALANCE'].min() - filtered_df['BALANCE'].iloc[0],
        "Drawdown Maximo": round(dd_max.max(), 2),
        "Drawdown Medio": round(dd_max.mean(), 2),
        "Dias": filtered_df['DATE'].dt.date.nunique(),
        "Dias Positivos": positive_days['DATE_ONLY'].nunique()
    }
    return metrics


# Função para criar o dashboard
def create_dash(df):
    # Adicionar um seletor de data
    st.subheader("Filtrar por Data")
    col01, col02, col03 = st.columns(3)

    with col01:
        start_date = st.date_input("Data de Início", df['DATE'].min().date())

    with col02:
        end_date = st.date_input("Data de Término", df['DATE'].max().date())

    with col03:
        if st.button("Todo Histórico"):
            start_date = df['DATE'].min()
            end_date = df['DATE'].max()

    # Calcular métricas
    metrics = calculate_metrics(df, start_date, end_date)

    # Exibir métricas
    tab1, tab2 = st.tabs([":old_key: Básico", ":zap: Avançado"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            c = st.container()
            c.caption('RETORNO')
            c.metric(label="Lucro: ", value=f"R${metrics['Lucro Bruto']:.2f}")
            c.metric(label="Lucro Max: ", value=f"R${metrics['Lucro Máximo']:.2f}")
        with col2:
            c = st.container()
            c.caption('RISCO')
            c.metric(label="Drawdown Médio: ", value=f"R${metrics['Drawdown Medio']:.2f}")
            c.metric(label="Drawdown Máximo: ", value=f"R${metrics['Drawdown Maximo']:.2f}")

        if start_date <= end_date:
            filtered_df = df[(df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(end_date))]
            valor_inicial = filtered_df['BALANCE'].iloc[0]
            st.line_chart(filtered_df.set_index('DATE')['BALANCE'] - valor_inicial)
        else:
            st.error("Erro: A data de início deve ser menor ou igual à data de término.")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            c = st.container()
            c.caption('RETORNO AVANÇADO')
            tipo_retorno = c.radio("Tipo", ["Relativo", "Absoluto"], key='tipo_retorno')
            if tipo_retorno == "Absoluto":
                c.metric(label="Lucro: ", value=f"R${metrics['Lucro Bruto']:.2f}")
                c.metric(label="Lucro Max: ", value=f"R${metrics['Lucro Máximo']:.2f}")
            else:
                aporte = c.number_input("Depósito ($)", min_value=100, value=1000, step=100, key='aporte')
                c.metric(label="Lucro: ", value="{:.2f}%".format((100 * metrics['Lucro Bruto']) / aporte))
                c.metric(label="Lucro Max: ", value="{:.2f}%".format((100 * metrics['Lucro Máximo']) / aporte))
        with col2:
            c = st.container()
            c.caption('RISCO AVANÇADO')
            tipo_risco = c.radio("Tipo", ["Relativo", "Absoluto"], key='tipo_risco')
            if tipo_risco == "Absoluto":
                c.metric(label="Total Dias: ", value=metrics['Dias'])
                c.metric(label="Positivos: ", value=metrics['Dias Positivos'])
            else:
                c.metric(label="Total Dias: ", value=metrics['Dias'])
                c.metric(label="Positivos: ",
                         value="{:.2f}%".format((metrics['Dias Positivos'] / metrics['Dias']) * 100))

        if start_date <= end_date:
            filtered_df = df[(df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(end_date))]
            filtered_df['DD_MAX'] = filtered_df['BALANCE'].cummax()
            st.line_chart(-1 * (filtered_df['DD_MAX'] - filtered_df['BALANCE']), color="#FF0055")
        else:
            st.error("Erro: A data de início deve ser menor ou igual à data de término.")

# Exemplo de uso (remova isso quando integrar com seu projeto principal)
# df = pd.read_csv("seu_arquivo.csv")  # Carregar seu DataFrame aqui
# create_dash(df)
