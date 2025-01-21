import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

# 警告を無視
warnings.filterwarnings('ignore')

# ページ設定
st.set_page_config(
    page_title="購買データ分析ダッシュボード",
    layout="wide",
    initial_sidebar_state="expanded"
)

# プロットの基本設定
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica', 'Yu Gothic', 'Meiryo'],
    'axes.unicode_minus': False,
    'figure.subplot.left': 0.15,
    'figure.subplot.right': 0.95,
    'figure.subplot.bottom': 0.15,
    'figure.subplot.top': 0.95,
    'font.size': 10
})

def create_figure(figsize=(10, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.tick_params(labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    return fig, ax

def format_axis_labels(ax, xlabel, ylabel, title):
    """軸ラベルとタイトルを設定する関数"""
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=12, pad=15)
    plt.tight_layout()

@st.cache_data
def load_data():
    try:
        # データファイルの場所を特定
        file_path = "data/sample-data.csv"
        
        if not os.path.exists(file_path):
            st.error(f"ファイルが見つかりません: {file_path}")
            # 現在のディレクトリ情報を表示
            st.write("現在のディレクトリ:", os.getcwd())
            st.write("ファイル一覧:")
            for root, dirs, files in os.walk("."):
                st.write(f"Directory: {root}")
                for file in files:
                    st.write(f"  - {file}")
            return None
            
        # データの読み込みと前処理
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # カラム名の確認と表示
        st.write("読み込んだデータのカラム:", df.columns.tolist())
        
        # 必須カラムの存在確認
        required_columns = ['購入日']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"必要なカラムが見つかりません: {missing_columns}")
            return None
        
        # 日付の変換
        df['購入日'] = pd.to_datetime(df['購入日'])
        df['年月'] = df['購入日'].dt.strftime('%Y/%m')
        df['曜日'] = df['購入日'].dt.day_name().map({
            'Monday': '月曜日', 'Tuesday': '火曜日', 'Wednesday': '水曜日',
            'Thursday': '木曜日', 'Friday': '金曜日', 'Saturday': '土曜日',
            'Sunday': '日曜日'
        })
        
        # 売上金額の設定
        if '購入金額' in df.columns:
            df['売上金額'] = df['購入金額']
        elif '売上金額' not in df.columns:
            if '売上金' in df.columns:
                df['売上金額'] = df['売上金']
            elif '売上' in df.columns:
                df['売上金額'] = df['売上']
            else:
                st.error("売上金額を計算するために必要なカラムが見つかりません。")
                st.write("必要なカラム: '売上金額'、'購入金額'、'売上金'、または '売上'")
                return None
        
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {str(e)}")
        return None

@st.cache_data
def create_summary_metrics(df):
    return {
        "データ件数": f"{len(df):,}件",
        "合計売上金額": f"¥{df['売上金額'].sum():,.0f}",
        "平均売上金額": f"¥{df['売上金額'].mean():,.0f}"
    }

@st.cache_data
def create_weekday_stats(df):
    return df.groupby('曜日').agg({
        '売上金額': ['mean', 'count']
    }).round(0)

@st.cache_data
def create_payment_stats(df):
    return df.groupby('支払方法').agg({
        '売上金額': ['mean', 'count']
    }).round(0)

# メインアプリケーション
def main():
    st.title("購買データ分析ダッシュボード")
    
    df = load_data()
    if df is None:
        st.error("データの読み込みに失敗しました。")
        return

    # サイドバー設定
    st.sidebar.header("フィルター設定")
    st.sidebar.subheader("期間選択")
    
    available_months = sorted(df['年月'].unique())
    selected_month = st.sidebar.selectbox(
        "年月を選択",
        available_months,
        index=len(available_months)-1
    )
    
    analysis_type = st.sidebar.selectbox(
        "分析項目を選択してください",
        ["データ概要", "曜日別分析", "支払方法別分析"]
    )

    try:
        filtered_df = df[df['年月'] == selected_month]
        
        if len(filtered_df) == 0:
            st.warning("選択された条件に該当するデータがありません。")
            return

        if analysis_type == "データ概要":
            st.header("データ概要")
            metrics = create_summary_metrics(filtered_df)
            
            cols = st.columns(3)
            for col, (label, value) in zip(cols, metrics.items()):
                col.metric(label, value)
            
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
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("曜日別売上金額")
                fig1, ax1 = create_figure()
                order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
                sns.boxplot(data=filtered_df, x='曜日', y='売上金額', order=order, ax=ax1)
                format_axis_labels(ax1, '曜日', '売上金額（円）', '曜日別売上金額分布')
                plt.xticks(rotation=45)
                st.pyplot(fig1)
                
                weekday_stats = create_weekday_stats(filtered_df)
                weekday_stats.columns = ['平均売上金額', '取引件数']
                st.dataframe(weekday_stats, use_container_width=True)
            
            with col2:
                st.subheader("曜日別販売数量")
                fig2, ax2 = create_figure()
                sns.boxplot(data=filtered_df, x='曜日', y='数量', order=order, ax=ax2)
                format_axis_labels(ax2, '曜日', '販売数量', '曜日別販売数量分布')
                plt.xticks(rotation=45)
                st.pyplot(fig2)

        else:  # 支払方法別分析
            st.header("支払方法別分析")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("支払方法別売上金額")
                fig1, ax1 = create_figure(figsize=(8, 6))
                sns.barplot(data=filtered_df, x='支払方法', y='売上金額', ax=ax1)
                format_axis_labels(ax1, '支払方法', '売上金額（円）', '支払方法別平均売上金額')
                st.pyplot(fig1)
                
                payment_stats = create_payment_stats(filtered_df)
                payment_stats.columns = ['平均売上金額', '取引件数']
                st.dataframe(payment_stats, use_container_width=True)
            
            with col2:
                st.subheader("支払方法別・曜日別売上金額")
                fig2, ax2 = create_figure()
                order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
                sns.boxplot(data=filtered_df, x='曜日', y='売上金額', hue='支払方法', order=order, ax=ax2)
                format_axis_labels(ax2, '曜日', '売上金額（円）', '支払方法別・曜日別売上金額分布')
                plt.xticks(rotation=45)
                plt.legend(bbox_to_anchor=(1.05, 1), fontsize=8, prop={'family': 'IPAexGothic'})
                st.pyplot(fig2)

        st.markdown("---")
        st.markdown(f"データ最終更新日: {filtered_df['購入日'].max().strftime('%Y年%m月%d日')}")

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main() 