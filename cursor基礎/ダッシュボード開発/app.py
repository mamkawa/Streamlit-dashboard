import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import japanize_matplotlib
import numpy as np
from datetime import datetime
import plotly.io as pio
import time
import base64
from io import BytesIO
import seaborn as sns
from scipy import stats

# テーマ設定
THEMES = {
    'デフォルト': {
        'colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
        'background': '#ffffff',
        'text': '#000000'
    },
    'ダーク': {
        'colors': ['#00ff00', '#ff0000', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'],
        'background': '#1f1f1f',
        'text': '#ffffff'
    },
    'パステル': {
        'colors': ['#ffb3ba', '#baffc9', '#bae1ff', '#ffffba', '#ffdfba', '#dbbae1'],
        'background': '#f8f9fa',
        'text': '#000000'
    }
}

# ページ設定
st.set_page_config(
    page_title="販売データ分析ダッシュボード",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
def get_custom_css(theme):
    return f"""
    <style>
    .main {{
        padding: 2rem;
        background-color: {theme['background']};
        color: {theme['text']};
    }}
    .stMetric {{
        background-color: {theme['background']};
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }}
    .css-1v0mbdj.e115fcil1 {{
        margin-top: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        background-color: {theme['background']};
    }}
    .css-1v0mbdj.e115fcil1:hover {{
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }}
    .download-button {{
        margin-top: 1rem;
        width: 100%;
    }}
    </style>
    """

# データの読み込みと前処理
@st.cache_data(ttl=3600)  # 1時間でキャッシュを更新
def load_data():
    df = pd.read_csv('data/sample-data.csv')
    df['purchase_date'] = pd.to_datetime(df['purchase_date'])
    return df

# グラフを画像として保存する関数
def get_image_download_link(fig, filename, text):
    img = fig.to_image(format="png")
    b64 = base64.b64encode(img).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">{text}</a>'
    return href

# 相関分析を行う関数
def analyze_correlations(df):
    numeric_cols = ['age', 'amount']
    corr = df[numeric_cols].corr()
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        text=np.round(corr.values, 2),
        texttemplate='%{text}',
        textfont={"size": 12},
        hoverongaps=False
    ))
    fig.update_layout(
        height=400,
        title='数値データの相関分析'
    )
    return fig

# RFM分析を行う関数
def perform_rfm_analysis(df):
    now = df['purchase_date'].max()
    rfm = df.groupby('customer_id').agg({
        'purchase_date': lambda x: (now - x.max()).days,  # Recency
        'customer_id': 'count',  # Frequency
        'amount': 'sum'  # Monetary
    }).rename(columns={
        'purchase_date': 'recency',
        'customer_id': 'frequency',
        'amount': 'monetary'
    })
    
    # スコアリング
    r_labels = range(4, 0, -1)
    r_quartiles = pd.qcut(rfm['recency'], q=4, labels=r_labels)
    f_labels = range(1, 5)
    f_quartiles = pd.qcut(rfm['frequency'], q=4, labels=f_labels)
    m_labels = range(1, 5)
    m_quartiles = pd.qcut(rfm['monetary'], q=4, labels=m_labels)
    
    rfm['R'] = r_quartiles
    rfm['F'] = f_quartiles
    rfm['M'] = m_quartiles
    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
    
    return rfm

# メイン処理
def main():
    # テーマ選択
    selected_theme = st.sidebar.selectbox(
        'テーマ選択',
        list(THEMES.keys()),
        help="ダッシュボードの表示テーマを選択"
    )
    
    # 選択されたテーマを適用
    st.markdown(get_custom_css(THEMES[selected_theme]), unsafe_allow_html=True)
    CUSTOM_COLORS = THEMES[selected_theme]['colors']
    
    # データの自動更新設定
    auto_refresh = st.sidebar.checkbox('データの自動更新（1分間隔）', help="チェックを入れると1分ごとにデータを更新します")
    if auto_refresh:
        time.sleep(60)
        st.experimental_rerun()

    # データの読み込みと更新日時の記録
    df = load_data()
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # サイドバーのフィルター
    st.sidebar.header('フィルター')

    # データ更新日時の表示
    st.sidebar.markdown(f"**データ更新日時:** {last_update}")

    # 日付範囲フィルター
    date_range = st.sidebar.date_input(
        "日付範囲",
        [df['purchase_date'].min(), df['purchase_date'].max()],
        min_value=df['purchase_date'].min().date(),
        max_value=df['purchase_date'].max().date(),
        help="分析対象期間を選択してください"
    )

    # カテゴリーフィルター
    categories = ['すべて'] + list(df['category'].unique())
    selected_category = st.sidebar.selectbox('カテゴリー', categories, help="商品カテゴリーでフィルタリング")

    # 性別フィルター
    genders = ['すべて'] + list(df['gender'].unique())
    selected_gender = st.sidebar.selectbox('性別', genders, help="顧客の性別でフィルタリング")

    # 地域フィルター
    regions = ['すべて'] + list(df['region'].unique())
    selected_region = st.sidebar.selectbox('地域', regions, help="販売地域でフィルタリング")

    # 支払方法フィルター
    payment_methods = ['すべて'] + list(df['payment_method'].unique())
    selected_payment = st.sidebar.selectbox('支払方法', payment_methods, help="支払方法でフィルタリング")

    # データのフィルタリング
    filtered_df = df.copy()

    # 日付フィルタリング
    filtered_df = filtered_df[
        (filtered_df['purchase_date'].dt.date >= date_range[0]) &
        (filtered_df['purchase_date'].dt.date <= date_range[1])
    ]

    if selected_category != 'すべて':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_gender != 'すべて':
        filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
    if selected_region != 'すべて':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    if selected_payment != 'すべて':
        filtered_df = filtered_df[filtered_df['payment_method'] == selected_payment]

    # メインページ
    st.title('販売データ分析ダッシュボード')

    # データダウンロードボタン
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 フィルタリングされたデータをダウンロード",
        data=csv,
        file_name=f'sales_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv',
        help="現在表示されているデータをCSVファイルとしてダウンロード"
    )

    # 1. 概要セクション
    st.header('1. 概要')
    col1, col2, col3, col4 = st.columns(4)

    # 前年同期比の計算（サンプルデータのため、実装は省略）
    previous_amount = filtered_df["amount"].sum() * 0.8  # サンプル用
    growth_rate = ((filtered_df["amount"].sum() - previous_amount) / previous_amount) * 100

    with col1:
        st.metric('総売上高', 
                  f'¥{filtered_df["amount"].sum():,.0f}',
                  f'{growth_rate:+.1f}%',
                  help="選択期間における総売上高と前年同期比")
    with col2:
        st.metric('総顧客数', 
                  f'{len(filtered_df):,}人',
                  help="選択期間における総顧客数")
    with col3:
        st.metric('平均購入金額', 
                  f'¥{filtered_df["amount"].mean():,.0f}',
                  help="選択期間における1件あたりの平均購入金額")
    with col4:
        st.metric('取引件数', 
                  f'{len(filtered_df):,}件',
                  help="選択期間における総取引件数")

    # カテゴリー別売上構成比（円グラフ）
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('カテゴリー別売上構成比')
        category_sales = filtered_df.groupby('category')['amount'].sum().reset_index()
        fig_pie = go.Figure(data=[go.Pie(
            labels=category_sales['category'],
            values=category_sales['amount'],
            hole=0.4,
            textinfo='label+percent',
            marker=dict(colors=CUSTOM_COLORS),
            hovertemplate="カテゴリー: %{label}<br>売上高: ¥%{value:,.0f}<br>構成比: %{percent}<extra></extra>"
        )])
        fig_pie.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader('地域別売上構成比')
        region_sales = filtered_df.groupby('region')['amount'].sum().reset_index()
        fig_region = go.Figure(data=[go.Pie(
            labels=region_sales['region'],
            values=region_sales['amount'],
            hole=0.4,
            textinfo='label+percent',
            marker=dict(colors=CUSTOM_COLORS),
            hovertemplate="地域: %{label}<br>売上高: ¥%{value:,.0f}<br>構成比: %{percent}<extra></extra>"
        )])
        fig_region.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_region, use_container_width=True)

    # 2. 顧客基本分析
    st.header('2. 顧客基本分析')
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('年齢分布')
        fig_age = go.Figure(data=[go.Histogram(
            x=filtered_df['age'],
            nbinsx=20,
            name='年齢分布',
            marker=dict(color=CUSTOM_COLORS[0]),
            hovertemplate="年齢: %{x}歳<br>人数: %{y}人<extra></extra>"
        )])
        fig_age.update_layout(
            height=400,
            margin=dict(t=30, b=0, l=0, r=0),
            xaxis_title='年齢',
            yaxis_title='人数'
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with col2:
        st.subheader('性別分布')
        gender_counts = filtered_df['gender'].value_counts()
        fig_gender = go.Figure(data=[go.Pie(
            labels=gender_counts.index,
            values=gender_counts.values,
            hole=0.4,
            textinfo='label+percent',
            marker=dict(colors=CUSTOM_COLORS),
            hovertemplate="性別: %{label}<br>人数: %{value}人<br>構成比: %{percent}<extra></extra>"
        )])
        fig_gender.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=30, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_gender, use_container_width=True)

    # 年齢層別購買金額分布（箱ひげ図）
    st.subheader('年齢層別購買金額分布')
    filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=[0, 20, 30, 40, 50, 60, 100], 
                        labels=['20歳未満', '20代', '30代', '40代', '50代', '60歳以上'])
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(
        x=filtered_df['age_group'],
        y=filtered_df['amount'],
        name='購買金額',
        marker=dict(color=CUSTOM_COLORS[0]),
        hovertemplate="年齢層: %{x}<br>購入金額: ¥%{y:,.0f}<extra></extra>"
    ))
    fig_box.update_layout(
        height=400,
        margin=dict(t=30, b=0, l=0, r=0),
        xaxis_title='年齢層',
        yaxis_title='購入金額'
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # 3. カテゴリー基本分析
    st.header('3. カテゴリー基本分析')

    # カテゴリー別売上推移（折れ線グラフ）
    st.subheader('カテゴリー別売上推移')
    daily_sales = filtered_df.groupby(['purchase_date', 'category'])['amount'].sum().reset_index()
    fig_line = go.Figure()
    for i, category in enumerate(daily_sales['category'].unique()):
        category_data = daily_sales[daily_sales['category'] == category]
        fig_line.add_trace(go.Scatter(
            x=category_data['purchase_date'],
            y=category_data['amount'],
            name=category,
            mode='lines+markers',
            line=dict(color=CUSTOM_COLORS[i % len(CUSTOM_COLORS)]),
            hovertemplate="日付: %{x}<br>売上高: ¥%{y:,.0f}<extra></extra>"
        ))
    fig_line.update_layout(
        height=400,
        margin=dict(t=30, b=0, l=0, r=0),
        xaxis_title='日付',
        yaxis_title='売上金額',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # カテゴリー別・支払方法別分析
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('カテゴリー別平均購入金額')
        category_avg = filtered_df.groupby('category')['amount'].mean().reset_index()
        fig_bar = go.Figure(data=[go.Bar(
            x=category_avg['category'],
            y=category_avg['amount'],
            text=category_avg['amount'].round().astype(int),
            textposition='auto',
            marker=dict(color=CUSTOM_COLORS[0]),
            hovertemplate="カテゴリー: %{x}<br>平均購入金額: ¥%{y:,.0f}<extra></extra>"
        )])
        fig_bar.update_layout(
            height=400,
            margin=dict(t=30, b=0, l=0, r=0),
            xaxis_title='カテゴリー',
            yaxis_title='平均購入金額'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader('支払方法別構成比')
        payment_counts = filtered_df['payment_method'].value_counts()
        fig_payment = go.Figure(data=[go.Pie(
            labels=payment_counts.index,
            values=payment_counts.values,
            hole=0.4,
            textinfo='label+percent',
            marker=dict(colors=CUSTOM_COLORS),
            hovertemplate="支払方法: %{label}<br>件数: %{value}件<br>構成比: %{percent}<extra></extra>"
        )])
        fig_payment.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=30, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_payment, use_container_width=True)

    # 4. データテーブル
    st.header('4. データテーブル')
    st.dataframe(
        filtered_df.style.format({
            'amount': '¥{:,.0f}',
            'purchase_date': lambda x: x.strftime('%Y-%m-%d')
        }),
        height=400
    )

    # 新しい分析セクション
    st.header('5. 詳細分析')
    
    # 相関分析
    st.subheader('相関分析')
    corr_fig = analyze_correlations(filtered_df)
    st.plotly_chart(corr_fig, use_container_width=True)
    
    # グラフの保存ボタン
    st.markdown(get_image_download_link(corr_fig, '相関分析.png', '📥 相関分析グラフをダウンロード'), unsafe_allow_html=True)
    
    # RFM分析
    st.subheader('RFM分析')
    rfm = perform_rfm_analysis(filtered_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write('RFMスコア分布')
        rfm_counts = rfm['RFM_Score'].value_counts().head(10)
        fig_rfm = go.Figure(data=[go.Bar(
            x=rfm_counts.index,
            y=rfm_counts.values,
            marker=dict(color=CUSTOM_COLORS[0])
        )])
        fig_rfm.update_layout(
            height=400,
            xaxis_title='RFMスコア',
            yaxis_title='顧客数'
        )
        st.plotly_chart(fig_rfm, use_container_width=True)
    
    with col2:
        st.write('顧客セグメント別平均値')
        rfm_summary = rfm.groupby('RFM_Score').agg({
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': 'mean'
        }).round(2)
        st.dataframe(rfm_summary)

    # データのダウンロードオプション
    st.header('6. データエクスポート')
    col1, col2 = st.columns(2)
    
    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 分析データをCSVでダウンロード",
            data=csv,
            file_name=f'sales_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )
    
    with col2:
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, sheet_name='販売データ', index=False)
            rfm.to_excel(writer, sheet_name='RFM分析', index=True)
        excel_data = excel_buffer.getvalue()
        
        st.download_button(
            label="📥 詳細レポートをExcelでダウンロード",
            data=excel_data,
            file_name=f'sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == '__main__':
    main() 