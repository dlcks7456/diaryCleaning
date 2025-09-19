import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import show_data_info
from features.setting import get_column_name, get_problem_columns, get_ui_color

def show_dashboard():
    """Dashboard 페이지를 표시합니다."""
    st.header('📊 Dashboard')

    # 데이터 정보 표시
    show_data_info()

    # 세션 상태에서 데이터 가져오기
    raw_data = st.session_state.get("raw_data")

    if raw_data is None:
        st.warning("먼저 데이터를 로드해주세요.")
        return

    df = raw_data.copy()

    # Columns
    panel_no = get_column_name('panel_no')
    area = get_column_name('area')
    age_5 = get_column_name('age_5')
    product_col = get_column_name('product_col')
    problem_columns = get_problem_columns()
    answer_date = get_column_name('answer_date')

    # 날짜별 응답 수 차트
    if answer_date in df.columns:
        df_date_only = pd.to_datetime(df[answer_date]).dt.date
        date_count = df_date_only.value_counts().sort_index()
        date_count.index = pd.to_datetime(date_count.index).strftime('%m월 %d일')

        fig = go.Figure(data=go.Bar(
            x=date_count.index,
            y=date_count.values,
            name='Response Count',
            marker_color=get_ui_color('chart_color')
        ))

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Response Count",
            xaxis=dict(tickangle=45),
            showlegend=False
        )

        st.plotly_chart(fig, width='stretch')
    else:
        st.error(f"**Cannot create date count bar chart. The following columns do not exist in the data: {answer_date}**")

    # AREA BY AGE_5 CROSSTABLE
    if age_5 in df.columns and area in df.columns:
        unique_df = df[[panel_no, age_5, area]].drop_duplicates()
        area_by_age_5_crosstable = pd.crosstab(unique_df[age_5], unique_df[area])
        area_by_age_5_crosstable.index.name = f"Total : {len(unique_df)}'s"
        st.dataframe(area_by_age_5_crosstable, width='stretch')
    else:
        missing_cols = []
        if age_5 not in df.columns:
            missing_cols.append(age_5)
        if area not in df.columns:
            missing_cols.append(area)
        st.error(f"**Cannot create crosstab. The following columns do not exist in the data: {', '.join(missing_cols)}**")

    # Q6 by Q3 crosstab
    existing_problem_columns = [col for col in problem_columns if col in df.columns]
    if existing_problem_columns and product_col in df.columns:
        crosstab_results = []

        for q6_col in existing_problem_columns:
            q6_by_q3_crosstab = pd.crosstab(df[q6_col], df[product_col], margins=False)
            q6_by_q3_crosstab.index = [idx for idx in q6_by_q3_crosstab.index]
            crosstab_results.append(q6_by_q3_crosstab)

        if crosstab_results:
            merged_crosstab = pd.concat(crosstab_results, axis=0)
            merged_crosstab.fillna(0, inplace=True)
            merged_crosstab.index.name = "Q6 By Q3"
            st.dataframe(merged_crosstab, width='stretch')
    elif not existing_problem_columns and product_col not in df.columns:
        st.error(f"**Cannot create Q6 by Q3 crosstab. Both Q6 columns and Q3 column ({product_col}) do not exist in the data.**")
    elif not existing_problem_columns:
        st.error(f"**Cannot create Q6 by Q3 crosstab. Q6 related columns do not exist in the data.**")
    elif product_col not in df.columns:
        st.error(f"**Cannot create Q6 by Q3 crosstab. Q3 column ({product_col}) does not exist in the data.**")
