import streamlit as st
import pandas as pd
from utils.data_loader import show_data_info
from utils.record_log import record_log
from datetime import datetime
from utils.column_manager import (
    get_column_manager,
    get_log_column_names
)
from features.setting import get_product_list, get_max_answers, get_duration_max
from utils.data_convert import convert_data

def show_error_check():
    """
    Error Check 페이지를 표시합니다.
    
    이 함수는 데이터의 오류를 검사하고 수정할 수 있는 인터페이스를 제공합니다.
    다양한 오류 유형별로 필터링하고 수정할 수 있습니다.
    """
    st.header('🔍 Error Check')

    # 세션 상태에서 데이터 가져오기
    raw_data = st.session_state.get("raw_data")

    if raw_data is None:
        st.warning("먼저 데이터를 로드해주세요.")
        return

    df = raw_data.copy()

    # 컬럼 매니저를 통해 모든 컬럼명을 한 번에 가져옴
    column_manager = get_column_manager()
    
    # 개별 컬럼명들 가져오기
    index_col = column_manager.get_column('index_col')
    unique_id = column_manager.get_column('unique_id')
    panel_no = column_manager.get_column('panel_no')
    input_col = column_manager.get_column('input_col')  # Q1
    order_col = column_manager.get_column('order_col')  # Q2
    product_col = column_manager.get_column('product_col')  # Q3
    start_col = column_manager.get_column('start_col')  # Q4
    end_col = column_manager.get_column('end_col')  # Q5
    
    # 에러 컬럼명들 가져오기
    order_error = column_manager.get_error_column('order_error')
    duplicate_error = column_manager.get_error_column('duplicate_error')
    day_order_error = column_manager.get_error_column('day_order_error')
    answer_count_error = column_manager.get_error_column('answer_count_error')
    start_end_duplicate = column_manager.get_error_column('start_end_duplicate')
    total_duration = column_manager.get_error_column('total_duration')
    time_error = column_manager.get_error_column('time_error')
    answer_combine = column_manager.get_error_column('answer_combine')
    duration_error = column_manager.get_error_column('duration_error')

    # 설정값들 가져오기
    product_list = get_product_list()
    duration_max = get_duration_max()
    max_answers = get_max_answers()

    error_structure = {
        "1. 중복 응답": {
            "col": start_end_duplicate,
            "cond": df[start_end_duplicate]==True,
            "check_col": "**응답 모두 확인**"
        },
        "2. 응답 수 초과": {
            "col": answer_count_error,
            "cond": df[answer_count_error]==True,
            "check_col": f"제품당 사용 수 초과(최대 {max_answers}개 가능) : **{product_col} 확인**"
        },
        "3. 중복 순번 확인": {
            "col": duplicate_error,
            "cond": df[duplicate_error]==True,
            "check_col": f"착용 순서 중복 오류 : **{input_col}/{order_col} 확인**"
        },
        "4. 제품 순서 응답 확인": {
            "col": order_error,
            "cond": df[order_error]==True,
            "check_col": f"제품 순서 오류 : **{input_col}/{order_col} 확인**"
        },
        "5. 직전 응답 시간 확인": {
            "col": time_error,
            "cond": df[time_error]==True,
            "check_col": f"직전 응답 시간 오류 : **{input_col}/{start_col}/{end_col} 확인**"
        },
        "6. 날짜 순서 응답 확인": {
            "col": day_order_error,
            "cond": df[day_order_error]==True,
            "check_col": f"날짜 순서 오류 : **{input_col} 확인**"
        },
        "7. 착용 시간 확인": {
            "col": duration_error,
            "cond": df[duration_error]==True,
            "check_col": f"착용 시간 초과(최대 {duration_max}분 이상 리체크) : **{start_col}/{end_col} 확인**"
        }
    }

    select_error_type = st.selectbox("📌 **오류 유형 선택**", error_structure.keys(), index=0, width=300)
    error_condition = error_structure[select_error_type]["cond"]
    error_col = error_structure[select_error_type]["col"]
    error_check_col = error_structure[select_error_type]["check_col"]
    has_error_panels = df[error_condition][panel_no].unique().tolist()

    if has_error_panels :
        st.caption(f"⚠️ [{select_error_type}] 해당 응답자 수 : {len(has_error_panels)}'s\n\n⚒️{error_check_col}")

        filt_col1, filt_col2, filt_col3, filt_col4 = st.columns([1, 1, 2, 2])
        with filt_col1 :
            error_panel = st.selectbox("응답자 선택", has_error_panels, index=None)
        with filt_col2 :
            error_products = df[(df[panel_no]==error_panel) & (error_condition)][product_col].unique().tolist()
            product_filt = st.selectbox("에러 제품 필터", error_products, index=None)

        with filt_col3 :
            if error_panel :
                # 데이터 필터링 조건 설정
                condition = (df[panel_no]==error_panel) & (error_condition) if select_error_type in ["중복 응답", "순서 오류"] else (df[panel_no]==error_panel)
                count_dict = df[condition][product_col].value_counts().to_dict()

                # 결과 표시
                if count_dict:
                    answer_count_list = ''
                    for product, count in count_dict.items():
                        answer_count_list += f"- {product} : {count}'s\n"
                    st.caption(answer_count_list)
                else:
                    st.caption("제품 응답이 없습니다.")

        if st.session_state.get('data_edited', False) == True :
            st.warning("⚠️ 데이터 수정 후 저장 버튼 클릭 및 Re-Convert로 다시 에러 체크 진행")

        if error_panel is not None :
            # 필요한 컬럼들이 데이터프레임에 존재하는지 확인
            error_check_columns = [error_col, unique_id, panel_no, answer_combine, input_col, order_col, product_col, start_col, end_col, total_duration]
            existing_columns = [col for col in error_check_columns if col in df.columns and col is not None and col != '']

            if product_filt :
                error_df = df[(df[panel_no]==error_panel) & (df[product_col]==product_filt)][existing_columns]
            else :
                error_df = df[df[panel_no]==error_panel][existing_columns]

            delete_col = 'delete_sample'
            error_df[delete_col] = False

            # 다양한 컬럼 구성 예시
            column_config = {
                error_col : st.column_config.CheckboxColumn(
                    "🔒 에러",
                    help=f"{select_error_type} 여부",
                    width="small",
                    disabled=True,
                ) if error_col in existing_columns else None,
                unique_id: None,
                panel_no: st.column_config.NumberColumn(
                    "🔒 패널 번호",
                    help="응답자의 고유 식별번호",
                    width="small",
                    disabled=True
                ) if panel_no in existing_columns else None,
                answer_combine: st.column_config.TextColumn(
                    "🔒 응답 요약",
                    help="Q1-Q5 응답 결합값",
                    width="medium",
                    disabled=True,
                ) if answer_combine in existing_columns else None,
                input_col: st.column_config.TextColumn(
                    "Q1: 입력 날짜",
                    help="입력 날짜: MM|DD",
                    width="small",
                    validate=r"^(0?[1-9]|1[0-2])\|(0?[1-9]|[12][0-9]|3[01])$",
                ) if input_col in existing_columns else None,
                order_col: st.column_config.NumberColumn(
                    "Q2: 입력 순서",
                    help="입력 순서",
                    width="small",
                    min_value=1,
                    max_value=max_answers,
                    step=1,
                    format="%d"
                ) if order_col in existing_columns else None,
                product_col: st.column_config.SelectboxColumn(
                    "Q3: 사용 제품",
                    help="사용 제품",
                    width="small",
                    options=product_list if product_list else None
                ) if product_col in existing_columns else None,
                start_col: st.column_config.TextColumn(
                    "Q4: 시작 시간",
                    help="착용 시작 시간: HH|MM",
                    width="small",
                    validate=r"^(0?[0-9]|1[0-9]|2[0-3])\|([0-5]?[0-9])$",
                ) if start_col in existing_columns else None,
                end_col: st.column_config.TextColumn(
                    "Q5: 종료 시간",
                    help="착용 종료 시간: HH|MM",
                    width="small",
                    validate=r"^(0?[0-9]|1[0-9]|2[0-3])\|([0-5]?[0-9])$",
                ) if end_col in existing_columns else None,
                total_duration: st.column_config.NumberColumn(
                    "🔒 총 착용 시간(분)",
                    help="총 착용 시간(분)",
                    width="small",
                    min_value=1,
                    step=1,
                    disabled=True,
                    format="%d분",
                ) if (select_error_type == "7. 착용 시간 확인" and total_duration in existing_columns) else None,
                delete_col : st.column_config.CheckboxColumn(
                    "⚠️ 삭제 여부",
                    help="삭제가 필요한 샘플은 체크합니다.",
                    width="small",
                )
            }


            with st.form(key="duplicate_editor"):
                data_editor = st.data_editor(
                    error_df,
                    width='stretch',
                    column_config=column_config,
                    hide_index=True,
                    num_rows="fixed",
                    # on_change 파라미터는 지원하지 않으므로 제거
                )
                # 데이터가 수정되었는지 확인 (수정 감지는 직접 비교 필요)
                if not st.session_state.get('original_error_df') is None:
                    if not data_editor.equals(st.session_state['original_error_df']):
                        st.session_state['data_edited'] = True
                else:
                    st.session_state['original_error_df'] = error_df.copy()

                save_btn = st.form_submit_button("💾 저장", width='stretch')

                if save_btn:
                    st.session_state['updated_data'] = True
                    try:
                        # 삭제 체크된 행들 처리
                        rows_to_delete = data_editor[data_editor[delete_col] == True].index.tolist()

                        # 그 다음 삭제 체크된 행들 처리
                        log_columns = get_log_column_names()
                        log_columns = [col for col in log_columns if col in df.columns and col is not None and col != '']
                        curr_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                        modified_count = 0  # 수정된 데이터 개수 추적

                        # 먼저 삭제 체크되지 않은 행들의 수정사항을 반영
                        for idx, row in data_editor.iterrows():
                            if not row[delete_col]:  # 삭제 체크되지 않은 행만 업데이트
                                raw_data_row = st.session_state['raw_data'].loc[idx]
                                modify_row = {col: raw_data_row[col] for col in log_columns}
                                has_changes = False

                                check_columns = [col for col in [input_col, order_col, product_col, start_col, end_col]
                                               if col in data_editor.columns and col is not None and col != '']

                                for chk in check_columns:
                                    if row[chk] != st.session_state['raw_data'].loc[idx, chk] :
                                        modify_row[chk] = f'{raw_data_row[chk]} > {row[chk]}'
                                        has_changes = True
                                    st.session_state['raw_data'].loc[idx, chk] = row[chk]

                                # 변경사항이 있는 경우에만 로그 기록
                                if has_changes:
                                    modify_df = pd.DataFrame([modify_row])
                                    record_log(modify_df, curr_time, 'MODIFY', select_error_type)
                                    modified_count += 1

                        # 수정된 데이터 개수 확인
                        if modified_count > 0:
                            st.warning(f"⚠️ {modified_count}개 데이터 수정")

                        if rows_to_delete:
                            st.session_state['raw_data'] = st.session_state['raw_data'].drop(rows_to_delete).reset_index(drop=True)
                            delete_log = data_editor[data_editor[delete_col] == True][log_columns]
                            record_log(delete_log, curr_time, 'DELETE', select_error_type)
                            st.warning(f"⚠️ {len(rows_to_delete)}개 데이터 삭제")

                        st.session_state['show_save_btn'] = True
                        st.success("✅ 저장 완료")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ 저장 중 오류가 발생했습니다: {str(e)}")

        if st.session_state.get('show_save_btn', False) == True:
            st.session_state['data_edited'] = False
            re_convert_btn = st.button("🚀 Re-Convert", width='stretch', type='primary')
            if re_convert_btn:
                st.session_state['show_save_btn'] = False
                convert_data()
                st.rerun()

    else :
        st.success(f"**[{select_error_type}]** 에러 케이스가 없습니다.")