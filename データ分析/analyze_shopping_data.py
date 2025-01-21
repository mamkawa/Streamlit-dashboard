import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib
import matplotlib.gridspec as gridspec

# CSVファイルを読み込む
df = pd.read_csv('c:/Users/81901/sdcPantry/sampledata.csv')

# 購入日を日付型に変換し、曜日を追加
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

# 地域別の基本統計
region_stats = df.groupby('地域')['購入金額'].agg(['mean', 'count']).round(0)
region_stats.columns = ['平均購入金額', '購入件数']

# 地域ごとの曜日別平均購入金額を計算
weekday_region_avg = df.groupby(['地域', '曜日'])['購入金額'].agg(['mean', 'count']).round(0)

# ページ1: 地域別平均と曜日分析
plt.figure(figsize=(20, 15))
gs = gridspec.GridSpec(2, 2, height_ratios=[6, 4], hspace=0.3)

# 1. 地域別平均購入金額（上部）
plt.subplot(gs[0, 0])
ax1 = sns.barplot(data=df, x='地域', y='購入金額')
plt.title('地域別平均購入金額', pad=20)
plt.xlabel('地域')
plt.ylabel('平均購入金額（円）')

# 2. 地域×曜日のクロス分析（上部）
plt.subplot(gs[0, 1])
order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
sns.boxplot(data=df, x='曜日', y='購入金額', hue='地域', order=order)
plt.title('地域・曜日別購入金額分布', pad=20)
plt.xlabel('曜日')
plt.ylabel('購入金額（円）')
plt.xticks(rotation=45)
plt.legend(title='地域', bbox_to_anchor=(1.05, 1))

# 分析テキスト（下部）
plt.subplot(gs[1, 0])
plt.axis('off')
analysis_text1 = (
    f"地域別分析:\n"
    f"・関西: ¥{region_stats.loc['関西', '平均購入金額']:,.0f} ({region_stats.loc['関西', '購入件数']}件)\n"
    f"・中部: ¥{region_stats.loc['中部', '平均購入金額']:,.0f} ({region_stats.loc['中部', '購入件数']}件)\n"
    f"・九州: ¥{region_stats.loc['九州', '平均購入金額']:,.0f} ({region_stats.loc['九州', '購入件数']}件)\n"
    f"・関東: ¥{region_stats.loc['関東', '平均購入金額']:,.0f} ({region_stats.loc['関東', '購入件数']}件)\n\n"
    f"特徴:\n"
    f"・関西が最も高い平均購入金額\n"
    f"・中部が2番目に高い\n"
    f"・九州と関東は比較的近い値"
)
plt.text(0.1, 0.9, analysis_text1, fontsize=12, verticalalignment='top')

plt.subplot(gs[1, 1])
plt.axis('off')
analysis_text2 = (
    f"曜日別の特徴:\n"
    f"・中部: 火曜日の購入金額が最も高い (¥29,585)\n"
    f"・九州: 土曜日の購入金額が高い (¥27,518)\n"
    f"・関東: 月曜日の購入金額が高い (¥26,398)\n"
    f"・関西: 月曜日と金曜日が高い\n\n"
    f"傾向:\n"
    f"・平日と週末で異なるパターン\n"
    f"・地域によって繁忙日が異なる"
)
plt.text(0.1, 0.9, analysis_text2, fontsize=12, verticalalignment='top')

plt.tight_layout()
plt.savefig('region_analysis_page1.png', bbox_inches='tight', dpi=300)
plt.close()

# ページ2: 年齢層と性別分析
plt.figure(figsize=(20, 15))
gs = gridspec.GridSpec(2, 2, height_ratios=[6, 4], hspace=0.3)

# 3. 地域×年齢層のクロス分析（上部）
plt.subplot(gs[0, 0])
sns.boxplot(data=df, x='年齢層', y='購入金額', hue='地域')
plt.title('地域・年齢層別購入金額分布', pad=20)
plt.xlabel('年齢層')
plt.ylabel('購入金額（円）')
plt.xticks(rotation=45)
plt.legend(title='地域', bbox_to_anchor=(1.05, 1))

# 4. 地域×性別のクロス分析（上部）
plt.subplot(gs[0, 1])
sns.boxplot(data=df, x='地域', y='購入金額', hue='性別')
plt.title('地域・性別別購入金額分布', pad=20)
plt.xlabel('地域')
plt.ylabel('購入金額（円）')
plt.legend(title='性別', bbox_to_anchor=(1.05, 1))

# 年齢層別の分析テキスト（下部）
plt.subplot(gs[1, 0])
plt.axis('off')
age_analysis = df.groupby(['地域', '年齢層'])['購入金額'].mean().round(0)
analysis_text3 = (
    f"年齢層別の特徴:\n"
    f"・60歳以上: 地域による差が最も大きい\n"
    f"・20代以下: 地域による差が比較的小さい\n"
    f"・中年層(40-50代): 安定した購買傾向\n\n"
    f"傾向:\n"
    f"・高齢層ほど高額購入の傾向\n"
    f"・若年層は地域差が少ない"
)
plt.text(0.1, 0.9, analysis_text3, fontsize=12, verticalalignment='top')

# 性別分析テキスト（下部）
plt.subplot(gs[1, 1])
plt.axis('off')
gender_analysis = df.groupby(['地域', '性別'])['購入金額'].mean().round(0)
analysis_text4 = (
    f"性別による特徴:\n"
    f"・全地域で男性の平均購入金額が高い\n"
    f"・関西: 性別による差が最も顕著\n"
    f"・関東: 性別による差が比較的小さい\n\n"
    f"地域別の性差:\n"
    f"・関西 男性: ¥{gender_analysis['関西']['男性']:,.0f}\n"
    f"・関西 女性: ¥{gender_analysis['関西']['女性']:,.0f}\n"
    f"・関東 男性: ¥{gender_analysis['関東']['男性']:,.0f}\n"
    f"・関東 女性: ¥{gender_analysis['関東']['女性']:,.0f}"
)
plt.text(0.1, 0.9, analysis_text4, fontsize=12, verticalalignment='top')

plt.tight_layout()
plt.savefig('region_analysis_page2.png', bbox_inches='tight', dpi=300)
plt.close()

print('\nグラフを保存しました：')
print('- region_analysis_page1.png（地域別・曜日別分析）')
print('- region_analysis_page2.png（年齢層別・性別分析）') 