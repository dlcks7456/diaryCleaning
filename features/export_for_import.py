import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.column_manager import (
    get_column_manager, 
    get_required_export_columns,
    get_derived_column_names
)

def show_export_for_import():
    """
    Export for Import 페이지를 표시합니다.
    
    이 함수는 데이터를 다른 시스템으로 가져오기 위한 형태로
    변환하여 내보내는 기능을 제공합니다.
    """
    st.header("📤 Export for Import")
    
    # 컬럼 매니저를 통해 모든 컬럼명을 한 번에 가져옴
    column_manager = get_column_manager()
    
    # 파생 컬럼명들 가져오기
    derived_columns = get_derived_column_names()
    

    raw_data = st.session_state.get("raw_data")
    base_dir = st.session_state.get("base_directory")
    
    if raw_data is not None and base_dir is not None:
        # 필수 포함 컬럼 - 컬럼 매니저에서 가져옴
        required_columns = get_required_export_columns()
        columns = raw_data.columns

        select_columns = st.multiselect("**Include Columns**", columns, default=required_columns, width=500)

        if select_columns :
            import_path = os.path.join(base_dir, "import")
            if not os.path.exists(import_path):
                os.makedirs(import_path, exist_ok=True)

            save_path = st.text_input("Save Path", value=import_path, disabled=True, width=500)
            import_btn = st.button("Export for Import", width=500)
            
            if import_btn :
                curr_datetime = datetime.now().strftime('%Y%m%d')
                with st.spinner('Data Exporting...'):
                    raw_data[select_columns].to_excel(os.path.join(save_path, f'import_data_{curr_datetime}.xlsx'), index=False, sheet_name='Raw Data')
                    st.success('Data Exported', icon='✅')

            preview = st.expander("Preview", expanded=False)
            with preview :
                st.dataframe(raw_data[select_columns], hide_index=True)

    else :
        st.warning("먼저 데이터를 로드해주세요.")