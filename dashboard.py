import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib
from pathlib import Path

# ページ設定
st.set_page_config(
    page_title="購買データ分析ダッシュボード",
    layout="wide",
    initial_sidebar_state="expanded"
)

# データ読み込み用の関数
@st.cache_data
def load_data():
    DATA_PATH = Path(__file__).parent / "data" / "sampledata.csv"
    try:
        df = pd.read_csv(DATA_PATH, encoding='utf-8')
        df['購入日'] = pd.to_datetime(df['購入日'])
        df['曜日'] = df['購入日'].dt.day_name()
        
        # 曜日を日本語に変換
        weekday_mapping = {
            'Monday': '月曜日',
            'Tuesday': '火曜日',
            'Wednesday': '水曜日',
            'Thursday': '木曜日',
            'Friday': '金曜日',
            'Saturday': '土曜日',
            'Sunday': '日曜日'
        }
        df['曜日'] = df['曜日'].map(weekday_mapping)
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {str(e)}")
        return None

# タイトル
st.title("購買データ分析ダッシュボード")

# データ読み込み
df = load_data()

if df is not None:
    # サイドバー - 分析項目の選択
    analysis_type = st.sidebar.selectbox(
        "分析項目を選択してください",
        ["データ概要", "曜日別分析", "支払方法別分析"]
    )
    
    # メインコンテンツ
    if analysis_type == "データ概要":
        st.header("データ概要")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("データの最初の5行:")
            st.dataframe(df.head(), use_container_width=True)
        
        with col2:
            st.write("基本統計情報:")
            st.dataframe(df.describe(), use_container_width=True)
        
        st.write("データ期間:")
        st.write(f"開始日: {df['購入日'].min().strftime('%Y年%m月%d日')}")
        st.write(f"終了日: {df['購入日'].max().strftime('%Y年%m月%d日')}")
    
    elif analysis_type == "曜日別分析":
        st.header("曜日別分析")
        
        @st.cache_data
        def create_weekday_plots(df):
            order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
            
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=df, x='曜日', y='売上金額', order=order)
            plt.title('曜日別売上金額分布')
            plt.xlabel('曜日')
            plt.ylabel('売上金額（円）')
            plt.xticks(rotation=45)
            
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=df, x='曜日', y='数量', order=order)
            plt.title('曜日別販売数量分布')
            plt.xlabel('曜日')
            plt.ylabel('販売数量')
            plt.xticks(rotation=45)
            
            return fig1, fig2
        
        col1, col2 = st.columns(2)
        fig1, fig2 = create_weekday_plots(df)
        
        with col1:
            st.subheader("曜日別売上金額")
            st.pyplot(fig1)
            
            weekday_stats = df.groupby('曜日').agg({
                '売上金額': ['mean', 'count']
            }).round(0)
            weekday_stats.columns = ['平均売上金額', '取引件数']
            st.dataframe(weekday_stats, use_container_width=True)
        
        with col2:
            st.subheader("曜日別販売数量")
            st.pyplot(fig2)
    
    else:  # 支払方法別分析
        st.header("支払方法別分析")
        
        @st.cache_data
        def create_payment_plots(df):
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            sns.barplot(data=df, x='支払方法', y='売上金額')
            plt.title('支払方法別平均売上金額')
            plt.xlabel('支払方法')
            plt.ylabel('売上金額（円）')
            
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
            sns.boxplot(data=df, x='曜日', y='売上金額', hue='支払方法', order=order)
            plt.title('支払方法別・曜日別売上金額分布')
            plt.xlabel('曜日')
            plt.ylabel('売上金額（円）')
            plt.xticks(rotation=45)
            plt.legend(bbox_to_anchor=(1.05, 1))
            
            return fig1, fig2
        
        col1, col2 = st.columns(2)
        fig1, fig2 = create_payment_plots(df)
        
        with col1:
            st.subheader("支払方法別売上金額")
            st.pyplot(fig1)
            
            payment_stats = df.groupby('支払方法').agg({
                '売上金額': ['mean', 'count']
            }).round(0)
            payment_stats.columns = ['平均売上金額', '取引件数']
            st.dataframe(payment_stats, use_container_width=True)
        
        with col2:
            st.subheader("支払方法別・曜日別売上金額")
            st.pyplot(fig2)
    
    # フッター
    st.markdown("---")
    st.markdown(f"データ最終更新日: {df['購入日'].max().strftime('%Y年%m月%d日')}") 