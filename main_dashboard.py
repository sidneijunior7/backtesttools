import pandas as pd
import streamlit as st


def calculate_metrics(df, start_date, end_date):
    # Converter as datas para datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrar o DataFrame com base nas datas selecionadas
    filtered_df = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]

    # Calcular o máximo acumulado e drawdown
    filtered_df['DD_MAX'] = filtered_df['BALANCE'].cummax()
    dd_max = filtered_df['DD_MAX'] - filtered_df['BALANCE']

    # Calcular as métricas
    metrics = {
        "Deposito": filtered_df['BALANCE'].iloc[0],
        "Lucro Bruto": filtered_df['BALANCE'].iloc[-1] - filtered_df['BALANCE'].iloc[0],
        "Lucro Máximo": filtered_df['BALANCE'].max() - filtered_df['BALANCE'].iloc[0],
        "Drawdown Relativo": filtered_df['BALANCE'].min() - filtered_df['BALANCE'].iloc[0],
        "Drawdown Maximo": round(dd_max.max(), 2),
        "Drawdown Medio": round(dd_max.mean(), 2)
    }
    return metrics


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
    st.subheader("Métricas")

    col1, col2 = st.columns(2)
    with col1:
        c = st.container(border=True)
        c.caption('Retorno')
        c.metric(label="Lucro: ", value=metrics['Lucro Bruto'])
        c.metric(label="Lucro Max: ", value=metrics['Lucro Máximo'])
    with col2:
        c = st.container(border=True)
        c.caption('Risco')
        c.metric(label="Drawdown Médio: ", value=metrics['Drawdown Medio'])
        c.metric(label="Drawdown Máximo: ", value=metrics['Drawdown Maximo'])

    if start_date <= end_date:
        filtered_df = df[(df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(end_date))]
        valor_inicial = filtered_df['BALANCE'].iloc[0]
        st.line_chart(filtered_df.set_index('DATE')['BALANCE'] - valor_inicial)
    else:
        st.error("Erro: A data de início deve ser menor ou igual à data de término.")


    return None