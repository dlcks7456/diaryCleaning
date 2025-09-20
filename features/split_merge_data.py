import streamlit as st
import os
from utils.data_loader import show_data_info
from datetime import datetime
from utils.xl_layout import set_xl_layout
import pandas as pd
import numpy as np
from utils.data_convert import convert_data
from utils.get_path import select_directory
from utils.data_loader import sort_data
from utils.column_manager import (
    get_column_manager,
    get_all_error_columns,
    get_all_check_columns,
    get_all_boolean_columns,
    get_columns_to_remove,
    get_derived_column_names
)

def split_list(split_count, _list) :
    return [list(_list[i::split_count]) for i in range(split_count)]

def pick_directory_via_dialog() -> list:
    """로컬 시스템 폴더 선택 대화상자를 띄워 여러 xlsx, csv 파일 경로를 리스트로 반환합니다."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_paths = filedialog.askopenfilenames(
            title="원시 데이터 파일(들) 선택",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All supported", "*.xlsx *.csv")
            ]
        )
        root.destroy()
        # tuple로 반환되므로 list로 변환
        return list(file_paths)
    except Exception:
        st.warning("시스템 파일 선택 대화상자를 열 수 없습니다. 경로를 직접 입력해주세요.")
        return []

def show_split_merge():
    """
    Split & Merge 페이지를 표시합니다.
    
    이 함수는 데이터를 분할하거나 병합하는 기능을 제공합니다.
    - Split: 데이터를 여러 파일로 분할하여 저장
    - Merge: 여러 파일을 하나로 병합
    """
    st.header("🚀 Split & Merge")

    raw_data = st.session_state.get("raw_data", None)
    
    # 컬럼 매니저를 통해 모든 컬럼명을 한 번에 가져옴
    column_manager = get_column_manager()
    
    # 컬럼 그룹들 가져오기
    error_columns = get_all_error_columns()
    check_columns = get_all_check_columns()
    boolean_columns = get_all_boolean_columns()
    columns_to_remove = get_columns_to_remove()
    
    # 파생 컬럼명들 가져오기
    derived_columns = get_derived_column_names()


    tab1, tab2 = st.tabs(["Split", "Merge"])

    with tab1 :
        st.subheader("💫 Split")
        
        # split_count에 따라 파일명에 들어가는 번호의 자릿수를 동적으로 결정
        split_panels = []
        success_panel_ids = []
        error_panel_ids = []
        if raw_data is not None :
            panel_no = column_manager.get_column('panel_no')
            unique_panels = [int(i) for i in raw_data[panel_no].unique()]
            max_split_count = len(unique_panels)

            select_col1, select_col2, select_col3 = st.columns([1.2, 3, 6], vertical_alignment="bottom")
            with select_col1 :
                split_type = st.selectbox("**📌 Split Type**", ["분할 (n등분)", "응답자별 분할"], index=0, width=300)

            with select_col2 :
                error_check = st.checkbox("에러 케이스만 분류하여 저장", value=True)

            if error_check :
                for panel in unique_panels :
                    panel_df = raw_data[raw_data[panel_no] == panel]
                    # boolean_columns에 해당하는 컬럼 중 하나라도 True가 있으면 안 됨 (모두 False여야 함)
                    if not (panel_df[boolean_columns] == True).any().any():
                        success_panel_ids.append(panel)
                error_panel_ids = [panel for panel in unique_panels if panel not in success_panel_ids]
                max_split_count = len(error_panel_ids)

            split_count = None
            if split_type == "분할 (n등분)":
                num_col1, num_col2, num_col3 = st.columns([0.3, 3, 1], vertical_alignment="center")
                with num_col1 :
                    split_count = st.number_input("분할 수 지정", value=2, min_value=2, max_value=max_split_count, step=1)
                with num_col2 :
                    st.write(f"<div style='margin-top: 20px;font-size: 14px;'>개 파일로 분할합니다. (최대 분할 수: {max_split_count})</div>", unsafe_allow_html=True)
            else :
                split_count = max_split_count
                st.info(f'총 {max_split_count:,}개의 파일로 분할합니다.', width=555)

            # split_count가 None이 아니면 파일명 포맷을 동적으로 생성
            if split_count is not None:
                # split_count의 자릿수 계산 (예: 9->1, 10->2, 100->3)
                digit_count = len(str(split_count))
                file_name_format = '{number:0' + str(digit_count) + 'd}_split_data.xlsx'

                target_panels = error_panel_ids if error_check else unique_panels

                split_panels = split_list(split_count, target_panels)
                col1, col2, col3 = st.columns([2, 1, 5], vertical_alignment="bottom")
                with col1 :
                    split_data_path = os.path.join(st.session_state.get("base_directory"), "split")
                    if not os.path.exists(split_data_path):
                            os.makedirs(split_data_path, exist_ok=True)

                    split_save_path = st.text_input("Save Path", value=split_data_path, disabled=True)

                with col2 :
                # Save split data
                    split_save_btn = st.button("Save Split Data", type="primary", width=200)
                    
                if split_save_btn :
                    curr_date = datetime.now().strftime('%Y%m%d')
                    save_path = os.path.join(split_save_path, curr_date)
                    if not os.path.exists(save_path):
                        os.makedirs(save_path, exist_ok=True)

                    # Progress bar creation
                    progress = st.progress(0, text="Saving split data...")

                    total = len(split_panels)

                    if success_panel_ids :
                        total += 1
                        df = raw_data[raw_data[panel_no].isin(success_panel_ids)]
                        xl_path = os.path.join(save_path, f'success_panel_data.xlsx')
                        set_xl_layout(xl_path, df, error_columns, check_columns, columns_to_remove)
                        # Update progress bar
                        progress.progress(1 / total, text=f"Success panel data saved")

                    for i, panel in enumerate(split_panels, 1):
                        file_name = file_name_format.format(number=i)
                        if split_type == "응답자별 분할" :
                            if len(panel) == 1 :
                                file_name = f'{panel[0]}_panel_data.xlsx'
                            else :
                                file_name = f'{panel[0]}-{panel[-1]}_panel_data.xlsx'
                        df = raw_data[raw_data[panel_no].isin(panel)]
                        xl_path = os.path.join(save_path, file_name)
                        set_xl_layout(xl_path, df, error_columns, check_columns, columns_to_remove)
                        # Update progress bar
                        progress.progress(i / total, text=f"{i}/{total} files saved")

                    progress.empty()
                    st.success("🚀 Split data has been saved successfully.")
                
                st.divider()

                if split_panels :
                    if success_panel_ids :
                        success_count = len(success_panel_ids)
                        st.success(f"{success_count} panels have no errors.", icon="✅")

                    if error_panel_ids :
                        error_count = len(error_panel_ids)
                        st.error(f"{error_count} panels have errors.", icon="❌")
                        
                    if not split_type == "응답자별 분할" :
                        st.info('**PANELNO Check**', icon='🔍')
                        if success_panel_ids :
                            st.markdown("##### Pass Panels")
                            success_expander = st.expander("Success Panels", expanded=False)
                            with success_expander :
                                st.markdown("**Panel List**")
                                # 패널 번호를 10개씩 한 줄에 보여주기
                                panel_str_list = [str(p) for p in sorted(success_panel_ids)]
                                chunk_size = 10
                                panel_lines = [
                                    ", ".join(panel_str_list[j:j+chunk_size])
                                    for j in range(0, len(panel_str_list), chunk_size)
                                ]
                                for idx, line in enumerate(panel_lines, 1):
                                    txt = f'''<div class="panel-line"><div class="panel-line-index">{idx}</div><div class="panel-line-panel">{line}</div></div>'''
                                    st.markdown(txt, unsafe_allow_html=True)
                            
                        st.markdown("##### Error Panels")
                        for i, panel in enumerate(split_panels, 1):
                            file_name = file_name_format.format(number=i)
                            df = raw_data[raw_data[panel_no].isin(panel)]
                            expander_text = f'{file_name} ({len(panel)} Panels / {len(df)} rows)'
                            expander = st.expander(expander_text, expanded=False)
                            with expander:
                                st.markdown("**Panel List**")
                                # 패널 번호를 10개씩 한 줄에 보여주기
                                panel_str_list = [str(p) for p in sorted(panel)]
                                chunk_size = 10
                                panel_lines = [
                                    ", ".join(panel_str_list[j:j+chunk_size])
                                    for j in range(0, len(panel_str_list), chunk_size)
                                ]
                                for idx, line in enumerate(panel_lines, 1):
                                    txt = f'''<div class="panel-line"><div class="panel-line-index">{idx}</div><div class="panel-line-panel">{line}</div></div>'''
                                    st.markdown(txt, unsafe_allow_html=True)
        else :
            st.warning("먼저 데이터를 로드해주세요.")

    with tab2 :
        st.subheader("📚 Merge")

        st.markdown('''
- `xlsx`, `csv` 만 지원합니다.
- 첫번째 시트의 데이터 기준으로 병합합니다.
- 기존 데이터 형식과 달라진 부분은 없는지 확인합니다.
''')

        file_paths = st.file_uploader("**Upload Data Files**", type=["xlsx", "csv"], accept_multiple_files=True, width=555)
                
        if file_paths:
            base_dir = st.session_state.get("base_directory")
            if base_dir:
                merge_path = os.path.join(base_dir, "merge")
                if not os.path.exists(merge_path):
                    os.makedirs(merge_path, exist_ok=True)
                save_path = merge_path
                st.text_input("Save Path", value=save_path, disabled=True, key="merge_save_path", width=550)
            else:
                path_col = st.columns([3, 2, 4.2], vertical_alignment="bottom")
                with path_col[0]:
                    save_path = st.text_input("Save Path", value="", disabled=True, width=550)
                with path_col[1]:
                    path_btn = st.button('Save Path')
                if path_btn:
                    selected_path = select_directory(f"저장 경로 선택")
                    if selected_path:
                        st.session_state["base_directory"] = selected_path
                        st.rerun()

            if not save_path == '' :
                merge_btn = st.button('Start Merge', key='merge_btn', width=555)
                if merge_btn:
                    with st.spinner('데이터를 병합하는 중입니다...'):
                        merge_dfs = []
                        for file in file_paths[::-1]:
                            file_name = file.name
                            endwith = file_name.split('.')[-1].lower()
                            if endwith == 'xlsx':
                                df = pd.read_excel(file)
                            elif endwith == 'csv':
                                df = pd.read_csv(file)
                            # columns_to_remove에 해당하는 컬럼이 df에 존재하면 삭제
                            remove_cols = [col for col in columns_to_remove if col in df.columns]
                            if remove_cols:
                                df = df.drop(columns=remove_cols)
                            df = sort_data(df)
                            merge_dfs.append(df)
                        # concat 시 index를 무시하고 새로 부여하여 이후 인덱스 관련 에러를 방지
                        merge_df = pd.concat(merge_dfs, ignore_index=True)
                        merge_df = sort_data(merge_df)

                        st.session_state["raw_data"] = merge_df

                        panel_no = column_manager.get_column('panel_no')
                        unique_panels = [int(i) for i in merge_df[panel_no].unique()]
                        merge_expander = st.expander(f'**Merge Data** : {len(merge_df)} rows ({len(unique_panels)} panels)', expanded=False)
                        with merge_expander:
                            st.dataframe(merge_df)

                        convert_data(file_name='merge_data', set_path=save_path)
                        merge_df.to_excel(os.path.join(save_path, 'merge_data.xlsx'), index=False)
                        st.success('데이터 병합이 완료되었습니다.')
                else:
                    st.info(f'{len(file_paths)}개 파일이 업로드되었습니다.', icon='🔍')
                    for file in file_paths[::-1]:
                        file_name = file.name
                        endwith = file_name.split('.')[-1].lower()
                        if endwith == 'xlsx':
                            df = pd.read_excel(file)
                        elif endwith == 'csv':
                            df = pd.read_csv(file)
                        remove_cols = [col for col in columns_to_remove if col in df.columns]
                        if remove_cols:
                            df = df.drop(columns=remove_cols)
                        df = sort_data(df)
                        
                        panel_no = column_manager.get_column('panel_no')
                        unique_panels = [int(i) for i in df[panel_no].unique()]
                        expander = st.expander(f'**{file_name}** : {len(df)} rows ({len(unique_panels)} panels)', expanded=False)
                        with expander:
                            st.dataframe(df)