"""
데이터 처리 관련 유틸리티 함수들
data_convert.py에서 사용되는 컬럼 생성 및 오류 검사 로직을 모듈화
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from features.setting import get_column_name, get_error_column, get_max_answers, get_product_list, get_duration_max



def split_date_columns(df, input_col):
    """
    입력 날짜 컬럼을 월/일로 분할하여 새로운 컬럼을 추가

    Args:
        df (DataFrame): 원본 데이터프레임
        input_col (str): 분할할 입력 컬럼명 (예: 'Q1')

    Returns:
        DataFrame: 월/일 컬럼이 추가된 데이터프레임
    """
    df_copy = df.copy()

    # 입력 컬럼의 위치 찾기
    q1_index = df_copy.columns.get_loc(input_col)

    # 날짜 데이터 분리 (예: "3|15" -> month=3, day=15)
    temp_df = df_copy[input_col].str.split('|', expand=True)
    temp_df.columns = [f'{input_col}_month', f'{input_col}_day']
    temp_df[f'{input_col}_month'] = temp_df[f'{input_col}_month'].astype(int)
    temp_df[f'{input_col}_day'] = temp_df[f'{input_col}_day'].astype(int)

    # 원본 컬럼 다음 위치에 새 컬럼들 삽입
    for i, col in enumerate([f'{input_col}_month', f'{input_col}_day']):
        df_copy.insert(q1_index + 1 + i, col, temp_df[col])

    return df_copy


def split_time_columns(df, time_cols):
    """
    시간 컬럼들을 시/분으로 분할하여 새로운 컬럼을 추가

    Args:
        df (DataFrame): 원본 데이터프레임
        time_cols (list): 분할할 시간 컬럼명 리스트 (예: ['Q4', 'Q5'])

    Returns:
        tuple: (수정된 데이터프레임, 시간 데이터 딕셔너리)
    """
    df_copy = df.copy()
    time_data = {}

    for v in time_cols:
        # 현재 변수의 인덱스 찾기
        v_index = df_copy.columns.get_loc(v)

        # 시간 데이터 분리 (예: "14|30" -> hour=14, min=30)
        temp_time = df_copy[v].str.split('|', expand=True)
        temp_time.columns = [f'{v}_hour', f'{v}_min']
        temp_time[f'{v}_hour'] = temp_time[f'{v}_hour'].astype(int)
        temp_time[f'{v}_min'] = temp_time[f'{v}_min'].astype(int)

        # 시간 객체 생성
        temp_time[f'{v}_time'] = temp_time[[f'{v}_hour', f'{v}_min']].apply(
            lambda x: f"{x[f'{v}_hour']}:{x[f'{v}_min']}", axis=1
        )
        temp_time[f'{v}_time'] = pd.to_datetime(temp_time[f'{v}_time'], format='%H:%M').dt.time

        # 기준 변수 다음에 hour, min 컬럼만 삽입
        for i, col in enumerate([f'{v}_hour', f'{v}_min']):
            df_copy.insert(v_index + 1 + i, col, temp_time[col])

        # time 데이터 저장
        time_data[f'{v}_time'] = temp_time[f'{v}_time']

    return df_copy, time_data


def calculate_duration(start_time, end_time):
    """
    시작 시간과 종료 시간 사이의 지속시간을 분 단위로 계산

    Args:
        start_time (time): 시작 시간 객체
        end_time (time): 종료 시간 객체

    Returns:
        int: 지속시간 (분 단위)
    """
    # time 객체에서 시간과 분 추출
    start_hour = start_time.hour
    start_min = start_time.minute
    end_hour = end_time.hour
    end_min = end_time.minute

    # 시간을 분 단위로 변환
    start_total_min = start_hour * 60 + start_min
    end_total_min = end_hour * 60 + end_min

    # 만약 시작 시간이 종료 시간보다 늦다면 (자정을 넘긴 경우)
    if start_total_min > end_total_min:
        end_total_min += 24 * 60  # 하루(1440분) 추가

    # 시간 차이 계산 (분 단위)
    duration = end_total_min - start_total_min
    return duration


def add_duration_column(df, time_data, start_col, end_col, total_duration_col, end_min_col):
    """
    총 지속시간 컬럼을 데이터프레임에 추가

    Args:
        df (DataFrame): 원본 데이터프레임
        time_data (dict): 시간 데이터 딕셔너리
        start_col (str): 시작 시간 컬럼명
        end_col (str): 종료 시간 컬럼명
        total_duration_col (str): 총 지속시간 컬럼명
        end_min_col (str): 종료 시간 분 컬럼명

    Returns:
        DataFrame: 지속시간 컬럼이 추가된 데이터프레임
    """
    df_copy = df.copy()

    start_time = f'{start_col}_time'
    end_time = f'{end_col}_time'

    # 각 행에 대해 시간 차이 계산
    total_duration_list = []
    for idx in df_copy.index:
        start_time_row = time_data[start_time].iloc[idx]
        end_time_row = time_data[end_time].iloc[idx]
        duration = calculate_duration(start_time_row, end_time_row)
        total_duration_list.append(duration)

    total_duration_data = pd.Series(total_duration_list, index=df_copy.index)

    # 지정된 위치에 컬럼들 삽입
    end_min_index = df_copy.columns.get_loc(end_min_col)
    df_copy.insert(end_min_index + 1, start_time, time_data[start_time])
    df_copy.insert(end_min_index + 2, end_time, time_data[end_time])
    df_copy.insert(end_min_index + 3, total_duration_col, total_duration_data)

    return df_copy


def check_order_errors(df, panel_no, order_col, input_col):
    """
    순서 오류를 검사하는 함수

    Args:
        df (DataFrame): 검사할 데이터프레임
        panel_no (str): 패널 번호 컬럼명
        order_col (str): 순서 컬럼명
        input_col (str): 입력 컬럼명

    Returns:
        tuple: (Q2 순서 오류 인덱스 리스트, Q1_day 순서 오류 인덱스 리스트, 중복 오류 인덱스 리스트)
    """
    order_answer_errors = []  # Q2 순차 입력 오류
    day_order_errors = []     # Q1_day 순차 입력 오류
    dup_errors = []           # Q2 중복 오류

    # 임시 날짜 결합 컬럼 생성
    df_temp = df.copy()
    df_temp['date_merge'] = df_temp.apply(lambda x: f'{x[f"{input_col}_month"]}/{x[f"{input_col}_day"]}', axis=1)

    unique_panels = df_temp[panel_no].unique().tolist()

    for pn in unique_panels:
        # 해당 패널의 고유 날짜 목록 추출
        unique_date = df_temp[df_temp[panel_no] == pn]['date_merge'].unique().tolist()

        for date in unique_date:
            # 특정 패널과 날짜로 필터링
            filt_df = df_temp[(df_temp[panel_no] == pn) & (df_temp['date_merge'] == date)]

            # Q2 기준으로 정렬
            sort_df = filt_df.sort_values([order_col])
            chk_df = sort_df[[f'{input_col}_month', f'{input_col}_day', order_col]]

            # Q2 중복 체크 - 같은 패널, 같은 날짜에서 Q2 값이 중복되는 경우
            q2_counts = filt_df[order_col].value_counts()
            duplicated_q2 = q2_counts[q2_counts > 1].index.tolist()
            for dup_q2 in duplicated_q2:
                dup_indices = filt_df[filt_df[order_col] == dup_q2].index.tolist()
                dup_errors.extend(dup_indices)

            chk_index = chk_df.index.tolist()

            # 순차적 입력 오류 체크
            for idx, r in enumerate(chk_index):
                if idx == 0:
                    continue

                # 현재 행의 Q2, Q1_day 값
                curr_q2 = chk_df.loc[r, order_col]

                # 이전 행의 인덱스와 값들
                prev_idx = chk_index[idx-1]
                prev_q2 = chk_df.loc[prev_idx, order_col]

                # Q2 순차 입력 체크 - 이전 값 + 1이 아닌 경우 오류
                if prev_q2 != curr_q2 - 1:
                    order_answer_errors.append(prev_idx)
                    order_answer_errors.append(r)

        # 각 패널별로 전체 데이터에서 Q1_day 순차 입력 체크 (입력된 시간 순서대로)
        panel_df = df_temp[df_temp[panel_no] == pn].copy()
        panel_indices = panel_df.index.tolist()

        for idx in range(1, len(panel_indices)):
            curr_idx = panel_indices[idx]
            prev_idx = panel_indices[idx-1]

            curr_day = panel_df.loc[curr_idx, f'{input_col}_day']
            prev_day = panel_df.loc[prev_idx, f'{input_col}_day']

            # 현재 day가 이전 day보다 작은 경우 (역순으로 입력된 경우) 오류
            if curr_day < prev_day:
                day_order_errors.append(prev_idx)
                day_order_errors.append(curr_idx)

    return order_answer_errors, day_order_errors, dup_errors


def check_count_errors(df, panel_no, product_col, index_col):
    """
    제품 응답 수 초과 오류를 검사하는 함수

    Args:
        df (DataFrame): 검사할 데이터프레임
        panel_no (str): 패널 번호 컬럼명
        product_col (str): 제품 컬럼명
        index_col (str): 인덱스 컬럼명

    Returns:
        list: 응답 수 초과 오류 인덱스 리스트
    """
    count_errors = []
    unique_panels = df[panel_no].unique().tolist()
    product_list = get_product_list()
    max_answers = get_max_answers()

    for pn in unique_panels:
        # 제품 응답 수 초과 오류 체크
        for product in product_list:
            count_filt = df[(df[panel_no] == pn) & (df[product_col] == product)][[index_col, product_col]]
            product_answer_count = len(count_filt)
            if product_answer_count > max_answers:
                diff_count = product_answer_count - max_answers
                count_errors.extend(count_filt.index.to_list()[-diff_count:])

    return count_errors


def create_answer_combine(row, input_col, order_col, product_col, start_col, end_col):
    """
    응답 데이터를 결합하여 표시용 문자열을 생성

    Args:
        row (Series): 데이터프레임의 행
        input_col (str): 입력 컬럼명
        order_col (str): 순서 컬럼명
        product_col (str): 제품 컬럼명
        start_col (str): 시작 시간 컬럼명
        end_col (str): 종료 시간 컬럼명

    Returns:
        str: 결합된 응답 문자열
    """
    def digit_2(num):
        return '{0:02d}'.format(num)

    # 입력 날짜
    month = digit_2(row[f'{input_col}_month'])
    day = digit_2(row[f'{input_col}_day'])

    # 순번
    order = digit_2(row[order_col])

    # 제품
    product = row[product_col]

    # 시작 시간
    start_hour = digit_2(row[f'{start_col}_hour'])
    start_min = digit_2(row[f'{start_col}_min'])

    # 종료 시간
    end_hour = digit_2(row[f'{end_col}_hour'])
    end_min = digit_2(row[f'{end_col}_min'])

    return f'[{month}/{day}] {product}-{order} ({start_hour}:{start_min}~{end_hour}:{end_min})'


def check_duplicate_times(df, panel_no, answer_combine_col):
    """
    시작/종료 시간 중복을 검사하는 함수

    Args:
        df (DataFrame): 검사할 데이터프레임
        panel_no (str): 패널 번호 컬럼명
        answer_combine_col (str): 결합된 응답 컬럼명

    Returns:
        list: 시간 중복 오류 인덱스 리스트
    """
    start_end_duplicate_errors = []
    unique_panels = df[panel_no].unique().tolist()

    for pn in unique_panels:
        # 시작 / 종료 시간 직전 데이터와 동일한 지 체크
        filt_by_pn = df[df[panel_no] == pn]

        # 중복 시간 체크
        panel_start_end_duplicate = filt_by_pn[
            filt_by_pn[answer_combine_col].duplicated(keep=False)
        ].index.tolist()

        start_end_duplicate_errors.extend(panel_start_end_duplicate)

    return start_end_duplicate_errors


def compare_previous_response_and_time(df, panel_no, input_month, input_day, start_time, end_time):
    """
    직전 응답과 시간 비교
    """
    df_copy = df.copy()
    unique_panels = df_copy[panel_no].unique().tolist()
    time_error_errors = []

    for pn in unique_panels:
        panel_df = df_copy[df_copy[panel_no] == pn]

        # 각 패널 내에서 월/일별로 그룹화
        unique_dates = panel_df.groupby([input_month, input_day]).groups

        for (month, day), date_indices in unique_dates.items():
            # 동일한 월/일 데이터만 필터링
            date_df = panel_df.loc[date_indices].sort_index()
            date_indices_list = date_df.index.tolist()

            # 같은 날짜 내에서 시간 순서 검증
            for idx in range(1, len(date_indices_list)):
                curr_idx = date_indices_list[idx]
                prev_idx = date_indices_list[idx-1]
                curr_start_time = date_df.loc[curr_idx, start_time]
                prev_end_time = date_df.loc[prev_idx, end_time]
                if curr_start_time < prev_end_time:
                    time_error_errors.append(curr_idx)
    return time_error_errors


def add_error_columns(df, error_data):
    """
    오류 검사 결과를 기반으로 오류 컬럼들을 데이터프레임에 추가

    Args:
        df (DataFrame): 원본 데이터프레임
        error_data (dict): 오류 데이터 딕셔너리

    Returns:
        DataFrame: 오류 컬럼들이 추가된 데이터프레임
    """
    df_copy = df.copy()

    # 컬럼명 가져오기
    start_time = get_column_name('start_time')
    end_time = get_column_name('end_time')
    order_col = get_column_name('order_col')
    input_col = get_column_name('input_col')
    product_col = get_column_name('product_col')
    total_duration = get_error_column('total_duration')
    answer_combine = get_error_column('answer_combine')

    order_error = get_error_column('order_error')
    duplicate_error = get_error_column('duplicate_error')
    day_order_error = get_error_column('day_order_error')
    answer_count_error = get_error_column('answer_count_error')
    start_end_duplicate = get_error_column('start_end_duplicate')
    duration_error = get_error_column('duration_error')
    duration_max = get_duration_max()
    time_error = get_error_column('time_error')

    # 오류 시리즈 생성
    order_error_series = df_copy.index.isin(error_data['order_errors'])
    day_order_error_series = df_copy.index.isin(error_data['day_order_errors'])
    dup_error_series = df_copy.index.isin(error_data['dup_errors'])
    answer_count_error_series = df_copy.index.isin(error_data['count_errors'])
    start_end_duplicate_error_series = df_copy.index.isin(error_data['duplicate_time_errors'])
    duration_error_series = df_copy[total_duration] > duration_max
    time_error_series = df_copy.index.isin(error_data['time_error_errors'])
    # 컬럼 삽입
    # Q2 컬럼 다음에 ORDER_ERROR와 DUP_ERROR 삽입
    q2_index = df_copy.columns.get_loc(order_col)
    df_copy.insert(q2_index + 1, order_error, order_error_series)
    df_copy.insert(q2_index + 2, duplicate_error, dup_error_series)

    # Q1_day 컬럼 다음에 DAY_ORDER_ERROR 삽입
    q1_day_index = df_copy.columns.get_loc(f'{input_col}_day')
    df_copy.insert(q1_day_index + 1, day_order_error, day_order_error_series)

    # Q3 컬럼 다음에 ANSWER_COUNT_ERROR 삽입
    q3_index = df_copy.columns.get_loc(product_col)
    df_copy.insert(q3_index + 1, answer_count_error, answer_count_error_series)
    # total_duration 컬럼 앞에 time_error, start_end_duplicate 순으로 삽입
    total_duration_index = df_copy.columns.get_loc(total_duration)
    df_copy.insert(total_duration_index, time_error, time_error_series)
    df_copy.insert(total_duration_index + 1, start_end_duplicate, start_end_duplicate_error_series)

    # answer_combine 컬럼을 start_end_duplicate 컬럼 다음으로 이동 (이미 존재하는 경우)
    if answer_combine in df_copy.columns:
        answer_combine_data = df_copy[answer_combine]
        df_copy = df_copy.drop(answer_combine, axis=1)
        start_end_duplicate_index = df_copy.columns.get_loc(start_end_duplicate)
        df_copy.insert(start_end_duplicate_index + 1, answer_combine, answer_combine_data)


    # total_duration 컬럼 다음에 duration_error 삽입
    df_copy.insert(df_copy.columns.get_loc(total_duration) + 1, duration_error, duration_error_series)


    return df_copy


def add_answer_combine_column(df, input_col, order_col, product_col, start_col, end_col, answer_combine_col, insert_after_col=None):
    """
    응답 결합 컬럼을 데이터프레임에 추가

    Args:
        df (DataFrame): 원본 데이터프레임
        input_col (str): 입력 컬럼명
        order_col (str): 순서 컬럼명
        product_col (str): 제품 컬럼명
        start_col (str): 시작 시간 컬럼명
        end_col (str): 종료 시간 컬럼명
        answer_combine_col (str): 응답 결합 컬럼명
        insert_after_col (str, optional): 이 컬럼 다음에 삽입할 컬럼명. None이면 맨 끝에 추가

    Returns:
        DataFrame: 응답 결합 컬럼이 추가된 데이터프레임
    """
    df_copy = df.copy()

    # 응답 결합 컬럼 생성
    df_copy[answer_combine_col] = df_copy.apply(
        lambda row: create_answer_combine(row, input_col, order_col, product_col, start_col, end_col),
        axis=1
    )

    # 특정 컬럼 다음으로 이동 (해당 컬럼이 존재하는 경우에만)
    if insert_after_col and insert_after_col in df_copy.columns:
        answer_combine_data = df_copy[answer_combine_col]
        df_copy = df_copy.drop(answer_combine_col, axis=1)
        insert_after_index = df_copy.columns.get_loc(insert_after_col)
        df_copy.insert(insert_after_index + 1, answer_combine_col, answer_combine_data)

    return df_copy
