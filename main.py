import streamlit as st
import pandas as pd
from features.error_check import show_error_check
from features.dashboard import show_dashboard
from features.setting import show_settings, get_session_variables, get_default_page, get_preview_rows, get_save_path_manager
from utils.data_loader import show_data_upload_sidebar, show_data_info, validate_session_file_path

# 페이지 설정
st.set_page_config(
    page_title="Data Cleaning",
    page_icon="📊",
    layout="wide"
)

# CSS 파일 로드 함수
def load_css(file_path):
    """CSS 파일을 로드하여 Streamlit에 적용합니다."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS 파일을 찾을 수 없습니다: {file_path}")

# 커스텀 CSS 스타일 적용
load_css("styles/main.css")

st.title("Data Cleaning")

# 세션 상태 초기화
need_session = get_session_variables()

# save_path.toml에서 저장된 경로 불러오기
save_path_manager = get_save_path_manager()
saved_paths = save_path_manager.get_paths()

for session in [*need_session, 'convert_data_path', 'split_data_path', 'log_save_path', 'show_save_btn'] :
    if session not in st.session_state:
        # 경로 설정의 경우 save_path.toml에서 값을 가져옴
        if session in ['convert_data_path', 'split_data_path', 'log_save_path']:
            st.session_state[session] = saved_paths.get(session, '')
        else:
            st.session_state[session] = None

if 'log_data' not in st.session_state:
    st.session_state['log_data'] = pd.DataFrame()

# 초기 페이지 설정
if st.session_state.get('selected_page') is None:
    st.session_state['selected_page'] = get_default_page()

# 세션에 저장된 파일 경로 유효성 확인
validate_session_file_path()

# 사이드바에 페이지 네비게이션 추가
with st.sidebar:
    st.header("📋 Navigation")

    # 페이지 선택 - 하드코딩된 페이지 옵션 사용
    page_options = ["Guide Page", "Error Check", "Dashboard", "Settings"]
    selected_page = st.selectbox(
        "Select Page",
        page_options,
        index=page_options.index(st.session_state.get('selected_page', 'Guide Page')) if st.session_state.get('selected_page') in page_options else 0
    )

    # 선택된 페이지가 변경되면 세션 상태 업데이트
    if selected_page != st.session_state.get('selected_page'):
        st.session_state['selected_page'] = selected_page

    st.divider()

    # 데이터 업로드 인터페이스는 모든 페이지에서 접근 가능
    show_data_upload_sidebar()

# 메인 콘텐츠 영역
if st.session_state.get('selected_page') == "Guide Page":
    st.header("📃 Guide Page")

    raw_data = st.session_state.get("raw_data")
    raw_data_path = st.session_state.get("raw_data_path")

    try :
        if raw_data is None and raw_data_path is None:
            st.info("사이드바에서 데이터 파일을 업로드해주세요.")
        elif raw_data is None and raw_data_path and raw_data_path.endswith('.xlsx'):
            st.warning('''엑셀 파일을 업로드하셨습니다. 사이드바에서 데이터 시트를 선택 후 Read Excel 버튼을 클릭해주세요.''')
        elif raw_data is not None:
            st.success("✅ 데이터 업로드 완료")

            # 데이터 정보 표시
            show_data_info()

            # 데이터 미리보기
            with st.expander("데이터 미리보기", expanded=False):
                st.dataframe(raw_data.head(get_preview_rows()), width='stretch')
    except Exception as e:
        st.error(f"읽을 수 없는 데이터 형식입니다. 시트 또는 데이터를 확인해주세요.")

elif st.session_state.get('selected_page') == "Error Check":
    show_error_check()

elif st.session_state.get('selected_page') == "Dashboard":
    show_dashboard()

elif st.session_state.get('selected_page') == "Settings":
    show_settings()