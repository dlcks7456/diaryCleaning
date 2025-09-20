"""
컬럼명 관리를 위한 공통 모듈

이 모듈은 프로젝트 전체에서 사용되는 컬럼명들을 중앙에서 관리하고,
중복 코드를 줄이고 유지보수성을 높이기 위해 생성되었습니다.

주요 기능:
- 컬럼명 캐싱 및 일괄 로드
- 에러 컬럼명 관리
- 컬럼 그룹 관리 (error_columns, check_columns 등)
- 컬럼명 검증 및 기본값 제공
"""

from typing import List, Dict, Optional
from features.setting import get_column_name, get_error_column, get_max_answers, get_product_list, get_duration_max


class ColumnManager:
    """
    컬럼명을 중앙에서 관리하는 클래스
    
    이 클래스는 모든 컬럼명을 한 번에 로드하고 캐싱하여
    반복적인 get_column_name(), get_error_column() 호출을 방지합니다.
    """
    
    def __init__(self):
        """ColumnManager 초기화"""
        self._columns: Dict[str, str] = {}
        self._error_columns: Dict[str, str] = {}
        self._load_all_columns()
    
    def _load_all_columns(self) -> None:
        """
        모든 컬럼명을 한 번에 로드하여 캐싱
        
        이 메서드는 설정 파일에서 모든 컬럼명을 읽어와서
        내부 딕셔너리에 저장합니다.
        """
        # 기본 컬럼명들 로드
        self._columns = {
            'index_col': get_column_name('index_col'),
            'unique_id': get_column_name('unique_id'),
            'panel_code': get_column_name('panel_code'),
            'panel_no': get_column_name('panel_no'),
            'input_col': get_column_name('input_col'),
            'order_col': get_column_name('order_col'),
            'product_col': get_column_name('product_col'),
            'start_col': get_column_name('start_col'),
            'end_col': get_column_name('end_col'),
            'answer_date': get_column_name('answer_date'),
            'area': get_column_name('area'),
            'age_5': get_column_name('age_5'),
        }
        
        # 에러 컬럼명들 로드
        self._error_columns = {
            'order_error': get_error_column('order_error'),
            'duplicate_error': get_error_column('duplicate_error'),
            'day_order_error': get_error_column('day_order_error'),
            'answer_count_error': get_error_column('answer_count_error'),
            'start_end_duplicate': get_error_column('start_end_duplicate'),
            'total_duration': get_error_column('total_duration'),
            'time_error': get_error_column('time_error'),
            'duration_error': get_error_column('duration_error'),
            'answer_combine': get_error_column('answer_combine'),
        }
    
    def get_column(self, column_key: str) -> str:
        """
        기본 컬럼명을 반환
        
        Args:
            column_key (str): 컬럼 키 (예: 'panel_no', 'product_col')
            
        Returns:
            str: 실제 컬럼명
        """
        return self._columns.get(column_key, "")
    
    def get_error_column(self, error_key: str) -> str:
        """
        에러 컬럼명을 반환
        
        Args:
            error_key (str): 에러 컬럼 키 (예: 'order_error', 'duplicate_error')
            
        Returns:
            str: 실제 에러 컬럼명
        """
        return self._error_columns.get(error_key, "")
    
    def get_error_columns(self) -> List[str]:
        """
        모든 에러 컬럼명 리스트를 반환
        
        Returns:
            List[str]: 에러 컬럼명 리스트
        """
        return [
            self._error_columns['order_error'],
            self._error_columns['duplicate_error'],
            self._error_columns['day_order_error'],
            self._error_columns['answer_count_error'],
            self._error_columns['start_end_duplicate'],
            self._error_columns['time_error'],
        ]
    
    def get_check_columns(self) -> List[str]:
        """
        체크 컬럼명 리스트를 반환 (duration_error 등)
        
        Returns:
            List[str]: 체크 컬럼명 리스트
        """
        return [self._error_columns['duration_error']]
    
    def get_boolean_columns(self) -> List[str]:
        """
        모든 불린 컬럼명 리스트를 반환 (에러 + 체크 컬럼)
        
        Returns:
            List[str]: 불린 컬럼명 리스트
        """
        return self.get_error_columns() + self.get_check_columns()
    
    def get_columns_to_remove(self) -> List[str]:
        """
        제거해야 할 컬럼명 리스트를 반환
        
        이 컬럼들은 데이터 변환 과정에서 생성되었다가
        최종 출력 시 제거되는 컬럼들입니다.
        
        Returns:
            List[str]: 제거할 컬럼명 리스트
        """
        input_col = self.get_column('input_col')
        start_col = self.get_column('start_col')
        end_col = self.get_column('end_col')
        
        return [
            f'{input_col}_month', f'{input_col}_day',
            f'{start_col}_hour', f'{start_col}_min', f'{start_col}_time',
            f'{end_col}_hour', f'{end_col}_min', f'{end_col}_time',
            self._error_columns['total_duration'],
            *self.get_error_columns(),
            *self.get_check_columns(),
            self._error_columns['answer_combine'],
        ]
    
    def get_derived_columns(self) -> Dict[str, str]:
        """
        파생된 컬럼명들을 반환
        
        기본 컬럼에서 파생된 컬럼명들 (예: Q1_month, Q4_hour 등)
        
        Returns:
            Dict[str, str]: 파생 컬럼명 딕셔너리
        """
        input_col = self.get_column('input_col')
        start_col = self.get_column('start_col')
        end_col = self.get_column('end_col')
        
        return {
            'input_month': f'{input_col}_month',
            'input_day': f'{input_col}_day',
            'start_time': f'{start_col}_time',
            'start_hour': f'{start_col}_hour',
            'start_min': f'{start_col}_min',
            'end_time': f'{end_col}_time',
            'end_hour': f'{end_col}_hour',
            'end_min': f'{end_col}_min',
        }
    
    def get_log_columns(self) -> List[str]:
        """
        로그 기록에 사용할 컬럼명 리스트를 반환
        
        Returns:
            List[str]: 로그 컬럼명 리스트
        """
        return [
            self.get_column('unique_id'),
            self.get_column('panel_no'),
            self.get_column('input_col'),
            self.get_column('order_col'),
            self.get_column('product_col'),
            self.get_column('start_col'),
            self.get_column('end_col'),
        ]
    
    def get_required_columns_for_export(self) -> List[str]:
        """
        Export for Import에서 필수로 포함해야 할 컬럼명 리스트를 반환
        
        Returns:
            List[str]: 필수 컬럼명 리스트
        """
        derived = self.get_derived_columns()
        return [
            self.get_column('unique_id'),
            self.get_column('panel_code'),
            self.get_column('panel_no'),
            derived['input_month'],
            derived['input_day'],
            self.get_column('order_col'),
            derived['start_hour'],
            derived['start_min'],
            derived['end_hour'],
            derived['end_min'],
        ]
    
    def refresh(self) -> None:
        """
        컬럼명 캐시를 새로고침
        
        설정 파일이 변경된 경우 이 메서드를 호출하여
        새로운 컬럼명들을 다시 로드할 수 있습니다.
        """
        self._load_all_columns()


# 전역 ColumnManager 인스턴스
_column_manager: Optional[ColumnManager] = None


def get_column_manager() -> ColumnManager:
    """
    ColumnManager 싱글톤 인스턴스를 반환
    
    Returns:
        ColumnManager: 전역 ColumnManager 인스턴스
    """
    global _column_manager
    if _column_manager is None:
        _column_manager = ColumnManager()
    return _column_manager


# 편의 함수들 - 기존 코드와의 호환성을 위해 제공
def get_column(column_key: str) -> str:
    """기본 컬럼명을 반환하는 편의 함수"""
    return get_column_manager().get_column(column_key)


def get_error_column_name(error_key: str) -> str:
    """에러 컬럼명을 반환하는 편의 함수"""
    return get_column_manager().get_error_column(error_key)


def get_all_error_columns() -> List[str]:
    """모든 에러 컬럼명 리스트를 반환하는 편의 함수"""
    return get_column_manager().get_error_columns()


def get_all_check_columns() -> List[str]:
    """모든 체크 컬럼명 리스트를 반환하는 편의 함수"""
    return get_column_manager().get_check_columns()


def get_all_boolean_columns() -> List[str]:
    """모든 불린 컬럼명 리스트를 반환하는 편의 함수"""
    return get_column_manager().get_boolean_columns()


def get_columns_to_remove() -> List[str]:
    """제거할 컬럼명 리스트를 반환하는 편의 함수"""
    return get_column_manager().get_columns_to_remove()


def get_derived_column_names() -> Dict[str, str]:
    """파생 컬럼명 딕셔너리를 반환하는 편의 함수"""
    return get_column_manager().get_derived_columns()


def get_log_column_names() -> List[str]:
    """로그 컬럼명 리스트를 반환하는 편의 함수"""
    return get_column_manager().get_log_columns()


def get_required_export_columns() -> List[str]:
    """Export용 필수 컬럼명 리스트를 반환하는 편의 함수"""
    return get_column_manager().get_required_columns_for_export()


def refresh_column_cache() -> None:
    """컬럼명 캐시를 새로고침하는 편의 함수"""
    get_column_manager().refresh()
