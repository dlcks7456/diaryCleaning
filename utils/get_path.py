import streamlit as st

def select_directory(title: str) -> str:
    """
    파일 탐색기로 디렉토리를 선택하는 함수
    
    Args:
        title (str): 파일 탐색기 창 제목
        
    Returns:
        str: 선택된 디렉토리 경로 (선택하지 않으면 빈 문자열)
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected_path = filedialog.askdirectory(title=title)
        root.destroy()

        return selected_path or ""
    except Exception as e:
        st.error(f"파일 탐색기를 열 수 없습니다: {str(e)}")
        return ""