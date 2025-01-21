import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

# ページ設定
st.set_page_config(page_title="購買データ分析ダッシュボード", layout="wide")

# タイトル
st.title("購買データ分析ダッシュボード")

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_csv('data/sampledata.csv')
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
    
    # 年齢層を作成
    df['年齢層'] = pd.cut(df['年齢'], bins=[0, 20, 30, 40, 50, 60, 100], 
                        labels=['20歳未満', '20代', '30代', '40代', '50代', '60歳以上'])
    return df

df = load_data()

# サイドバー - 分析項目の選択
analysis_type = st.sidebar.selectbox(
    "分析項目を選択してください",
    ["地域別分析", "曜日別分析", "年齢層別分析", "性別分析"]
)

# メインコンテンツ
if analysis_type == "地域別分析":
    st.header("地域別分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("地域別平均購入金額")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df, x='地域', y='購入金額')
        plt.title('地域別平均購入金額')
        plt.xlabel('地域')
        plt.ylabel('平均購入金額（円）')
        st.pyplot(fig)
        
        # 統計情報
        region_stats = df.groupby('地域')['購入金額'].agg(['mean', 'count']).round(0)
        region_stats.columns = ['平均購入金額', '購入件数']
        st.dataframe(region_stats)
    
    with col2:
        st.subheader("地域×性別購入金額分布")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df, x='地域', y='購入金額', hue='性別')
        plt.title('地域・性別別購入金額分布')
        plt.xlabel('地域')
        plt.ylabel('購入金額（円）')
        st.pyplot(fig)

elif analysis_type == "曜日別分析":
    st.header("曜日別分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("曜日別平均購入金額")
        order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(data=df, x='曜日', y='購入金額', order=order)
        plt.title('曜日別購入金額分布')
        plt.xlabel('曜日')
        plt.ylabel('購入金額（円）')
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    with col2:
        st.subheader("地域・曜日別平均購入金額")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(data=df, x='曜日', y='購入金額', hue='地域', order=order)
        plt.title('地域・曜日別購入金額分布')
        plt.xlabel('曜日')
        plt.ylabel('購入金額（円）')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1))
        st.pyplot(fig)

elif analysis_type == "年齢層別分析":
    st.header("年齢層別分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("年齢層別平均購入金額")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df, x='年齢層', y='購入金額')
        plt.title('年齢層別購入金額分布')
        plt.xlabel('年齢層')
        plt.ylabel('購入金額（円）')
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # 統計情報
        age_stats = df.groupby('年齢層')['購入金額'].agg(['mean', 'count']).round(0)
        age_stats.columns = ['平均購入金額', '購入件数']
        st.dataframe(age_stats)
    
    with col2:
        st.subheader("地域・年齢層別購入金額分布")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df, x='年齢層', y='購入金額', hue='地域')
        plt.title('地域・年齢層別購入金額分布')
        plt.xlabel('年齢層')
        plt.ylabel('購入金額（円）')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1))
        st.pyplot(fig)

else:  # 性別分析
    st.header("性別分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("性別平均購入金額")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=df, x='性別', y='購入金額')
        plt.title('性別平均購入金額')
        plt.xlabel('性別')
        plt.ylabel('購入金額（円）')
        st.pyplot(fig)
        
        # 統計情報
        gender_stats = df.groupby('性別')['購入金額'].agg(['mean', 'count']).round(0)
        gender_stats.columns = ['平均購入金額', '購入件数']
        st.dataframe(gender_stats)
    
    with col2:
        st.subheader("性別・年齢層別購入金額分布")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df, x='年齢層', y='購入金額', hue='性別')
        plt.title('性別・年齢層別購入金額分布')
        plt.xlabel('年齢層')
        plt.ylabel('購入金額（円）')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1))
        st.pyplot(fig)

# フッター
st.markdown("---")
st.markdown("データ最終更新日: " + df['購入日'].max().strftime('%Y年%m月%d日')) 