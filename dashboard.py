import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import matplotlib as mpl

# キャッシュの設定
st.set_page_config(
    page_title="購買データ分析ダッシュボード",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 日本語フォントの設定
plt.rcParams['font.family'] = 'MS Gothic'

# データ読み込み用の関数
@st.cache_data(ttl=3600)
def load_data():
    DATA_PATH = Path(__file__).parent / "data" / "sampledata.csv"
    try:
        df = pd.read_csv(DATA_PATH, encoding='utf-8', parse_dates=['購入日'])
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {str(e)}")
        return None

# データの前処理
@st.cache_data(ttl=3600)
def preprocess_data(df):
    if df is None:
        return None
    
    df = df.copy()
    df['曜日'] = df['購入日'].dt.day_name()
    df['年'] = df['購入日'].dt.year
    df['月'] = df['購入日'].dt.month
    df['日'] = df['購入日'].dt.day
    
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

# タイトル
st.title("購買データ分析ダッシュボード")

# データ読み込みと前処理
df = load_data()
df = preprocess_data(df)

if df is not None:
    # サイドバー - フィルター
    st.sidebar.header("フィルター設定")
    
    # 日付フィルター
    st.sidebar.subheader("期間選択")
    min_date = df['購入日'].min()
    max_date = df['購入日'].max()
    selected_date = st.sidebar.date_input(
        "日付を選択",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # エリアフィルター
    st.sidebar.subheader("エリア選択")
    areas = sorted(df['地域'].unique())
    selected_areas = st.sidebar.multiselect("地域", areas, default=areas)
    
    # 性別フィルター
    st.sidebar.subheader("性別選択")
    genders = sorted(df['性別'].unique())
    selected_genders = st.sidebar.multiselect("性別", genders, default=genders)
    
    # 年代フィルター
    st.sidebar.subheader("年代選択")
    age_groups = sorted(df['年代'].unique())
    selected_age_groups = st.sidebar.multiselect("年代", age_groups, default=age_groups)
    
    # データのフィルタリング
    filtered_df = df[
        (df['購入日'].dt.date == selected_date) &
        (df['地域'].isin(selected_areas)) &
        (df['性別'].isin(selected_genders)) &
        (df['年代'].isin(selected_age_groups))
    ]
    
    # 分析タイプの選択
    analysis_type = st.sidebar.selectbox(
        "分析項目を選択してください",
        ["データ概要", "曜日別分析", "支払方法別分析"]
    )
    
    # メインコンテンツ
    if analysis_type == "データ概要":
        st.header("データ概要")
        
        # 選択されたデータの概要
        st.subheader("フィルター適用後のデータ概要")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        with metrics_col1:
            st.metric("データ件数", f"{len(filtered_df):,}件")
        with metrics_col2:
            st.metric("合計売上金額", f"¥{filtered_df['売上金額'].sum():,.0f}")
        with metrics_col3:
            st.metric("平均売上金額", f"¥{filtered_df['売上金額'].mean():,.0f}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("データの最初の5行:")
            st.dataframe(filtered_df.head(), use_container_width=True)
        
        with col2:
            st.write("基本統計情報:")
            st.dataframe(filtered_df.describe(), use_container_width=True)
    
    elif analysis_type == "曜日別分析":
        st.header("曜日別分析")
        
        @st.cache_data(ttl=3600)
        def create_weekday_plots(df):
            if len(df) == 0:
                return None, None
                
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
        
        if len(filtered_df) > 0:
            col1, col2 = st.columns(2)
            fig1, fig2 = create_weekday_plots(filtered_df)
            
            if fig1 is not None and fig2 is not None:
                with col1:
                    st.subheader("曜日別売上金額")
                    st.pyplot(fig1)
                    
                    weekday_stats = filtered_df.groupby('曜日').agg({
                        '売上金額': ['mean', 'count']
                    }).round(0)
                    weekday_stats.columns = ['平均売上金額', '取引件数']
                    st.dataframe(weekday_stats, use_container_width=True)
                
                with col2:
                    st.subheader("曜日別販売数量")
                    st.pyplot(fig2)
        else:
            st.warning("選択された条件に該当するデータがありません。")
    
    else:  # 支払方法別分析
        st.header("支払方法別分析")
        
        @st.cache_data(ttl=3600)
        def create_payment_plots(df):
            if len(df) == 0:
                return None, None
                
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
        
        if len(filtered_df) > 0:
            col1, col2 = st.columns(2)
            fig1, fig2 = create_payment_plots(filtered_df)
            
            if fig1 is not None and fig2 is not None:
                with col1:
                    st.subheader("支払方法別売上金額")
                    st.pyplot(fig1)
                    
                    payment_stats = filtered_df.groupby('支払方法').agg({
                        '売上金額': ['mean', 'count']
                    }).round(0)
                    payment_stats.columns = ['平均売上金額', '取引件数']
                    st.dataframe(payment_stats, use_container_width=True)
                
                with col2:
                    st.subheader("支払方法別・曜日別売上金額")
                    st.pyplot(fig2)
        else:
            st.warning("選択された条件に該当するデータがありません。")
    
    # フッター
    st.markdown("---")
    st.markdown(f"データ最終更新日: {filtered_df['購入日'].max().strftime('%Y年%m月%d日')}") 