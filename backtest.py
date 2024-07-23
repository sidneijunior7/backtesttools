import os
import pandas as pd
import streamlit as st
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-16', sep='\t')
        # Renomear as colunas
        df.rename(columns={'<DATE>': 'DATE', '<BALANCE>': 'BALANCE', '<EQUITY>': 'EQUITY'}, inplace=True)

        # Converter a coluna 'DATE' para datetime
        try:
            df['DATE'] = pd.to_datetime(df['DATE'], format='%Y.%m.%d %H:%M')
        except ValueError:
            st.error("Error: Date format is incorrect. Please check the date format in the file.")
            st.stop()

    except Exception as e:
        print(e)
        return None
    return df

def save_csv(uploaded_file, username, backtest_name):
    user_folder = os.path.join('backtests', username)
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, f"{backtest_name}.csv")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def visualize_backtest(file_path):
    df = load_csv(file_path)
    if df is not None:
        return df
    else:
        return None
