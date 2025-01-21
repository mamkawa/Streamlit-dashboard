import streamlit as st
import pandas as pd
import os

# ページ設定
st.set_page_config(page_title="購買データ分析ダッシュボード", layout="wide")

# タイトル
st.title("購買データ分析ダッシュボード")

# 現在のディレクトリとファイルの確認
st.write("現在のディレクトリ:")
st.write(os.getcwd())

st.write("ディレクトリの内容:")
try:
    files = os.listdir()
    st.write(files)
except Exception as e:
    st.error(f"ディレクトリ一覧エラー: {str(e)}")

st.write("dataディレクトリの内容:")
try:
    data_files = os.listdir('data')
    st.write(data_files)
except Exception as e:
    st.error(f"dataディレクトリ一覧エラー: {str(e)}")

# データ読み込み
try:
    df = pd.read_csv('data/sampledata.csv', encoding='utf-8')
    st.success("データ読み込み成功!")
    st.write("データの最初の5行:")
    st.write(df.head())
    st.write("データの列名:")
    st.write(df.columns.tolist())
except Exception as e:
    st.error(f"データ読み込みエラー: {str(e)}")

# サイドバー - 分析項目の選択
analysis_type = st.sidebar.selectbox(
    "分析項目を選択してください",
    ["曜日別分析", "支払方法別分析"]
)

# メインコンテンツ
if analysis_type == "曜日別分析":
    st.header("曜日別分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("曜日別平均売上金額")
        order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(data=df, x='曜日', y='売上金額', order=order)
        plt.title('曜日別売上金額分布')
        plt.xlabel('曜日')
        plt.ylabel('売上金額（円）')
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # 統計情報
        weekday_stats = df.groupby('曜日')['売上金額'].agg(['mean', 'count']).round(0)
        weekday_stats.columns = ['平均売上金額', '取引件数']
        st.dataframe(weekday_stats)
    
    with col2:
        st.subheader("曜日別販売数量")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(data=df, x='曜日', y='数量', order=order)
        plt.title('曜日別販売数量分布')
        plt.xlabel('曜日')
        plt.ylabel('販売数量')
        plt.xticks(rotation=45)
        st.pyplot(fig)

else:  # 支払方法別分析
    st.header("支払方法別分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("支払方法別平均売上金額")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=df, x='支払方法', y='売上金額')
        plt.title('支払方法別平均売上金額')
        plt.xlabel('支払方法')
        plt.ylabel('売上金額（円）')
        st.pyplot(fig)
        
        # 統計情報
        payment_stats = df.groupby('支払方法')['売上金額'].agg(['mean', 'count']).round(0)
        payment_stats.columns = ['平均売上金額', '取引件数']
        st.dataframe(payment_stats)
    
    with col2:
        st.subheader("支払方法別・曜日別売上金額分布")
        fig, ax = plt.subplots(figsize=(10, 6))
        order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
        sns.boxplot(data=df, x='曜日', y='売上金額', hue='支払方法', order=order)
        plt.title('支払方法別・曜日別売上金額分布')
        plt.xlabel('曜日')
        plt.ylabel('売上金額（円）')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1))
        st.pyplot(fig)

# フッター
st.markdown("---")
st.markdown("データ最終更新日: " + df['購入日'].max().strftime('%Y年%m月%d日')) 