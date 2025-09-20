import streamlit as st
import pandas as pd
from features.error_check import show_error_check
from features.dashboard import show_dashboard
from features.setting import get_default_page, get_preview_rows
from utils.data_loader import show_data_upload_sidebar, show_data_info, validate_session_file_path
from features.split_merge_data import show_split_merge
from features.export_for_import import show_export_for_import

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

if 'updated_data' not in st.session_state:
    st.session_state['updated_data'] = False

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
    page_options = ["Guide Page", "Error Check", "Dashboard", "Split & Merge", "Export for Import"]
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

    with st.expander("Simple Guide", expanded=False):
        # 컨테이너 시작
        st.markdown('<div class="guide-container">', unsafe_allow_html=True)
        
        # 헤더 섹션
        st.markdown("""
        <div class="guide-header">
            <h2>🎯 Introduction Data Cleaning</h2>
            <p class="guide-subtitle">데이터 검수 및 정제 간편화</p>
        </div>
        """, unsafe_allow_html=True)

        # 사용 팁 섹션
        st.markdown("""
        <div class="tips-section">
            <h3>💡 주요 기능</h3>
            <div class="tips-grid">
                <div class="tip-item">
                    <div class="tip-icon">⚡</div>
                    <div class="tip-text">
                        <strong>변수 변환</strong>
                    </div>
                    <p>데이터 업로드시 자동 변환</p>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">🧹</div>
                    <div class="tip-text">
                        <strong>클리닝</strong>
                    </div>
                    <p>오류 유형별 필터링 및 수정</p>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">💾</div>
                    <div class="tip-text">
                        <strong>로그 저장</strong>
                    </div>
                    <p>모든 변경사항은 로그 기록</p>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">🚀</div>
                    <div class="tip-text">
                        <strong>분할과 병합</strong>
                    </div>
                    <p>응답자별/등분 분할 및 병합</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 주의 사항 섹션
        st.markdown("""
        <div class="warning-section">
            <h3>🚨 주의 사항</h3>
            <p>Raw Data를 업로드하면 자동으로 변수 변환이 진행됩니다.</p>
            <p>변수 변환이 진행된 후 Raw Data의 경로 기준으로 이 후 작업이 진행됩니다. (Base Directory)</p>
            <p>Error Check 페이지에서 수정시 `저장` 버튼을 꼭 눌러주세요.</p>
            <p>병합은 Raw Data를 업로드하지 않아도 진행할 수 있습니다.</p>
            <p>병합이 필요한 데이터는 기존 데이터 형태를 유지해야합니다.</p>
        </div>
        """, unsafe_allow_html=True)

        # 기능 소개 섹션
        st.markdown('<div class="guide-section">', unsafe_allow_html=True)
                        
        # Error Check 카드
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-content">
                <h3>Error Check</h3>
                <p>데이터의 오류 케이스를 검사하고 수정 및 삭제할 수 있는 기능을 제공합니다.</p>
                <p>수정 및 삭제를 반영한 후 변동 사항이 로그에 기록됩니다.</p>
                <ul class="feature-list">
                    <li>🔄 중복 응답 검사</li>
                    <li>📊 응답 수 초과 검사</li>
                    <li>🔢 순서 오류 검사</li>
                    <li>⏰ 시간 관련 오류 검사</li>
                    <li>📅 날짜 순서 검사</li>
                    <li>⏱️ 착용 시간 검사</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Dashboard 카드
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-content">
                <h3>Dashboard</h3>
                <p>응답 현황 확인 페이지입니다.</p>
                <ul class="feature-list">
                    <li>📈 날짜별 응답 수 차트</li>
                    <li>📋 지역별 연령대 교차표</li>
                    <li>🔍 제품별 문제점 분석</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Split & Merge 카드
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🚀</div>
            <div class="feature-content">
                <h3>Split & Merge</h3>
                <p>데이터를 분할하거나 병합하는 기능을 제공합니다.</p>
                <p>패널넘버 기준으로 n등분 또는 응답자별로 분할할 수 있습니다.</p>
                <p>에러 케이스만 분류하여 저장할 수 있습니다.</p>
                <ul class="feature-list">
                    <li>📂 <strong>Split:</strong> 데이터를 여러 파일로 분할</li>
                    <li>🔗 <strong>Merge:</strong> 여러 파일을 하나로 병합</li>
                    <li>✅ 에러 케이스만 분류하여 저장</li>
                    <li>👥 응답자별 분할 옵션</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Export for Import 카드
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📤</div>
            <div class="feature-content">
                <h3>Export for Import</h3>
                <p>데이터를 DS에 임포트하기 위해 필요한 형태로 변환합니다.</p>
                <ul class="feature-list">
                    <li>📋 필요한 컬럼만 선택하여 내보내기</li>
                    <li>📁 자동으로 import 폴더에 저장</li>
                    <li>👀 미리보기 기능 제공</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 기능 섹션 종료
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 작업 순서 섹션
        st.markdown("""
        <div class="workflow-section">
            <h3>🔄 권장 작업 순서</h3>
            <div class="workflow-steps">
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h4>데이터 업로드</h4>
                        <p>사이드바에서 Raw Data를 업로드합니다.</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h4>Dashboard 확인</h4>
                        <p>데이터의 전체적인 현황을 확인합니다.</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h4>Error Check</h4>
                        <p>클리닝 대상 데이터를 확인 및 수정/삭제를 진행합니다.</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h4>Split & Merge</h4>
                        <p>필요에 따라 데이터를 분할하거나 병합합니다.</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">5</div>
                    <div class="step-content">
                        <h4>Export</h4>
                        <p>최종적으로 DS에 임포트할 데이터를 다운로드합니다.</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 컨테이너 종료
        st.markdown('</div>', unsafe_allow_html=True)

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

elif st.session_state.get('selected_page') == "Split & Merge":
    show_split_merge()

elif st.session_state.get('selected_page') == "Export for Import":
    show_export_for_import()

# elif st.session_state.get('selected_page') == "Settings":
#     show_settings()