import pandas as pd
import streamlit as st
import os
from datetime import datetime
from features.setting import get_column_name

def save_log_data() :
    log_path = st.session_state.get("log_save_path")
    raw_data_path = st.session_state.get("raw_data_path")

    # log_path가 설정되어 있고 유효한 경우 사용
    if log_path and log_path.strip():
        save_path = log_path
    # raw_data_path가 유효한 경우, 해당 디렉토리에 log 폴더 생성
    elif raw_data_path and raw_data_path.strip() and os.path.exists(raw_data_path):
        save_path = os.path.join(os.path.dirname(raw_data_path), 'log')
    # 둘 다 없는 경우 현재 작업 디렉토리에 log 폴더 생성
    else:
        save_path = os.path.join(os.getcwd(), 'log')
        st.warning("⚠️ 로그 저장 경로가 설정되지 않아 현재 작업 디렉토리에 저장합니다.")

    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    curr_datetime = datetime.now().strftime('%Y%m%d')
    file_name = f'log_{curr_datetime}.csv'
    log_csv = os.path.join(save_path, file_name)
    st.session_state['log_data'].to_csv(log_csv, index=False, encoding='cp949')


def record_log(data: pd.DataFrame, date: str, type: str, error_type: str) :
    delete_df = data.copy()
    raw_columns = delete_df.columns.tolist()
    delete_df['ERROR_TYPE'] = error_type
    delete_df['UPDATED_DATE'] = date
    delete_df['METHOD'] = type
    delete_df = delete_df[['ERROR_TYPE', 'UPDATED_DATE', 'METHOD', *raw_columns]]
    delete_df.reset_index(drop=True, inplace=True)
    st.session_state['log_data'] = pd.concat([st.session_state['log_data'], delete_df], ignore_index=True)
    st.session_state['log_data'].drop_duplicates(inplace=True)

    save_log_data()