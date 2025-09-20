import pandas as pd
import numpy as np
import streamlit as st
import openpyxl as xl
import os
import re
from datetime import datetime, timedelta
from utils.xl_layout import set_xl_layout
from utils.column_manager import (
    get_column_manager,
    get_all_error_columns,
    get_all_check_columns,
    get_columns_to_remove,
    get_derived_column_names
)
from utils.data_processing import (
    split_date_columns, split_time_columns, add_duration_column,
    check_order_errors, check_count_errors, check_duplicate_times,
    add_error_columns, add_answer_combine_column, compare_previous_response_and_time
)

def convert_data(file_name='converted_data', rerun=True, set_path=None):
    """
    데이터를 변환하고 처리하는 메인 함수
    
    이 함수는 원시 데이터를 받아서 다음과 같은 처리를 수행합니다:
    1. 날짜/시간 컬럼 분리
    2. 지속시간 계산
    3. 오류 검사 및 컬럼 추가
    4. 엑셀 파일로 저장
    
    Args:
        file_name (str): 저장할 파일명 (기본값: 'converted_data')
        rerun (bool): 처리 완료 후 페이지 새로고침 여부 (기본값: True)
        set_path (str): 저장 경로 (기본값: None, 자동 결정)
    """
    raw_data = st.session_state.get("raw_data")
    if raw_data is None:
        st.warning("먼저 데이터를 로드해주세요.")
        return
    
    df = raw_data.copy()

    # 컬럼 매니저를 통해 모든 컬럼명을 한 번에 가져옴
    column_manager = get_column_manager()
    
    # 컬럼 그룹들 가져오기
    error_columns = get_all_error_columns()
    check_columns = get_all_check_columns()
    columns_to_remove = get_columns_to_remove()
    
    # 파생 컬럼명들 가져오기
    derived_columns = get_derived_column_names()
    
    # 개별 컬럼명들 가져오기
    panel_no = column_manager.get_column('panel_no')
    product_col = column_manager.get_column('product_col')
    order_col = column_manager.get_column('order_col')
    input_col = column_manager.get_column('input_col')
    start_col = column_manager.get_column('start_col')
    end_col = column_manager.get_column('end_col')
    index_col = column_manager.get_column('index_col')
    
    # 에러 컬럼명들 가져오기
    total_duration = column_manager.get_error_column('total_duration')
    answer_combine = column_manager.get_error_column('answer_combine')

    progress = st.progress(0)
    status_text = st.empty()

    # 진행 단계를 추적하기 위한 리스트
    process_steps = [
        "Remove columns",
        "Process date columns",
        "Process time columns",
        "Calculate duration",
        "Prepare error check",
        "Review panel data",
        "Add error columns",
        "Prepare data save",
        "Apply Excel styles",
        "Save complete"
    ]

    def update_status_display(current_step_idx, current_text=""):
        display_text = "**Data Conversion Progress:**\n\n"
        for i, step in enumerate(process_steps):
            if i < current_step_idx:
                display_text += f"✅ ~~{step}~~\n\n"
            elif i == current_step_idx:
                display_text += f"⏳ **{step}**\n\n"
            else:
                display_text += f"⏸️ {step}\n\n"
        status_text.markdown(display_text)

    # 1단계: 기존 컬럼 제거
    update_status_display(0)
    progress.progress(5)
    for col in columns_to_remove:
        if col in df.columns:
            df = df.drop(columns=[col])

    # 2단계: 날짜 컬럼 분리 및 추가 (함수 사용)
    update_status_display(1)
    progress.progress(15)
    df = split_date_columns(df, input_col)

    # 3단계: 시간 컬럼 데이터 처리 (함수 사용)
    update_status_display(2)
    progress.progress(25)
    df, time_data = split_time_columns(df, [start_col, end_col])

    # 4단계: 총 소요시간 계산 (함수 사용)
    update_status_display(3)
    progress.progress(35)
    df = add_duration_column(df, time_data, start_col, end_col, total_duration, derived_columns['end_min'])

    # 5단계: 오류 검사 준비
    update_status_display(4)
    progress.progress(45)

    # 6단계: 패널별 데이터 검토 (함수들 사용)
    update_status_display(5)
    progress.progress(55)

    # 순서 오류 검사
    order_answer_errors, day_order_errors, dup_errors = check_order_errors(df, panel_no, order_col, input_col)

    # 응답 수 초과 오류 검사
    count_errors = check_count_errors(df, panel_no, product_col, index_col)

    # 응답 결합 컬럼 추가 (일단 맨 끝에 추가)
    df = add_answer_combine_column(df, input_col, order_col, product_col, start_col, end_col,
                                  answer_combine)

    # 시간 중복 오류 검사
    start_end_duplicate_errors = check_duplicate_times(df, panel_no, answer_combine)


    # 직전 응답과 시간 비교
    time_error_errors = compare_previous_response_and_time(
        df, panel_no, 
        derived_columns['input_month'], derived_columns['input_day'], 
        derived_columns['start_time'], derived_columns['end_time']
    )


    # 7단계: 오류 컬럼 추가 (함수 사용)
    update_status_display(6)
    progress.progress(75)

    # 오류 데이터 딕셔너리 준비
    error_data = {
        'order_errors': order_answer_errors,
        'day_order_errors': day_order_errors,
        'dup_errors': dup_errors,
        'count_errors': count_errors,
        'duplicate_time_errors': start_end_duplicate_errors,
        'time_error_errors': time_error_errors
    }

    # 오류 컬럼들 추가
    df = add_error_columns(df, error_data)

    # 8단계: 데이터 저장 준비
    update_status_display(7)
    progress.progress(85)
    raw_data = df

    raw_data_path = st.session_state.get("raw_data_path")
    curr_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
    origin_name = f'{file_name}_{curr_datetime}.xlsx'
    file_name = origin_name

    base_dir = set_path if set_path is not None else os.path.dirname(raw_data_path) if raw_data_path else os.getcwd()
    save_path = base_dir

    convert_data_path = st.session_state.get("convert_data_path")
    if (convert_data_path is None or convert_data_path == '') and set_path is None:
        save_path = os.path.join(base_dir, 'convert')
        st.session_state["convert_data_path"] = save_path
    else:
        save_path = convert_data_path

    if set_path is None and not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    if set_path is not None:
        save_path = set_path

    new_path = os.path.join(save_path, file_name)
    clean_data = raw_data.copy()

    # 9단계: 엑셀 스타일 적용
    update_status_display(8)
    progress.progress(95)

    # 엑셀 스타일 적용
    set_xl_layout(new_path, clean_data, error_columns, check_columns, columns_to_remove)

    # 10단계: 완료
    update_status_display(9)
    progress.progress(100)

    # 상태 텍스트를 최종 완료 상태로 업데이트
    final_display = "**Completed! 🎉**\n\n"
    for step in process_steps:
        final_display += f"~~{step}~~ ✅\n\n"
    status_text.markdown(final_display)

    # 잠시 후 상태 텍스트와 프로그레스 바 정리
    import time
    time.sleep(2)
    status_text.empty()
    progress.empty()

    st.session_state["raw_data"] = raw_data
    st.session_state["curr_file_name"] = origin_name
    st.session_state["base_directory"] = base_dir
    st.success(f"✅ {os.path.basename(file_name)}")
    if rerun:
        st.rerun()
