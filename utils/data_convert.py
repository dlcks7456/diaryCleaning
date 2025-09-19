import pandas as pd
import numpy as np
import streamlit as st
import openpyxl as xl
import os
import re
from datetime import datetime, timedelta
from features.setting import get_column_name, get_error_column, get_max_answers, get_product_list, get_duration_max
from utils.xl_layout import set_xl_layout
from utils.data_processing import (
    split_date_columns, split_time_columns, add_duration_column,
    check_order_errors, check_count_errors, check_duplicate_times,
    add_error_columns, add_answer_combine_column, compare_previous_response_and_time
)

def convert_data() :
    raw_data = st.session_state.get("raw_data")
    if raw_data is None:
        st.warning("먼저 데이터를 로드해주세요.")
        return

    max_answers = get_max_answers()

    df = raw_data.copy()

    # 설정에서 컬럼명 가져오기
    product_list = get_product_list()
    index_col = get_column_name('index_col')
    panel_no = get_column_name('panel_no')
    product_col = get_column_name('product_col')
    order_col = get_column_name('order_col')
    input_col = get_column_name('input_col')
    start_col = get_column_name('start_col')
    end_col = get_column_name('end_col')
    order_error = get_error_column('order_error')
    duplicate_error = get_error_column('duplicate_error')
    day_order_error = get_error_column('day_order_error')
    answer_count_error = get_error_column('answer_count_error')
    start_end_duplicate = get_error_column('start_end_duplicate')
    total_duration = get_error_column('total_duration')
    time_error = get_error_column('time_error')

    answer_combine = get_error_column('answer_combine')

    duration_error = get_error_column('duration_error')
    duration_max = get_duration_max()

    error_columns = [order_error, duplicate_error, day_order_error, answer_count_error, start_end_duplicate, time_error]
    check_columns = [duration_error]
    # 기존에 추가된 컬럼들이 있는지 확인하고 삭제
    start_time = f'{start_col}_time'
    end_time = f'{end_col}_time'
    input_month = f'{input_col}_month'
    input_day = f'{input_col}_day'

    columns_to_remove = [
        input_month, input_day,
        f'{start_col}_hour', f'{start_col}_min', start_time,
        f'{end_col}_hour', f'{end_col}_min', end_time,
        total_duration,
        *error_columns,
        *check_columns,
        answer_combine,
    ]

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
    df = add_duration_column(df, time_data, start_col, end_col, total_duration, f'{end_col}_min')

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
    time_error_errors = compare_previous_response_and_time(df, panel_no, input_month, input_day, start_time, end_time)


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
    st.session_state["raw_data"] = raw_data

    raw_data_path = st.session_state.get("raw_data_path")
    curr_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f'converted_data_{curr_datetime}.xlsx'

    base_dir = os.path.dirname(raw_data_path) if raw_data_path else os.getcwd()
    save_path = base_dir

    convert_data_path = st.session_state.get("convert_data_path")
    if convert_data_path is None or convert_data_path == '':
        save_path = os.path.join(base_dir, 'convert')
        st.session_state["convert_data_path"] = save_path
    else:
        save_path = convert_data_path

    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    new_path = os.path.join(save_path, file_name)
    clean_data = raw_data.copy()

    # st.session_state["raw_data_path"] = new_path

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

    st.success(f"✅ {os.path.basename(file_name)}")
