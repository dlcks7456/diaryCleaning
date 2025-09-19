"""
data_processing.py 모듈의 함수들을 다른 곳에서 사용하는 예제

이 파일은 새로 생성한 데이터 처리 함수들을
다른 파일에서 어떻게 재사용할 수 있는지 보여주는 예제입니다.
"""

import pandas as pd
from utils.data_processing import (
    split_date_columns, split_time_columns, add_duration_column,
    check_order_errors, check_count_errors, check_duplicate_times,
    add_error_columns, add_answer_combine_column, create_answer_combine,
    calculate_duration
)
from datetime import datetime


def example_usage():
    """
    데이터 처리 함수들의 사용 예제
    """
    # 예제 데이터 생성
    sample_data = {
        'ID': [1, 2, 3, 4, 5],
        'PANEL_NO': ['P001', 'P001', 'P001', 'P002', 'P002'],
        'Q1': ['3|15', '3|16', '3|17', '3|15', '3|16'],
        'Q2': [1, 2, 3, 1, 2],
        'Q3': ['A', 'B', 'A', 'C', 'A'],
        'Q4': ['14|30', '15|45', '16|20', '09|15', '10|30'],
        'Q5': ['15|00', '16|15', '17|00', '10|00', '11|15']
    }

    df = pd.DataFrame(sample_data)
    print("원본 데이터:")
    print(df)
    print("\n" + "="*50 + "\n")

    # 1. 날짜 컬럼 분할
    print("1. 날짜 컬럼 분할:")
    df_with_dates = split_date_columns(df, 'Q1')
    print(df_with_dates[['Q1', 'Q1_month', 'Q1_day']])
    print("\n" + "-"*30 + "\n")

    # 2. 시간 컬럼 분할
    print("2. 시간 컬럼 분할:")
    df_with_times, time_data = split_time_columns(df_with_dates, ['Q4', 'Q5'])
    print(df_with_times[['Q4', 'Q4_hour', 'Q4_min', 'Q5', 'Q5_hour', 'Q5_min']])
    print("\n시간 데이터:")
    for key, value in time_data.items():
        print(f"{key}: {value.tolist()}")
    print("\n" + "-"*30 + "\n")

    # 3. 지속시간 계산
    print("3. 지속시간 계산:")
    df_with_duration = add_duration_column(df_with_times, time_data, 'Q4', 'Q5', 'TOTAL_DURATION', 'Q5_min')
    print(df_with_duration[['Q4_time', 'Q5_time', 'TOTAL_DURATION']])
    print("\n" + "-"*30 + "\n")

    # 4. 개별 시간 차이 계산 예제
    print("4. 개별 시간 차이 계산:")
    start_time = datetime.strptime("14:30", "%H:%M").time()
    end_time = datetime.strptime("15:00", "%H:%M").time()
    duration = calculate_duration(start_time, end_time)
    print(f"14:30에서 15:00까지 지속시간: {duration}분")
    print("\n" + "-"*30 + "\n")

    # 5. 응답 결합 문자열 생성 예제
    print("5. 응답 결합 문자열 생성:")
    sample_row = df_with_duration.iloc[0]
    combined_answer = create_answer_combine(sample_row, 'Q1', 'Q2', 'Q3', 'Q4', 'Q5')
    print(f"결합된 응답: {combined_answer}")

    return df_with_duration


def standalone_error_check_example():
    """
    오류 검사 함수들을 독립적으로 사용하는 예제
    """
    print("\n" + "="*50)
    print("독립적인 오류 검사 예제")
    print("="*50 + "\n")

    # 오류가 있는 예제 데이터
    error_data = {
        'ID': [1, 2, 3, 4, 5, 6],
        'PANEL_NO': ['P001', 'P001', 'P001', 'P001', 'P002', 'P002'],
        'Q1_month': [3, 3, 3, 3, 3, 3],
        'Q1_day': [15, 16, 14, 17, 15, 16],  # 3번째가 역순
        'Q2': [1, 2, 2, 4, 1, 2],  # 2번과 3번이 중복, 4번이 순서 오류
        'Q3': ['A', 'A', 'A', 'A', 'B', 'B'],  # P001에 A가 4개 (초과)
    }

    df_error = pd.DataFrame(error_data)
    print("오류 테스트 데이터:")
    print(df_error)
    print("\n")

    # 순서 오류 검사
    order_errors, day_errors, dup_errors = check_order_errors(df_error, 'PANEL_NO', 'Q2', 'Q1')

    print("검사 결과:")
    print(f"Q2 순서 오류 인덱스: {order_errors}")
    print(f"Q1_day 순서 오류 인덱스: {day_errors}")
    print(f"Q2 중복 오류 인덱스: {dup_errors}")

    # 응답 수 초과 오류는 실제 설정값이 필요하므로 스킵

    return df_error


if __name__ == "__main__":
    print("데이터 처리 함수 사용 예제\n")

    # 기본 사용 예제
    result_df = example_usage()

    # 오류 검사 예제
    error_df = standalone_error_check_example()

    print("\n" + "="*50)
    print("모든 예제가 완료되었습니다!")
    print("이제 이 함수들을 다른 파일에서 import하여 사용할 수 있습니다.")
    print("="*50)
