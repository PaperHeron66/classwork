import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

file_path = r"C:\baidunetdiskdownload\案例1：收入趋势分析\案例1：收入趋势分析原始数据.xlsx"
df = pd.read_excel(file_path)

# ==========================================
# 分析 1：年度销售趋势分析
# ==========================================
yearly_sales = df.groupby('订单年份')['销售额'].sum().reset_index()

plt.figure(figsize=(8, 4))
plt.bar(yearly_sales['订单年份'].astype(str), yearly_sales['销售额'], color='steelblue')
plt.title('1、年度销售趋势分析')
plt.ylabel('销售额')
for i, v in enumerate(yearly_sales['销售额']):
    plt.text(i, v + 100000, f"{v/10000:.1f}万", ha='center') 
plt.show()

# ==========================================
# 分析 2：2020年月销售趋势分析
# ==========================================
df_2020 = df[df['订单年份'] == 2020]
monthly_2020 = df_2020.groupby('订单月份')['销售额'].sum().reset_index()

plt.figure(figsize=(10, 4))
plt.plot(monthly_2020['订单月份'], monthly_2020['销售额'], marker='o', color='coral')
plt.xticks(range(1, 13))
plt.title('2、2020年月销售趋势分析')
plt.ylabel('销售额')
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

# ==========================================
# 分析 3：2020年销售同比增长率趋势分析
# ==========================================
df_19_20 = df[df['订单年份'].isin([2019, 2020])]
pivot_month = df_19_20.pivot_table(index='订单月份', columns='订单年份', values='销售额', aggfunc='sum').fillna(0)
pivot_month['同比增长率'] = (pivot_month[2020] - pivot_month[2019]) / pivot_month[2019]

fig, ax1 = plt.subplots(figsize=(12, 5))
# 柱状图：2019和2020销售额
ax1.bar(pivot_month.index - 0.2, pivot_month[2019], width=0.4, label='2019年', color='lightgrey')
ax1.bar(pivot_month.index + 0.2, pivot_month[2020], width=0.4, label='2020年', color='skyblue')
ax1.set_ylabel('销售额')
ax1.set_xticks(range(1, 13))
ax1.legend(loc='upper left')

# 折线图：同比增长率
ax2 = ax1.twinx()
ax2.plot(pivot_month.index, pivot_month['同比增长率'], color='red', marker='s', label='同比增长率')
ax2.set_ylabel('同比增长率')
ax2.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
# 在 y=0 处画一条基准线
ax2.axhline(0, color='grey', linewidth=1, linestyle='--')
ax2.legend(loc='upper right')

plt.title('3、2020年销售同比增长率趋势分析')
plt.show()

# ==========================================
# 分析 4：2020年11月各省份同比增长情况分析
# ==========================================
df_nov = df[(df['订单年份'].isin([2019, 2020])) & (df['订单月份'] == 11)]
pivot_prov_nov = df_nov.pivot_table(index='销售省份', columns='订单年份', values='销售额', aggfunc='sum').fillna(0)
# 按2020年销售额降序排列
pivot_prov_nov = pivot_prov_nov.sort_values(by=2020, ascending=True)

plt.figure(figsize=(10, 8))
plt.barh(pivot_prov_nov.index, pivot_prov_nov[2019], color='lightgrey', label='2019年11月')
plt.barh(pivot_prov_nov.index, pivot_prov_nov[2020], color='steelblue', alpha=0.7, label='2020年11月')
plt.title('4、2020年11月各省份销售额对比分析')
plt.xlabel('销售额')
plt.legend()
plt.tight_layout()
plt.show()

# ==========================================
# 分析 5：2020年各销售省份同比增长情况分析(四川省为例)
# ==========================================
df_sc = df[(df['销售省份'] == '四川') & (df['订单年份'].isin([2019, 2020]))]
pivot_sc = df_sc.pivot_table(index='订单月份', columns='订单年份', values='销售额', aggfunc='sum').fillna(0)
pivot_sc['同比增长率'] = (pivot_sc[2020] - pivot_sc[2019]) / pivot_sc[2019]

fig, ax1 = plt.subplots(figsize=(10, 5))
# 将增长率改为画折线，避免极端数值（如3000%）的柱子破坏画面
ax1.plot(pivot_sc.index, pivot_sc['同比增长率'], color='orange', marker='^', label='同比增长率')
ax1.set_xticks(range(1, 13))
ax1.set_ylabel('同比增长率', color='darkorange')
ax1.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
ax1.tick_params(axis='y', labelcolor='darkorange')
ax1.axhline(0, color='grey', linewidth=1, linestyle='--')
ax1.legend(loc='upper left')

# 销售额画柱状图放在副轴
ax2 = ax1.twinx()
width = 0.3
ax2.bar(pivot_sc.index - width/2, pivot_sc[2019], width, label='2019年销售额', color='grey', alpha=0.6)
ax2.bar(pivot_sc.index + width/2, pivot_sc[2020], width, label='2020年销售额', color='steelblue', alpha=0.8)
ax2.set_ylabel('销售额 (元)')
ax2.legend(loc='upper right')

plt.title('5、四川省2019-2020年各月销售额及同比分析 ')
plt.tight_layout()
plt.show()