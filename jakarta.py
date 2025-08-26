import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import json
import os


# =======================================
# 인증 ID 목록
# =======================================
ALLOWED_IDS = ['kimdonghyun']

# =======================================
# 세션 상태 기본값
# =======================================
if 'authorized' not in st.session_state:
    st.session_state.authorized = False
if 'home_clicked' not in st.session_state:
    st.session_state.home_clicked = False

# =======================================
# 로그인 화면 (단일화)
#  - Enter 키 제출을 위해 st.form 사용
#  - 여기서 렌더링을 멈추기 위해 st.stop() 호출 (핵심)
# =======================================

def show_login():
    # 로고와 헤더를 2개 컬럼으로 배치
    logo_col, header_col = st.columns([1, 7])
    
    with logo_col:
        st.image("logo.png", width=65)
    
    with header_col:
        st.subheader("Korea - Jakara Container Export Data Analysis")

    # 한 행에 ID 입력칸과 버튼 배치
    col1, col2 = st.columns([9, 1])  # 비율은 필요에 따라 조정 가능

    with col1:
        user_id = st.text_input(
            label="Please enter your ID",
            label_visibility="collapsed",
            placeholder="Please enter your ID",
            key="login_user_id",
        )

    with col2:
        enter_clicked = st.button("Enter", use_container_width=True)

    # 버튼 클릭 시 인증 처리
    if enter_clicked:
        if user_id in ALLOWED_IDS:
            st.session_state.authorized = True
            st.rerun()
        elif user_id:
            st.warning("Unregistered ID. Please contact the administrator.")

    # YouTube 배경
    youtube_url = "https://www.youtube.com/embed/7XSyroiA-FI?autoplay=1&mute=1&loop=1&playlist=7XSyroiA-FI"
    st.markdown(
        f"""
        <style>
            iframe {{ border: none !important; }}
        </style>
        <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;">
            <iframe src="{youtube_url}"
                    style="position:absolute;top:0;left:0;width:100%;height:100%;"
                    allow="autoplay; encrypted-media"
                    allowfullscreen>
            </iframe>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown("")
    st.markdown(
        "<p style='text-align: center; font-size: 12px; color: gray;'>"
        "© 2025 Created by KUMO Logistics | Contact : main@kologis.co.kr"
        "</p>",
        unsafe_allow_html=True
    )
    
    # 🔴 이후 렌더링 중단 (중요)
    st.stop()


# =======================================
# 데이터 관련 설정/함수
# =======================================
PREDEFINED_FILE_PATH = 'jakarta.xlsx'

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(PREDEFINED_FILE_PATH, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"파일 로드 중 오류 발생: {e}")
        return None


def show_data_overview(df, start_date=None, end_date=None):
    st.markdown(f"✅ **분석 데이터 개요**")

    total_records = len(df)
    total_exporters = df['수출자'].nunique()
    total_importers = df['수입자'].nunique()
    total_containers = df['컨테이너수'].sum()
    total_container_lines = df['컨테이너선사'].nunique()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.markdown(
        """
        <div style='text-align: center;'>
            📄 <b>선적 건</b><br>
            <span style='font-size: 20px;'>{:,}</span>
        </div>
        """.format(total_records),
        unsafe_allow_html=True,
    )

    col2.markdown(
        """
        <div style='text-align: center;'>
            🧑 <b>수출자</b><br>
            <span style='font-size: 20px;'>{:,}</span>
        </div>
        """.format(total_exporters),
        unsafe_allow_html=True,
    )

    col3.markdown(
        """
        <div style='text-align: center;'>
            👳 <b>수입자</b><br>
            <span style='font-size: 20px;'>{:,}</span>
        </div>
        """.format(total_importers),
        unsafe_allow_html=True,
    )

    col4.markdown(
        """
        <div style='text-align: center;'>
            📦 <b>컨테이너</b><br>
            <span style='font-size: 20px;'>{:,}</span>
        </div>
        """.format(total_containers),
        unsafe_allow_html=True,
    )

    col5.markdown(
        """
        <div style='text-align: center;'>
            🚢 <b>컨테이너선사</b><br>
            <span style='font-size: 20px;'>{}</span>
        </div>
        """.format(total_container_lines),
        unsafe_allow_html=True,
    )

    st.write("")    
    st.image("jakarta1.jpg", width=700)
    
    # 컨테이너선사 정보 추가
    st.markdown("---")
    container_line_df = df.groupby('컨테이너선사').agg({'컨테이너수': 'sum'}).reset_index()
    container_line_df = container_line_df.sort_values(by='컨테이너수', ascending=False)
    container_line_df['순위'] = range(1, len(container_line_df) + 1)
    container_line_df = container_line_df[['순위', '컨테이너선사', '컨테이너수']].reset_index(drop=True)
    total_lines = len(container_line_df)
    
    st.write("✅ **컨테이너선사 정보**")
    with st.expander(f"🔍 총 **{total_lines}**개 선사 확인", expanded=False):
        st.dataframe(container_line_df, use_container_width=True)


def filter_data(df, analysis_type, min_containers, selected_category='ALL'):
    # 대분류 필터링
    if selected_category != 'ALL':
        if analysis_type == '수출자':
            df = df[df['수출자 대분류'] == selected_category]
        else:
            df = df[df['수입자 대분류'] == selected_category]
    
    # 분석 타입에 따라 데이터 필터링
    if analysis_type == '수출자':
        grouped = df.groupby(['수출자', '수출자 대분류', '수출자 사업내용']).agg({'컨테이너수': 'sum'}).reset_index()
        grouped = grouped[grouped['컨테이너수'] >= min_containers]
        grouped = grouped.sort_values(by='컨테이너수', ascending=False).reset_index(drop=True)
        grouped['순위'] = range(1, len(grouped) + 1)
        return grouped[['순위', '수출자', '수출자 대분류', '수출자 사업내용', '컨테이너수']]
    else:  # 수입자
        grouped = df.groupby(['수입자', '수입자 대분류', '수입자 사업내용']).agg({'컨테이너수': 'sum'}).reset_index()
        grouped = grouped[grouped['컨테이너수'] >= min_containers]
        grouped = grouped.sort_values(by='컨테이너수', ascending=False).reset_index(drop=True)
        grouped['순위'] = range(1, len(grouped) + 1)
        return grouped[['순위', '수입자', '수입자 대분류', '수입자 사업내용', '컨테이너수']]



# 홈으로 돌아가기 (세션 초기화)

def reset_to_home():
    if 'authorized' not in st.session_state:
        st.session_state.authorized = False  # 비정상 접근 방지

    # 검색/분석 결과 초기화
    st.session_state.has_search_results = False
    st.session_state.has_analysis_results = False
    st.session_state.analysis_data = None
    st.session_state.show_similar_customers = False
    st.session_state.analysis_type = '수출자'
    st.session_state.min_containers = 0
    st.session_state.selected_company = None
    st.session_state.selected_category = 'ALL'
    st.session_state.selected_business = 'ALL'
    st.session_state.has_business_filter = False
    st.session_state.home_clicked = True

    # 사이드바 조건들 초기화
    for key in [
        'analysis_type', 'min_containers', 'selected_company', 'selected_category', 'selected_business', 'has_business_filter',
    ]:
        if key in st.session_state:
            del st.session_state[key]


# =======================================
# 메인 앱
#  - 로그인 중복 제거 (show_login만 사용)
#  - 인증 전: show_login() -> st.stop()
# =======================================

def app():
    # 쿼리 파라미터에 home 있으면 홈 초기화
    if "home" in st.query_params:
        reset_to_home()

    # 인증 확인 (여기서는 새 로그인 UI를 만들지 않음)
    if not st.session_state.get('authorized', False):
        show_login()  # 방어적 호출

    # ---- 여기부터 대시보드 ----
    if not st.session_state.get('has_search_results', False) and not st.session_state.get('has_analysis_results', False):
        # 로고와 헤더를 2개 컬럼으로 배치
        logo_col, header_col = st.columns([1, 6])
        
        with logo_col:
            st.image(r"C:\Users\hanse\Desktop\kumo\logo.png", width=55)
        
        with header_col:
            st.subheader("Korea - Indonesia, Jakarta 수출 컨테이너 분석")
        
        st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)

    with st.spinner("⏳ 조금만 기다려주세요. 데이터 로딩 중입니다."):
        df = load_data()
    if df is None:
        return

    # 세션 키 기본값 설정
    for key, val in {
        'has_search_results': False,
        'has_analysis_results': False,
        'analysis_data': None,
        'analysis_type': '수출자',
        'min_containers': 0,
        'selected_company': None,
        'selected_category': 'ALL',
        'selected_business': 'ALL',
        'has_business_filter': False,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

    with st.sidebar:
        # ✅ 사이드바: 제목 + 홈 버튼을 한 줄에 배치
        col1, col2 = st.columns([2.8, 1])
        with col1:
            st.subheader("🔍 검색 조건 설정")            
        with col2:
            if st.button("🏠", key="home_button"):
                reset_to_home()
                st.rerun()
        
        # 분석 타입 선택
        st.session_state.analysis_type = st.selectbox(
            "**❓ 분석 대상**(수출자/수입자)", 
            ['수출자', '수입자'], 
            index=['수출자', '수입자'].index(st.session_state.analysis_type)
        )
        
        # 대분류 선택 (분석 타입에 따라 동적 변경)
        if st.session_state.analysis_type == '수출자':
            available_categories = ['ALL'] + sorted(df['수출자 대분류'].dropna().unique().tolist())
            category_label = "**🏢 수출자 대분류**"
        else:
            available_categories = ['ALL'] + sorted(df['수입자 대분류'].dropna().unique().tolist())
            category_label = "**🏢 수입자 대분류**"
        
        # 현재 선택된 대분류가 새로운 분석 타입에 없으면 ALL로 초기화
        if st.session_state.selected_category not in available_categories:
            st.session_state.selected_category = 'ALL'
        
        st.session_state.selected_category = st.selectbox(
            category_label,
            available_categories,
            index=available_categories.index(st.session_state.selected_category) if st.session_state.selected_category in available_categories else 0
        )
        
        # 최소 컨테이너 수 설정
        container_values = [0, 10, 50, 100, 500, 1000, 5000, 10000]
        container_index = container_values.index(st.session_state.min_containers) if st.session_state.min_containers in container_values else 0
        st.session_state.min_containers = st.selectbox("**📦 최소 컨테이너 수**", container_values, index=container_index)

        if st.button("조건 검색", use_container_width=True):
            st.session_state.has_search_results = True
            st.session_state.has_analysis_results = False
            st.session_state.analysis_data = None
            st.session_state.selected_company = None
            st.session_state.has_business_filter = False
            st.session_state.selected_business = 'ALL'
            st.rerun()
        
        # 개별 회사 선택
        st.markdown("---")
        st.subheader(" **🔍 개별 상세 분석**")
        
        # 선택된 대분류에 따라 회사 목록 필터링
        if st.session_state.analysis_type == '수출자':
            if st.session_state.selected_category == 'ALL':
                filtered_companies = df['수출자'].dropna().astype(str).unique()
            else:
                filtered_companies = df[df['수출자 대분류'] == st.session_state.selected_category]['수출자'].dropna().astype(str).unique()
            all_companies = sorted(filtered_companies.tolist())
            company_label = "수출자"
        else:
            if st.session_state.selected_category == 'ALL':
                filtered_companies = df['수입자'].dropna().astype(str).unique()
            else:
                filtered_companies = df[df['수입자 대분류'] == st.session_state.selected_category]['수입자'].dropna().astype(str).unique()
            all_companies = sorted(filtered_companies.tolist())
            company_label = "수입자"
        
        company_options = [f"{company_label} 입력하세요"] + all_companies
        default_company = st.session_state.selected_company if st.session_state.get("selected_company") else company_options[0]
        
        selected_company = st.selectbox(
            f"🧑 **{company_label} 검색**", 
            company_options, 
            index=company_options.index(default_company) if default_company in company_options else 0
        )

        if selected_company != f"{company_label} 선택":
            st.session_state.selected_company = selected_company
        else:
            st.session_state.selected_company = None
        
        if st.button(f"{company_label} 분석", use_container_width=True):
            if st.session_state.selected_company:
                st.session_state.has_analysis_results = True
                st.session_state.has_search_results = False
                
                # 개별 분석 데이터 준비
                if st.session_state.analysis_type == '수출자':
                    filtered = df[df['수출자'] == st.session_state.selected_company]
                else:
                    filtered = df[df['수입자'] == st.session_state.selected_company]
                
                if not filtered.empty:
                    st.session_state.analysis_data = {
                        'filtered': filtered,
                        'company': st.session_state.selected_company,
                        'type': st.session_state.analysis_type
                    }
                else:
                    st.session_state.analysis_data = None
                    st.warning(f"선택한 {company_label}에 해당하는 데이터가 없습니다.")
                    return
                
                st.rerun()
            else:
                st.warning(f"{company_label}를 선택해 주세요.")
        
        st.markdown(
            "<div style='font-size:11px; text-align:center; color:gray;'>ⓒ 2025 KUMO Logistics</div>",
            unsafe_allow_html=True
        )
    # 전체 분석 결과 표시
    if st.session_state.has_search_results:
        analysis_type = st.session_state.analysis_type
        
        st.subheader(f"📊 {analysis_type} 전체 분석 결과")
        st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
        
        st.markdown("🚩 **분석 조건**")
        category_display = st.session_state.selected_category if st.session_state.selected_category != 'ALL' else '전체'
        st.markdown(f"""
        <div style='display: flex; justify-content: space-around; text-align: center;'>
            <div>
                <strong>📊 분석 대상</strong><br>
                <span style='font-size:16px;'>{analysis_type}</span>
            </div>
            <div>
                <strong>🏢 대분류</strong><br>
                <span style='font-size:16px;'>{category_display}</span>
            </div>
            <div>
                <strong>📦 최소 컨테이너 수</strong><br>
                <span style='font-size:16px;'>{st.session_state.min_containers:,}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
        
        with st.spinner("⌛ 데이터를 분석 중입니다..."):
            result_df = filter_data(df, analysis_type, st.session_state.min_containers, st.session_state.selected_category)
            
            if not result_df.empty:
                total_companies = len(result_df)
                total_containers = result_df['컨테이너수'].sum()
                
                st.write(f"✅ **{analysis_type} 리스트**")
                with st.expander(f"🔍 총 **{total_companies}**개 {analysis_type} 확인 (총 컨테이너: {total_containers:,}대)", expanded=True):
                    # 컬럼 이름을 더 보기 좋게 변경
                    display_df = result_df.copy()
                    if analysis_type == '수출자':
                        display_df.columns = ['순위', '수출자', '대분류', '사업내용', '컨테이너수']
                    else:
                        display_df.columns = ['순위', '수입자', '대분류', '사업내용', '컨테이너수']
                    
                    st.dataframe(display_df, use_container_width=True)
                
                # 사업내용별 추가 필터링 기능
                st.markdown("---")
                st.markdown("🔍 **사업내용별 추가 검색**")
                
                # 결과 데이터에서 사업내용 목록 추출
                if analysis_type == '수출자':
                    available_businesses = ['ALL'] + sorted(result_df['수출자 사업내용'].dropna().unique().tolist())
                    business_column = '수출자 사업내용'
                else:
                    available_businesses = ['ALL'] + sorted(result_df['수입자 사업내용'].dropna().unique().tolist())
                    business_column = '수입자 사업내용'
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    selected_business = st.selectbox(
                        f"💼 {analysis_type} 사업내용 선택",
                        available_businesses,
                        key="business_filter",
                        label_visibility="collapsed",
                        index=0
                    )
                
                with col2:
                    if st.button("사업내용 검색", use_container_width=True):
                        st.session_state.selected_business = selected_business
                        st.session_state.has_business_filter = True
                        st.rerun()
                
                # 사업내용 필터링 결과 표시
                if st.session_state.get('has_business_filter', False) and st.session_state.get('selected_business', 'ALL') != 'ALL':
                    filtered_business_df = result_df[result_df[business_column] == st.session_state.selected_business]
                    
                    if not filtered_business_df.empty:
                        total_filtered = len(filtered_business_df)
                        total_filtered_containers = filtered_business_df['컨테이너수'].sum()
                        
                        st.markdown(f"**📊 '{st.session_state.selected_business}' 사업내용 결과**")
                        with st.expander(f"🔍 총 **{total_filtered}**개 {analysis_type} 확인 (총 컨테이너: {total_filtered_containers:,}대)", expanded=True):
                            # 컬럼 이름을 더 보기 좋게 변경
                            display_filtered_df = filtered_business_df.copy()
                            if analysis_type == '수출자':
                                display_filtered_df.columns = ['순위', '수출자', '대분류', '사업내용', '컨테이너수']
                            else:
                                display_filtered_df.columns = ['순위', '수입자', '대분류', '사업내용', '컨테이너수']
                            
                            st.dataframe(display_filtered_df, use_container_width=True)
                    else:
                        st.warning("선택한 사업내용에 해당하는 데이터가 없습니다.")

            else:
                st.warning("조건에 맞는 데이터가 없습니다.")
    # 개별 분석 결과 표시 (세션 상태 기반)
    if st.session_state.has_analysis_results and st.session_state.analysis_data:
        filtered = st.session_state.analysis_data['filtered']
        selected_company = st.session_state.analysis_data['company']
        analysis_type = st.session_state.analysis_data['type']

        st.subheader(f"📈 {selected_company} 상세 분석 결과")
        st.markdown("<hr style='margin-top: 5px; margin-bottom: 10px;'>", unsafe_allow_html=True)
        st.markdown("✅ **요약 정보**")

        total_records = len(filtered)
        total_containers = filtered['컨테이너수'].sum()
        total_container_lines = filtered['컨테이너선사'].nunique()
        
        # 상대방 수 계산
        if analysis_type == '수출자':
            partner_count = filtered['수입자'].nunique()
            partner_label = "거래 수입자"
        else:
            partner_count = filtered['수출자'].nunique()
            partner_label = "거래 수출자"

        col1, col2, col3, col4 = st.columns(4)
        
        col1.markdown(f"""
        <div style='text-align: center;'>
            📄 <b>선적 건</b><br>
            <span style='font-size: 20px;'>{total_records:,}</span>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div style='text-align: center;'>
            📦 <b>컨테이너</b><br>
            <span style='font-size: 20px;'>{total_containers:,}</span>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div style='text-align: center;'>
            👥 <b>{partner_label}</b><br>
            <span style='font-size: 20px;'>{partner_count}</span>
        </div>
        """, unsafe_allow_html=True)

        col4.markdown(f"""
        <div style='text-align: center;'>
            🚢 <b>부킹 선사</b><br>
            <span style='font-size: 20px;'>{total_container_lines}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # 회사 정보 표시
        if analysis_type == '수출자':
            company_info = filtered[['수출자', '수출자 대분류', '수출자 사업내용']].drop_duplicates().iloc[0]
            st.markdown("✅ **회사 정보**")
            st.markdown(f"**회사명:** {company_info['수출자']}")
            st.markdown(f"**대분류:** {company_info['수출자 대분류']}")
            st.markdown(f"**사업내용:** {company_info['수출자 사업내용']}")
        else:
            company_info = filtered[['수입자', '수입자 대분류', '수입자 사업내용']].drop_duplicates().iloc[0]
            st.markdown("✅ **회사 정보**")
            st.markdown(f"**회사명:** {company_info['수입자']}")
            st.markdown(f"**대분류:** {company_info['수입자 대분류']}")
            st.markdown(f"**사업내용:** {company_info['수입자 사업내용']}")

        st.markdown("✅ **상세 정보**")

        with st.expander("🔍 **상세 정보 확인**", expanded=False):
            # 상대방 분석 (수출자 분석 시 → 수입자 정보, 수입자 분석 시 → 수출자 정보)
            if analysis_type == '수출자':
                # 수출자 분석 시 수입자 정보 표시
                partner_summary = filtered.groupby(['수입자', '수입자 대분류', '수입자 사업내용']).agg({'컨테이너수': 'sum'}).reset_index()
                partner_summary = partner_summary.sort_values(by='컨테이너수', ascending=False).reset_index(drop=True)
                partner_summary['순위'] = range(1, len(partner_summary) + 1)
                partner_summary = partner_summary[['순위', '수입자', '수입자 대분류', '수입자 사업내용', '컨테이너수']]
                
                # 비중(%) 계산
                total_containers_partner = partner_summary['컨테이너수'].sum()
                partner_summary['비중(%)'] = (partner_summary['컨테이너수'] / total_containers_partner * 100).round(1)
                
                st.markdown("👳 **거래 수입자 분석**")
                st.dataframe(partner_summary, use_container_width=True)
                
                st.markdown("---")
                
                # 거래 수입자 분석2 (수출자 분석 시에만 표시)
                partner_summary2 = filtered.groupby(['수입자', '선적항', '도착항']).agg({'컨테이너수': 'sum'}).reset_index()
                partner_summary2 = partner_summary2.sort_values(by='컨테이너수', ascending=False).reset_index(drop=True)
                partner_summary2['순위'] = range(1, len(partner_summary2) + 1)
                partner_summary2 = partner_summary2[['순위', '수입자', '선적항', '도착항', '컨테이너수']]
                
                st.markdown("👳 **거래 수입자 분석2**")
                st.dataframe(partner_summary2, use_container_width=True)
            else:
                # 수입자 분석 시 수출자 정보 표시
                partner_summary = filtered.groupby(['수출자', '수출자 대분류', '수출자 사업내용']).agg({'컨테이너수': 'sum'}).reset_index()
                partner_summary = partner_summary.sort_values(by='컨테이너수', ascending=False).reset_index(drop=True)
                partner_summary['순위'] = range(1, len(partner_summary) + 1)
                partner_summary = partner_summary[['순위', '수출자', '수출자 대분류', '수출자 사업내용', '컨테이너수']]
                
                # 비중(%) 계산
                total_containers_partner = partner_summary['컨테이너수'].sum()
                partner_summary['비중(%)'] = (partner_summary['컨테이너수'] / total_containers_partner * 100).round(1)
                
                st.markdown("🧑 **거래 수출자 분석**")
                st.dataframe(partner_summary, use_container_width=True)
                
                st.markdown("---")
                
                # 거래 수출자 분석2 (수입자 분석 시에만 표시)
                partner_summary2 = filtered.groupby(['수출자', '선적항', '도착항']).agg({'컨테이너수': 'sum'}).reset_index()
                partner_summary2 = partner_summary2.sort_values(by='컨테이너수', ascending=False).reset_index(drop=True)
                partner_summary2['순위'] = range(1, len(partner_summary2) + 1)
                partner_summary2 = partner_summary2[['순위', '수출자', '선적항', '도착항', '컨테이너수']]
                
                st.markdown("🧑 **거래 수출자 분석2**")
                st.dataframe(partner_summary2, use_container_width=True)
            
            st.markdown("---")
            
            # 컨테이너선사별 분석
            container_line_summary = filtered.groupby('컨테이너선사').agg({'컨테이너수': 'sum'}).reset_index()
            container_line_summary = container_line_summary.sort_values(by='컨테이너수', ascending=False).reset_index(drop=True)
            
            # 비중(%) 계산
            total_containers_for_pct = container_line_summary['컨테이너수'].sum()
            container_line_summary['비중(%)'] = (container_line_summary['컨테이너수'] / total_containers_for_pct * 100).round(1)
            
            st.markdown("🚢 **컨테이너선사별 분석**")
            st.dataframe(container_line_summary, use_container_width=True)

    if not st.session_state.has_search_results and not st.session_state.has_analysis_results:
        show_data_overview(df)

if __name__ == "__main__":
    app()