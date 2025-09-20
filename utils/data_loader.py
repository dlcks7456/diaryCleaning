import streamlit as st
import pandas as pd
import openpyxl as xl
import os
from utils.data_convert import convert_data
from features.setting import get_column_name, get_default_excel_sheet_index

def validate_file_path(file_path: str) -> bool:
    """파일 경로가 유효한지 확인합니다."""
    if not file_path:
        return False

    if not os.path.exists(file_path):
        st.error(f"❌ 파일이 존재하지 않습니다: {file_path}")
        return False

    return True

def sort_data(df):
    index_col = get_column_name('index_col')
    panel_no = get_column_name('panel_no')
    product_col = get_column_name('product_col')
    answer_date = get_column_name('answer_date')
    df = df.copy()
    df = df.sort_values([panel_no, product_col, answer_date])
    df[index_col] = range(1, len(df) + 1)
    df = df[[index_col, *[col for col in df.columns if col != index_col]]].copy()
    return df

@st.cache_data
def load_data_excel(file_path, sheet_name):
    """Excel 파일에서 데이터를 로드합니다."""
    if not validate_file_path(file_path):
        return None

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return sort_data(df)
    except Exception as e:
        st.error(f"❌ Excel 파일 읽기 오류: {str(e)}")
        return None

@st.cache_data
def load_data_csv(file_path):
    """CSV 파일에서 데이터를 로드합니다."""
    if not validate_file_path(file_path):
        return None

    try:
        df = pd.read_csv(file_path)
        return sort_data(df)
    except Exception as e:
        st.error(f"❌ CSV 파일 읽기 오류: {str(e)}")
        return None

def pick_directory_via_dialog() -> str:
    """로컬 시스템 폴더 선택 대화상자를 띄워 폴더 경로를 반환합니다."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.askopenfilename(
            title="Select the raw data file",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All supported", "*.xlsx *.csv")
            ]
        )
        root.destroy()
        return file_path or ""
    except Exception:
        st.warning("System file selection dialog cannot be opened. Please enter the path directly.")
        return ""


def show_data_upload_sidebar():
    set_raw_data_btn = None
    """사이드바에 데이터 업로드 인터페이스를 표시합니다."""

    with st.sidebar:
        if st.session_state.get("base_directory") is not None:
            st.success("✅ Data Loaded")
            path = st.session_state.get("base_directory")
            file_name = st.session_state.get("curr_file_name")
            st.text_input("Base Directory", value=path, disabled=True)
            if file_name:
                st.markdown(f'📄 `{file_name}`')
        else :
            st.header("⚒️ Set Raw Data")

            browse = st.button("Upload", key="upload_btn", width='stretch')
            if browse:
                chosen = pick_directory_via_dialog()
                if chosen:
                    st.session_state["updated_data"] = False
                    st.session_state["raw_data_path"] = chosen
                    st.session_state["raw_data"] = None


            folder_input = st.text_input(
                "Raw Data Path",
                value=st.session_state.get("raw_data_path", ""),
                disabled=True,
            )

    raw_data_path = st.session_state.get("raw_data_path")

    if raw_data_path and st.session_state.get("raw_data") is None:
        # 파일 존재 여부 확인
        if not validate_file_path(raw_data_path):
            return  # 파일이 존재하지 않으면 함수 종료

        try:
            if raw_data_path.endswith('.xlsx'):
                xl_data = xl.load_workbook(raw_data_path)
                sheets = xl_data.sheetnames

                default_index = get_default_excel_sheet_index() if len(sheets) > get_default_excel_sheet_index() else 0
                select_sheet = st.selectbox('Select the sheet', sheets, index=default_index)

                if select_sheet:
                    set_raw_data_btn = st.button(f'Read Excel: {select_sheet}', width='stretch')
                    if set_raw_data_btn:
                        raw_data = load_data_excel(raw_data_path, select_sheet)
                        if raw_data is not None:
                            st.session_state["raw_data"] = raw_data
                            convert_data()

            elif raw_data_path.endswith('.csv'):
                csv_read_btn = st.button('Read CSV File', width='stretch')
                if csv_read_btn:
                    raw_data = load_data_csv(raw_data_path)
                    if raw_data is not None:
                        st.session_state["raw_data"] = raw_data
                        convert_data()
            else:
                st.error('**Invalid file type**')


            if st.session_state["updated_data"] :
                save_btn = st.button('‼️ Modified Data Save', width='stretch', type='primary')
                if save_btn :
                    convert_data()
                    st.session_state["updated_data"] = False

        except Exception as e:
            st.error(f"❌ 파일 처리 중 오류 발생: {str(e)}")


def validate_session_file_path():
    """세션에 저장된 파일 경로가 유효한지 확인하고 필요시 초기화합니다."""
    raw_data_path = st.session_state.get("raw_data_path")

    if raw_data_path and not os.path.exists(raw_data_path):
        st.warning(f"⚠️ 저장된 파일 경로가 존재하지 않습니다. 데이터를 초기화합니다: {raw_data_path}")

def show_data_info():
    """데이터 정보를 표시합니다."""
    raw_data = st.session_state.get("raw_data")

    if raw_data is not None:
        df = raw_data.copy()

        panel_no = get_column_name('panel_no')
        total_response = len(df)
        answer_count = df[panel_no].unique().size if panel_no in df.columns else 0

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="**📊 Total Response**",
                value=f"{total_response:,} Answers"
            )

        with col2:
            st.metric(
                label="**👥 Answer Count**",
                value=f"{answer_count:,} PANELS"
            )
