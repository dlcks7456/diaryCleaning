import streamlit as st
import pandas as pd
import toml
import os
from typing import Dict, Any, List
import shutil


class ConfigManager:
    """TOML 설정 파일을 관리하는 클래스"""

    def __init__(self, setting_path: str = None, default_setting_path: str = None):
        # 현재 파일의 디렉토리를 기준으로 프로젝트 루트를 찾음
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)  # features 폴더의 상위 디렉토리

        # 기본값 설정 (절대 경로)
        if setting_path is None:
            setting_path = os.path.join(project_root, "setup", "setting.toml")
        if default_setting_path is None:
            default_setting_path = os.path.join(project_root, "setup", "default_setting.toml")
        self.setting_path = setting_path
        self.default_setting_path = default_setting_path
        self._setting = None
        self.load_setting()

    def load_setting(self) -> Dict[str, Any]:
        """TOML 설정 파일을 로드합니다."""
        try:
            if os.path.exists(self.setting_path):
                with open(self.setting_path, 'r', encoding='utf-8') as f:
                    self._setting = toml.load(f)
            else:
                st.error(f"설정 파일을 찾을 수 없습니다: {self.setting_path}")
                self._setting = {}
        except Exception as e:
            st.error(f"설정 파일 로드 중 오류 발생: {str(e)}")
            self._setting = {}

        return self._setting

    def save_setting(self, setting: Dict[str, Any]) -> bool:
        """TOML 설정 파일을 저장합니다."""
        try:
            with open(self.setting_path, 'w', encoding='utf-8') as f:
                toml.dump(setting, f)
            self._setting = setting
            return True
        except Exception as e:
            st.error(f"설정 파일 저장 중 오류 발생: {str(e)}")
            return False

    def save_setting_text(self, setting_text: str) -> bool:
        """TOML 텍스트를 직접 저장합니다."""
        try:
            # 먼저 텍스트가 유효한 TOML인지 확인
            toml.loads(setting_text)

            # 유효하면 파일에 저장
            with open(self.setting_path, 'w', encoding='utf-8') as f:
                f.write(setting_text)

            # 메모리에도 로드
            self._setting = toml.loads(setting_text)
            return True
        except Exception as e:
            st.error(f"설정 파일 저장 중 오류 발생: {str(e)}")
            return False

    def reset_setting(self) -> bool:
        """설정을 초기화합니다."""
        # if not os.path.exists(self.default_setting_path):
        #     st.error(f"기본 설정 파일을 찾을 수 없습니다: {self.default_setting_path}")
        #     return False

        # 기본 설정 파일을 현재 설정 파일로 복사
        shutil.copy2(self.default_setting_path, self.setting_path)

        # 메모리에도 새로 로드
        self.load_setting()

        return True

    def get_setting(self) -> Dict[str, Any]:
        """현재 설정을 반환합니다."""
        if self._setting is None:
            self.load_setting()
        return self._setting

    def get_setting_text(self) -> str:
        """현재 설정을 TOML 텍스트로 반환합니다."""
        try:
            with open(self.setting_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            st.error(f"설정 파일 읽기 중 오류 발생: {str(e)}")
            return ""

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """특정 섹션의 설정을 반환합니다."""
        setting = self.get_setting()
        return setting.get(section_name, {})

    def get_value(self, section: str, key: str, default=None):
        """특정 설정값을 반환합니다."""
        section_setting = self.get_section(section)
        return section_setting.get(key, default)

# 전역 ConfigManager 인스턴스
_setting_manager = None

def get_setting_manager() -> ConfigManager:
    """ConfigManager 싱글톤 인스턴스를 반환합니다."""
    global _setting_manager
    if _setting_manager is None:
        _setting_manager = ConfigManager()
    return _setting_manager

def show_settings():
    """설정 페이지를 표시합니다."""
    st.header('⚙️ Settings')

    # SavePathManager 인스턴스 가져오기
    # save_path_manager = get_save_path_manager()

    # Path Setting
    # st.caption('🗂️ 저장될 파일 경로 설정')
    # st.caption('값을 입력하지 않으면 읽은 Raw Data와 동일 경로에 저장됩니다.')
    # col1, col2, col3 = st.columns(3)

    # def handle_path_setting(col, path_key: str, display_name: str, save_path_manager):
    #     """경로 설정을 처리하는 공통 함수"""
    #     with col:
    #         # save_path.toml에서 저장된 값과 세션 상태 값 중 하나를 선택 (세션 상태 우선)
    #         saved_path = save_path_manager.get_path(path_key)
    #         current_path = st.session_state.get(path_key, saved_path)
    #
    #         path_value = st.text_input(f'{display_name} 저장 경로', value=current_path, disabled=True)
    #         path_btn = st.button('경로 설정', width='stretch', key=f'{path_key}_btn')
    #
    #         if path_btn:
    #             selected_path = select_directory(f"{display_name} 저장 경로 선택")
    #             if selected_path:
    #                 # 세션 상태와 save_path.toml 파일 모두에 저장
    #                 if save_path_manager.set_path(path_key, selected_path):
    #                     st.session_state[path_key] = selected_path
    #                     st.rerun()
    #                 # 에러 메시지는 set_path 내부에서 처리됨
    #
    #         # 세션 상태 동기화 (필요시)
    #         if current_path != st.session_state.get(path_key):
    #             st.session_state[path_key] = current_path

    # # 경로 설정 처리
    # path_settings = [
    #     ('convert_data_path', '변환 데이터'),
    #     ('split_data_path', '분할 데이터'),
    #     ('log_save_path', '로그 데이터')
    # ]
    #
    # for i, (path_key, display_name) in enumerate(path_settings):
    #     if i == 0:
    #         handle_path_setting(col1, path_key, display_name, save_path_manager)
    #     elif i == 1:
    #         handle_path_setting(col2, path_key, display_name, save_path_manager)
    #     elif i == 2:
    #         handle_path_setting(col3, path_key, display_name, save_path_manager)


    setting_manager = get_setting_manager()

    st.caption("TOML 파일 설정. 검수 및 변환을 위한 변수명 및 설정 값들을 조정합니다.")

    # 현재 설정을 텍스트로 가져오기
    current_setting_text = setting_manager.get_setting_text()

    # 코드 에디터 사용
    edited_setting_text = st.text_area(
        "setting.toml",
        value=current_setting_text,
        height=400,
        help="TOML 형식으로 설정을 편집하세요. 리스트는 ['item1', 'item2'] 형식으로 작성하세요."
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💾 Save", type="primary", width="stretch"):
            if setting_manager.save_setting_text(edited_setting_text):
                st.success("✅ Success")
                st.rerun()
            else:
                st.error("❌ Fail")

    with col2:
        if st.button("🔄 Reload", width="stretch"):
            setting_manager.load_setting()
            st.success("✅ Success")
            st.rerun()

    with col3:
        if st.button("⚠️ Reset", width="stretch") :
            if setting_manager.reset_setting():
                st.rerun()
            else:
                st.error("❌ Fail")

    # 현재 설정 미리보기
    with st.expander("📋 Current Config Preview", expanded=False):
        try:
            current_setting = setting_manager.get_setting()
            st.json(current_setting)
        except Exception as e:
            st.error(f"Config Parsing Error: {str(e)}")

    # TOML 문법 도움말
    with st.expander("ℹ️ TOML Syntax Help", expanded=False):
        st.markdown("""
        ### 기본 문법
        ```toml
        # 주석
        [섹션명]
        문자열_키 = "값"
        숫자_키 = 123
        불린_키 = true
        리스트_키 = ["항목1", "항목2", "항목3"]
        ```

        ### 예시
        ```toml
        [data_validation]
        product_list = ["제품 C", "제품 P", "제품 R"]
        max_answers = 36

        [column_names]
        panel_no = "PANELNO"
        product_col = "Q3"
        ```
        """)

# 편의 함수들 - 다른 모듈에서 설정값을 쉽게 가져올 수 있도록
def get_product_list() -> List[str]:
    """제품 리스트를 반환합니다."""
    return get_setting_manager().get_value("data_validation", "product_list", [])

def get_max_answers() -> int:
    """최대 응답 수를 반환합니다."""
    return get_setting_manager().get_value("data_validation", "max_answers", 36)

def get_column_name(column_key: str) -> str:
    """컬럼명을 반환합니다."""
    return get_setting_manager().get_value("column_names", column_key, "")

def get_problem_columns() -> List[str]:
    """Q6 컬럼 리스트를 반환합니다."""
    return get_setting_manager().get_value("problem_columns", "columns", [])

def get_error_column(error_key: str) -> str:
    """에러 컬럼명을 반환합니다."""
    return get_setting_manager().get_value("error_columns", error_key, "")

def get_ui_color(color_key: str) -> str:
    """UI 색상을 반환합니다."""
    return get_setting_manager().get_value("ui_colors", color_key, "")

def get_session_variables() -> List[str]:
    """세션 변수 리스트를 반환합니다."""
    return get_setting_manager().get_value("session_variables", "need_session", [])

def get_default_page() -> str:
    """기본 페이지를 반환합니다."""
    return get_setting_manager().get_value("session_variables", "default_page", "Guide Page")

def get_preview_rows() -> int:
    """미리보기 행 수를 반환합니다."""
    return get_setting_manager().get_value("data_preview", "preview_rows", 30)

def get_default_excel_sheet_index() -> int:
    """기본 엑셀 시트 인덱스를 반환합니다."""
    return get_setting_manager().get_value("data_validation", "default_excel_sheet_index", 1)

def get_duration_max() -> int:
    """최대 소요시간을 반환합니다."""
    return get_setting_manager().get_value("data_validation", "duration_max", 500)


# class SavePathManager:
#     """save_path.toml 파일을 관리하는 클래스"""
#
#     def __init__(self, save_path_file: str = None):
#         # 현재 파일의 디렉토리를 기준으로 프로젝트 루트를 찾음
#         if save_path_file is None:
#             current_dir = os.path.dirname(os.path.abspath(__file__))
#             project_root = os.path.dirname(current_dir)  # features 폴더의 상위 디렉토리
#             save_path_file = os.path.join(project_root, "setup", "save_path.toml")
#         self.save_path_file = save_path_file
#         self._paths = None
#         self.load_paths()
#
#     def load_paths(self) -> Dict[str, str]:
#         """save_path.toml 파일을 로드합니다."""
#         try:
#             if os.path.exists(self.save_path_file):
#                 with open(self.save_path_file, 'r', encoding='utf-8') as f:
#                     self._paths = toml.load(f)
#
#                 # 로드된 경로가 실제로 존재하는지 검증하고, 존재하지 않으면 초기화
#                 paths_updated = False
#                 for path_key in ['convert_data_path', 'split_data_path', 'log_save_path']:
#                     if path_key in self._paths and self._paths[path_key]:
#                         # 경로가 비어있지 않은 경우에만 존재 여부 확인
#                         if not os.path.exists(self._paths[path_key]):
#                             st.warning(f"⚠️ 저장된 {path_key} 경로가 존재하지 않습니다. 경로를 초기화합니다: {self._paths[path_key]}")
#                             self._paths[path_key] = ''
#                             paths_updated = True
#                     elif path_key not in self._paths:
#                         # 키가 없는 경우 기본값 추가
#                         self._paths[path_key] = ''
#                         paths_updated = True
#
#                 # 경로가 업데이트된 경우 파일에 저장
#                 if paths_updated:
#                     self.save_paths(self._paths)
#
#             else:
#                 # 파일이 없으면 기본값으로 생성
#                 self._paths = {
#                     'convert_data_path': '',
#                     'split_data_path': '',
#                     'log_save_path': ''
#                 }
#                 self.save_paths(self._paths)
#         except Exception as e:
#             st.error(f"경로 설정 파일 로드 중 오류 발생: {str(e)}")
#             self._paths = {
#                 'convert_data_path': '',
#                 'split_data_path': '',
#                 'log_save_path': ''
#             }
#         return self._paths
#
#     def save_paths(self, paths: Dict[str, str]) -> bool:
#         """save_path.toml 파일을 저장합니다."""
#         try:
#             with open(self.save_path_file, 'w', encoding='utf-8') as f:
#                 toml.dump(paths, f)
#             self._paths = paths
#             return True
#         except Exception as e:
#             st.error(f"경로 설정 파일 저장 중 오류 발생: {str(e)}")
#             return False
#
#     def get_paths(self) -> Dict[str, str]:
#         """현재 경로 설정을 반환합니다."""
#         if self._paths is None:
#             self.load_paths()
#         return self._paths
#
#     def get_path(self, path_key: str) -> str:
#         """특정 경로를 반환합니다."""
#         paths = self.get_paths()
#         return paths.get(path_key, '')
#
#     def set_path(self, path_key: str, path_value: str) -> bool:
#         """특정 경로를 설정하고 저장합니다."""
#         # 경로가 비어있지 않은 경우 존재 여부 확인
#         if path_value and not os.path.exists(path_value):
#             st.error(f"❌ 설정하려는 경로가 존재하지 않습니다: {path_value}")
#             return False
#
#         paths = self.get_paths()
#         paths[path_key] = path_value
#         return self.save_paths(paths)
#
#
# # 전역 SavePathManager 인스턴스
# _save_path_manager = None
#
# def get_save_path_manager() -> SavePathManager:
#     """SavePathManager 싱글톤 인스턴스를 반환합니다."""
#     global _save_path_manager
#     if _save_path_manager is None:
#         _save_path_manager = SavePathManager()
#     return _save_path_manager
#
#
# # 편의 함수들 - 다른 모듈에서 경로를 쉽게 가져올 수 있도록
# def get_convert_data_path() -> str:
#     """변환 데이터 저장 경로를 반환합니다."""
#     return get_save_path_manager().get_path('convert_data_path')
#
# def get_split_data_path() -> str:
#     """분할 데이터 저장 경로를 반환합니다."""
#     return get_save_path_manager().get_path('split_data_path')
#
# def get_log_save_path() -> str:
#     """로그 데이터 저장 경로를 반환합니다."""
#     return get_save_path_manager().get_path('log_save_path')