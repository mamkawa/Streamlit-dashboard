import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# ページ設定
st.set_page_config(
    page_title="購買データ分析ダッシュボード",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 日本語フォントの設定
plt.rcParams['font.family'] = ['MS Gothic', 'DejaVu Sans']

# データ読み込み用の関数
@st.cache_data
def load_data():
    try:
        # データファイルのパスを指定（複数のパターンを試行）
        possible_paths = [
            "sample-data.csv",  # リポジトリのルートディレクトリ
            "./sample-data.csv",  # 現在のディレクトリ
            "./data/sample-data.csv",  # dataディレクトリ
            "../sample-data.csv",  # 1階層上
            os.path.join(os.path.dirname(__file__), "sample-data.csv")  # スクリプトと同じディレクトリ
        ]
        
        df = None
        used_path = None
        
        # 現在のディレクトリとファイル一覧を表示（デバッグ用）
        st.write("現在のディレクトリ:", os.getcwd())
        st.write("ディレクトリ内のファイル:", os.listdir())
        
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    st.write(f"ファイルが見つかりました: {path}")
                    df = pd.read_csv(path, encoding='utf-8')
                    used_path = path
                    break
            except Exception as e:
                st.write(f"パス {path} でエラー: {str(e)}")
                continue
        
        if df is None:
            st.error("データファイルが見つかりません。")
            st.write("試行したパス:")
            for path in possible_paths:
                st.write(f"- {path}")
            return None
            
        # カラム名を表示（デバッグ用）
        st.write("データのカラム:", df.columns.tolist())
        
        # 日付の変換
        df['購入日'] = pd.to_datetime(df['購入日'])
        
        # 曜日の追加
        df['曜日'] = df['購入日'].dt.day_name().map({
            'Monday': '月曜日',
            'Tuesday': '火曜日',
            'Wednesday': '水曜日',
            'Thursday': '木曜日',
            'Friday': '金曜日',
            'Saturday': '土曜日',
            'Sunday': '日曜日'
        })
        
        # 売上金額の計算（売上金額がない場合は単価×数量で計算）
        if '売上金額' not in df.columns and '売上金' not in df.columns:
            df['売上金額'] = df['単価'] * df['数量']
        elif '売上金' in df.columns:
            df['売上金額'] = df['売上金']
        
        st.success(f"データ読み込み成功! 使用したパス: {used_path}")
        return df
        
    except Exception as e:
        st.error(f"データ読み込みエラー: {str(e)}")
        return None

# タイトル
st.title("購買データ分析ダッシュボード")

# データ読み込み
df = load_data()

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
    
    try:
        # データのフィルタリング（日付のみ）
        filtered_df = df[df['購入日'].dt.date == selected_date]
        
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
                numeric_cols = filtered_df.select_dtypes(include=['int64', 'float64']).columns
                st.dataframe(filtered_df[numeric_cols].describe(), use_container_width=True)
        
        elif analysis_type == "曜日別分析":
            st.header("曜日別分析")
            
            if len(filtered_df) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("曜日別売上金額")
                    fig1 = plt.figure(figsize=(10, 6))
                    order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
                    sns.boxplot(data=filtered_df, x='曜日', y='売上金額', order=order)
                    plt.title('曜日別売上金額分布')
                    plt.xlabel('曜日')
                    plt.ylabel('売上金額（円）')
                    plt.xticks(rotation=45)
                    st.pyplot(fig1)
                    
                    weekday_stats = filtered_df.groupby('曜日').agg({
                        '売上金額': ['mean', 'count']
                    }).round(0)
                    weekday_stats.columns = ['平均売上金額', '取引件数']
                    st.dataframe(weekday_stats, use_container_width=True)
                
                with col2:
                    st.subheader("曜日別販売数量")
                    fig2 = plt.figure(figsize=(10, 6))
                    sns.boxplot(data=filtered_df, x='曜日', y='数量', order=order)
                    plt.title('曜日別販売数量分布')
                    plt.xlabel('曜日')
                    plt.ylabel('販売数量')
                    plt.xticks(rotation=45)
                    st.pyplot(fig2)
            else:
                st.warning("選択された条件に該当するデータがありません。")
        
        else:  # 支払方法別分析
            st.header("支払方法別分析")
            
            if len(filtered_df) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("支払方法別売上金額")
                    fig1 = plt.figure(figsize=(8, 6))
                    sns.barplot(data=filtered_df, x='支払方法', y='売上金額')
                    plt.title('支払方法別平均売上金額')
                    plt.xlabel('支払方法')
                    plt.ylabel('売上金額（円）')
                    st.pyplot(fig1)
                    
                    payment_stats = filtered_df.groupby('支払方法').agg({
                        '売上金額': ['mean', 'count']
                    }).round(0)
                    payment_stats.columns = ['平均売上金額', '取引件数']
                    st.dataframe(payment_stats, use_container_width=True)
                
                with col2:
                    st.subheader("支払方法別・曜日別売上金額")
                    fig2 = plt.figure(figsize=(10, 6))
                    order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
                    sns.boxplot(data=filtered_df, x='曜日', y='売上金額', hue='支払方法', order=order)
                    plt.title('支払方法別・曜日別売上金額分布')
                    plt.xlabel('曜日')
                    plt.ylabel('売上金額（円）')
                    plt.xticks(rotation=45)
                    plt.legend(bbox_to_anchor=(1.05, 1))
                    st.pyplot(fig2)
            else:
                st.warning("選択された条件に該当するデータがありません。")
        
        # フッター
        st.markdown("---")
        st.markdown(f"データ最終更新日: {filtered_df['購入日'].max().strftime('%Y年%m月%d日')}")
    except Exception as e:
        st.error(f"フィルター処理でエラーが発生しました: {str(e)}")
        st.write("利用可能なカラム:", df.columns.tolist())
else:
    st.error("データの読み込みに失敗しました。") 