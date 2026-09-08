# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def extract_data(df):
    for idx in range(len(df)):
        if df.iloc[idx].notna().any():
            header_idx = idx
            break
    else:
        return None, None
    raw_header = df.iloc[header_idx].values
    data_df = df.iloc[header_idx+1:].reset_index(drop=True)
    data_df = data_df.dropna(axis=1, how='all')
    cols = []
    for i, val in enumerate(raw_header[:len(data_df.columns)]):
        if pd.notna(val) and str(val).strip() != '':
            cols.append(str(val).strip())
        else:
            cols.append(f'col_{i}')
    data_df.columns = cols
    data_df = data_df.dropna(how='all')
    return cols, data_df

def plot_gradient_bar(name, data_df):
    """1 渐变柱形图"""
    x = data_df.iloc[:, 0]
    y = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(x)))
    ax.bar(x, y, color=colors)
    ax.set_title('渐变柱形图')
    ax.set_ylabel('销售量')
    plt.tight_layout()
    plt.show()
    
def plot_mean_bar(name, data_df):
    """2 带均值柱形图"""
    categories = data_df.iloc[:, 0].astype(str) 
    values = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    mean_val = values.mean()   
    fig, ax = plt.subplots(figsize=(8,5))
    bars = ax.bar(categories, values, color='skyblue')
    if not np.isnan(mean_val):
        ax.axhline(y=mean_val, color='red', linestyle='--', label=f'均值 {mean_val:.0f}')
        ax.legend() 
    ax.set_title('带均值柱形图')
    ax.set_ylabel('销售量')
    ax.set_xticklabels(categories, rotation=0)
    plt.tight_layout()
    plt.show()

def plot_rounded_bar(name, data_df):
    """3 渐变圆角柱形图"""
    x = data_df.iloc[:, 0]
    y = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    colors = plt.cm.Oranges(np.linspace(0.4, 0.9, len(x)))
    ax.bar(x, y, color=colors, width=0.5)
    ax.set_title('渐变圆角柱形图')
    ax.set_ylabel('销量')
    plt.tight_layout()
    plt.show()

def plot_annotated_bar(name, data_df):
    """4 标注柱形图"""
    x = data_df.iloc[:, 0]
    y = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    bars = ax.bar(x, y, color='teal')
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.0f}', xy=(bar.get_x()+bar.get_width()/2, height),
                    xytext=(0,3), textcoords="offset points", ha='center', va='bottom')
    ax.set_title('标注柱形图')
    ax.set_ylabel('销量')
    plt.tight_layout()
    plt.show()

def plot_stacked_bar(name, data_df):
    """5 层叠柱形图"""
    x = data_df.iloc[:, 0]
    y1 = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    y2 = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(x, y1, label='销售额', color='#1f77b4')
    ax.bar(x, y2, bottom=y1, label='利润额', color='#ff7f0e')
    ax.legend()
    ax.set_title('层叠柱形图')
    ax.set_ylabel('金额')
    plt.tight_layout()
    plt.show()

def plot_butterfly(name, data_df):
    """6 蝴蝶图"""
    regions = data_df.iloc[:, 0]
    left_vals = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    right_vals = pd.to_numeric(data_df.iloc[:, 4], errors='coerce')
    y_pos = np.arange(len(regions))
    fig, ax = plt.subplots(figsize=(10,6))
    ax.barh(y_pos, -left_vals, color='#1f77b4', label='2022')
    ax.barh(y_pos, right_vals, color='#ff7f0e', label='2021')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(regions)
    ax.set_xlabel('销量')
    ax.set_title('蝴蝶图')
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_butterfly_text(name, data_df):
    """7 蝴蝶图（文本）"""
    regions = data_df.iloc[:, 0]
    left = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    right = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    y_pos = np.arange(len(regions))
    fig, ax = plt.subplots(figsize=(10,6))
    ax.barh(y_pos, -left, color='#2ca02c', label='2022')
    ax.barh(y_pos, right, color='#d62728', label='2021')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(regions)
    ax.set_xlabel('占比')
    ax.set_title('蝴蝶图（文本）')
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_num_percent(name, data_df):
    """8 数值百分比"""
    x = data_df.iloc[:, 0]
    y = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    pct = pd.to_numeric(data_df.iloc[:, 4], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    bars = ax.bar(x, y, color='coral')
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.annotate(f'{pct[i]*100:.1f}%', xy=(bar.get_x()+bar.get_width()/2, height),
                    xytext=(0,5), textcoords="offset points", ha='center', va='bottom')
    ax.set_title('数值百分比')
    ax.set_ylabel('销量')
    plt.tight_layout()
    plt.show()

def plot_comparison_bar(name, data_df):
    """9 对比柱形图"""
    x = data_df.iloc[:, 0]
    y1 = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    y2 = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    x_pos = np.arange(len(x))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(x_pos - width/2, y1, width, label='2021', color='#1f77b4')
    ax.bar(x_pos + width/2, y2, width, label='2022', color='#ff7f0e')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x)
    ax.legend()
    ax.set_title('对比柱形图')
    ax.set_ylabel('销量')
    plt.tight_layout()
    plt.show()

def plot_gantt(name, data_df):
    """10 甘特图"""
    projects = data_df.iloc[:, 0]
    start_dates = pd.to_datetime(data_df.iloc[:, 1], errors='coerce')
    durations = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    completed = pd.to_numeric(data_df.iloc[:, 3], errors='coerce')
    order = np.argsort(start_dates)
    projects = projects.iloc[order]
    start_dates = start_dates.iloc[order]
    durations = durations.iloc[order]
    completed = completed.iloc[order]
    y_pos = np.arange(len(projects))
    fig, ax = plt.subplots(figsize=(10,6))
    ax.barh(y_pos, durations, left=start_dates, color='lightgray', height=0.4)
    progress_days = durations * completed
    ax.barh(y_pos, progress_days, left=start_dates, color='steelblue', height=0.4)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(projects)
    ax.xaxis_date()
    ax.set_title('甘特图')
    plt.tight_layout()
    plt.show()

def plot_smooth_line(name, data_df):
    """11 平滑折线图"""
    years = data_df.iloc[:, 0]
    months = data_df.iloc[:, 1]
    sales = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    x = np.arange(len(sales))
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(x, sales, marker='o', linestyle='-', linewidth=2, color='#1f77b4')
    labels = [f'{y}{m}' for y,m in zip(years, months)]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45)
    ax.set_title('平滑折线图')
    ax.set_ylabel('销量')
    plt.tight_layout()
    plt.show()

def plot_diamond_line(name, data_df):
    """12 菱形走势图"""
    x = data_df.iloc[:, 0]
    y = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(x, y, marker='D', linestyle='-', color='purple', markersize=8)
    ax.set_title('菱形走势图')
    ax.set_ylabel('完成率')
    plt.tight_layout()
    plt.show()

def plot_comparison_line(name, data_df):
    """13 对比折线图"""
    x = data_df.iloc[:, 0]
    y1 = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    y2 = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(x, y1, marker='o', label='2021年')
    ax.plot(x, y2, marker='s', label='2022年')
    ax.legend()
    ax.set_title('对比折线图')
    ax.set_ylabel('销量')
    plt.tight_layout()
    plt.show()

def plot_single_donut(name, data_df):
    """14 单值圆环图"""
    rate = pd.to_numeric(data_df.iloc[0, 0], errors='coerce')
    fig, ax = plt.subplots(figsize=(4,4))
    wedge1 = Wedge((0.5,0.5), 0.4, 0, 360*rate, facecolor='#1f77b4', edgecolor='white')
    wedge2 = Wedge((0.5,0.5), 0.4, 360*rate, 360, facecolor='lightgray', edgecolor='white')
    ax.add_patch(wedge1)
    ax.add_patch(wedge2)
    ax.text(0.5, 0.5, f'{rate:.0%}', ha='center', va='center', fontsize=20)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('单值圆环图')
    plt.tight_layout()
    plt.show()

def plot_waterball(name, data_df):
    """15 水球图"""
    rate = pd.to_numeric(data_df.iloc[0, 0], errors='coerce')
    fig, ax = plt.subplots(figsize=(5,5))
    bg = Circle((0.5,0.5), 0.4, color='lightgray', ec='gray', lw=2)
    ax.add_patch(bg)
    theta1 = 90 - 360*rate
    theta2 = 90
    wedge = Wedge((0.5,0.5), 0.4, theta1, theta2, facecolor='#1f77b4', alpha=0.7)
    ax.add_patch(wedge)
    ax.text(0.5, 0.5, f'{rate:.0%}', ha='center', va='center', fontsize=24, fontweight='bold')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('水球图')
    plt.tight_layout()
    plt.show()

def plot_wave_waterball(name, data_df):
    """16 波浪水球图"""
    rate = pd.to_numeric(data_df.iloc[0, 0], errors='coerce')
    fig, ax = plt.subplots(figsize=(5,5))
    circle = Circle((0.5,0.5), 0.4, facecolor='lightblue', edgecolor='blue', lw=2)
    ax.add_patch(circle)
    theta1 = 90 - 360*rate
    theta2 = 90
    wave = Wedge((0.5,0.5), 0.4, theta1, theta2, facecolor='#1f77b4', alpha=0.6)
    ax.add_patch(wave)
    ax.text(0.5, 0.5, f'{rate:.0%}', ha='center', va='center', fontsize=24)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('波浪水球图')
    plt.tight_layout()
    plt.show()

def plot_jue(name, data_df):
    """17 玉玦图"""
    labels = data_df.iloc[:, 0]
    sizes = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    fig, ax = plt.subplots(figsize=(6,6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%',
           startangle=90, counterclock=False,
           wedgeprops={'edgecolor':'white', 'linewidth':2})
    ax.set_title('玉玦图')
    plt.tight_layout()
    plt.show()

def plot_track(name, data_df):
    """18 跑道图"""
    depts = data_df.iloc[:, 0]
    vals = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    colors = plt.cm.viridis(np.linspace(0.2,0.8, len(vals)))
    ax.barh(depts, vals, color=colors)
    ax.set_title('跑道图')
    ax.set_xlabel('人数')
    plt.tight_layout()
    plt.show()

def plot_nightingale_pie(name, data_df):
    """19 南丁格尔圆饼图"""
    depts = data_df.iloc[:, 0]
    values = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    N = len(depts)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False)
    fig, ax = plt.subplots(subplot_kw={'projection':'polar'}, figsize=(6,6))
    width = 2*np.pi/N
    colors = plt.cm.RdYlGn_r(values)
    ax.bar(angles, values, width=width, color=colors, edgecolor='white')
    ax.set_xticks(angles)
    ax.set_xticklabels(depts)
    ax.set_yticklabels([])
    ax.set_title('南丁格尔圆饼图')
    plt.tight_layout()
    plt.show()

def plot_nightingale_ring(name, data_df):
    """20 南丁格尔圆环图"""
    ages = data_df.iloc[:, 0]
    values = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    N = len(ages)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False)
    fig, ax = plt.subplots(subplot_kw={'projection':'polar'}, figsize=(6,6))
    width = 2*np.pi/N
    colors = plt.cm.PuBuGn(values)
    ax.bar(angles, values, width=width, color=colors, edgecolor='white')
    ax.set_xticks(angles)
    ax.set_xticklabels(ages)
    ax.set_yticklabels([])
    ax.set_title('南丁格尔圆环图')
    plt.tight_layout()
    plt.show()

def plot_nightingale_ppt(name, data_df):
    """20 南丁格尔（PPT）"""
    depts = data_df.iloc[:, 0]
    values = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    N = len(depts)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False)
    fig, ax = plt.subplots(subplot_kw={'projection':'polar'}, figsize=(6,6))
    width = 2*np.pi/N
    colors = plt.cm.OrRd(values)
    ax.bar(angles, values, width=width, color=colors, edgecolor='white')
    ax.set_xticks(angles)
    ax.set_xticklabels(depts)
    ax.set_yticklabels([])
    ax.set_title('南丁格尔（PPT）')
    plt.tight_layout()
    plt.show()

def plot_dashboard(name, data_df):
    """22 仪表盘图"""
    pointer_val = None
    for col in data_df.columns:
        if '指针数值' in str(col):
            pointer_val = pd.to_numeric(data_df[col].iloc[0], errors='coerce')
            break
    if pointer_val is None:
        pointer_val = 76
    fig, ax = plt.subplots(figsize=(6,4), subplot_kw={'projection':'polar'})
    theta = np.linspace(0, np.pi, 100)
    ax.plot(theta, [1]*len(theta), color='lightgray', linewidth=15)
    angle = (pointer_val - 50) / (150-50) * 180
    angle_rad = np.radians(angle)
    colors = plt.cm.RdYlGn_r(np.linspace(0,1,100))
    for i in range(len(theta)-1):
        if theta[i] <= angle_rad:
            ax.plot(theta[i:i+2], [1,1], color=colors[i], linewidth=15)
    ax.plot([angle_rad, angle_rad], [0,1.2], color='red', linewidth=3)
    ax.set_xticks([0, np.pi/2, np.pi])
    ax.set_xticklabels(['50', '100', '150'])
    ax.set_ylim(0,1.5)
    ax.set_yticks([])
    ax.set_title('仪表盘图')
    plt.tight_layout()
    plt.show()

def plot_bar_line(name, data_df):
    """23 柱形折线图"""
    x = data_df.iloc[:, 0]
    y1 = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    y2 = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    fig, ax1 = plt.subplots(figsize=(8,5))
    ax1.bar(x, y1, color='skyblue', label='销售量')
    ax1.set_xlabel('年份')
    ax1.set_ylabel('销售量', color='blue')
    ax1.tick_params('y', labelcolor='blue')
    ax2 = ax1.twinx()
    ax2.plot(x, y2, color='red', marker='o', label='同比')
    ax2.set_ylabel('同比', color='red')
    ax2.tick_params('y', labelcolor='red')
    ax1.set_title('柱形折线图')
    plt.tight_layout()
    plt.show()

def plot_target_bar(name, data_df):
    """24 目标柱形图"""
    products = data_df.iloc[:, 0]
    actual = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    target = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    x_pos = np.arange(len(products))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(x_pos - width/2, actual, width, label='实际', color='#1f77b4')
    ax.bar(x_pos + width/2, target, width, label='目标', color='#ff7f0e')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(products)
    ax.legend()
    ax.set_title('目标柱形图')
    ax.set_ylabel('销量')
    plt.tight_layout()
    plt.show()

def plot_bullet(name, data_df):
    """25 子弹图"""
    products = data_df.iloc[:, 0]
    actual = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    target = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    poor = pd.to_numeric(data_df.iloc[:, 3], errors='coerce')
    good = pd.to_numeric(data_df.iloc[:, 4], errors='coerce')
    excel = pd.to_numeric(data_df.iloc[:, 5], errors='coerce')
    fig, ax = plt.subplots(figsize=(10,6))
    y_pos = np.arange(len(products))
    ax.barh(y_pos, poor, color='#d3d3d3', label='及格')
    ax.barh(y_pos, good, left=poor, color='#a9a9a9', label='良好')
    ax.barh(y_pos, excel, left=poor+good, color='#696969', label='优秀')
    ax.scatter(target, y_pos, color='red', marker='|', s=100, label='目标')
    ax.scatter(actual, y_pos, color='black', marker='o', label='实际')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(products)
    ax.legend()
    ax.set_title('子弹图')
    ax.set_xlabel('销量')
    plt.tight_layout()
    plt.show()

def plot_bar_circle(name, data_df):
    """26 柱形圆"""
    x = data_df.iloc[:, 0]
    y = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    pct = pd.to_numeric(data_df.iloc[:, 3], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(x, y, color='lightblue')
    for i, (xi, yi, p) in enumerate(zip(x, y, pct)):
        radius = 10 + 20*p
        circle = Circle((xi, yi+0.05*max(y)), radius/100, color='red', alpha=0.5)
        ax.add_patch(circle)
    ax.set_title('柱形圆')
    ax.set_ylabel('销量')
    plt.tight_layout()
    plt.show()

def plot_clustered_bar_line(name, data_df):
    """27 簇状柱形折线图"""
    x = data_df.iloc[:, 0]
    y1 = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    y2 = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    y3 = pd.to_numeric(data_df.iloc[:, 3], errors='coerce')
    x_pos = np.arange(len(x))
    width = 0.25
    fig, ax1 = plt.subplots(figsize=(8,5))
    ax1.bar(x_pos - width, y1, width, label='2022销量', color='#1f77b4')
    ax1.bar(x_pos, y2, width, label='2021销量', color='#ff7f0e')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(x)
    ax1.set_ylabel('销量')
    ax1.legend(loc='upper left')
    ax2 = ax1.twinx()
    ax2.plot(x_pos, y3, color='green', marker='o', label='同比')
    ax2.set_ylabel('同比')
    ax2.legend(loc='upper right')
    ax1.set_title('簇状柱形折线图')
    plt.tight_layout()
    plt.show()

def plot_composite_bar(name, data_df):
    """28 复合柱形图"""
    months = data_df.iloc[:, 0]
    monthly = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    quarterly = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    x_pos = np.arange(len(months))
    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(x_pos, monthly, color='steelblue', label='月度销量')
    ax.plot(x_pos, quarterly, color='red', marker='s', label='季度销量')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(months, rotation=45)
    ax.legend()
    ax.set_title('复合柱形图')
    ax.set_ylabel('销量')
    plt.tight_layout()
    plt.show()

def plot_sliding_bubble(name, data_df):
    """29 滑珠图"""
    regions = data_df.iloc[:, 0]
    rate = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    fig, ax = plt.subplots(figsize=(8,5))
    y_pos = np.arange(len(regions))
    ax.barh(y_pos, rate, color='lightblue', height=0.2)
    for i, (r, y) in enumerate(zip(rate, y_pos)):
        circle = Circle((r, y), 0.02, color='red')
        ax.add_patch(circle)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(regions)
    ax.set_xlim(0,1.1)
    ax.set_title('滑珠图')
    ax.set_xlabel('完成率')
    plt.tight_layout()
    plt.show()

def plot_comparison_sliding_bubble(name, data_df):
    """30 对比滑珠图"""
    regions = data_df.iloc[:, 0]
    rate22 = pd.to_numeric(data_df.iloc[:, 1], errors='coerce')
    rate21 = pd.to_numeric(data_df.iloc[:, 2], errors='coerce')
    y_pos = np.arange(len(regions))
    fig, ax = plt.subplots(figsize=(8,5))
    for i, (r22, r21, y) in enumerate(zip(rate22, rate21, y_pos)):
        ax.plot([0, r22], [y, y], color='blue', lw=2, alpha=0.5)
        ax.plot([0, r21], [y-0.2, y-0.2], color='orange', lw=2, alpha=0.5)
        ax.scatter(r22, y, color='blue', s=80, label='2022' if i==0 else "")
        ax.scatter(r21, y-0.2, color='orange', s=80, label='2021' if i==0 else "")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(regions)
    ax.set_xlim(0,1.1)
    ax.legend()
    ax.set_title('对比滑珠图')
    ax.set_xlabel('完成率')
    plt.tight_layout()
    plt.show()

def get_plot_function(name):
    mapping = {
        '1 渐变柱形图': plot_gradient_bar,
        '2 带均值柱形图': plot_mean_bar,
        '3 渐变圆角柱形图': plot_rounded_bar,
        '4 标注柱形图': plot_annotated_bar,
        '5 层叠柱形图': plot_stacked_bar,
        '6 蝴蝶图': plot_butterfly,
        '7 蝴蝶图': plot_butterfly_text,
        '8 数值百分比': plot_num_percent,
        '9 对比柱形图': plot_comparison_bar,
        '10 甘特图': plot_gantt,
        '11 平滑折线图': plot_smooth_line,
        '12 菱形走势图': plot_diamond_line,
        '13 对比折线图': plot_comparison_line,
        '14 单值圆环图': plot_single_donut,
        '15 水球图': plot_waterball,
        '16 波浪水球图': plot_wave_waterball,
        '17 玉玦图': plot_jue,
        '18 跑道图': plot_track,
        '19 南丁格尔圆饼图': plot_nightingale_pie,
        '20 南丁格尔圆环图': plot_nightingale_ring,
        '20 南丁格尔（PPT）': plot_nightingale_ppt,
        '22 仪表盘图': plot_dashboard,
        '23 柱形折线图': plot_bar_line,
        '24 目标柱形图': plot_target_bar,
        '25 子弹图': plot_bullet,
        '26 柱形圆': plot_bar_circle,
        '27 簇状柱形折线图': plot_clustered_bar_line,
        '28 复合柱形图': plot_composite_bar,
        '29 滑珠图': plot_sliding_bubble,
        '30 对比滑珠图': plot_comparison_sliding_bubble,
    }
    return mapping.get(name)

def plot_all_charts(file_path):
    xlsx = pd.ExcelFile(file_path, engine='openpyxl')
    for sheet_name in xlsx.sheet_names:
        print(f"正在绘制: {sheet_name}")
        df = xlsx.parse(sheet_name, header=None)
        cols, data_df = extract_data(df)
        if data_df is None or len(data_df) == 0:
            print(f"  跳过 {sheet_name}，无数据")
            continue
        print(f"  数据预览（前2行）:\n{data_df.head(2)}")
        func = get_plot_function(sheet_name.strip())   # ← 这里加了 .strip()
        if func:
            try:
                func(sheet_name, data_df)
            except Exception as e:
                print(f"  绘制 {sheet_name} 时出错: {e}")
        else:
            print(f"  未找到 {sheet_name} 的绘图函数，跳过")

if __name__ == '__main__':
    file1 = "C:/Users/ARRON/Desktop/第二章 图表(前15).xlsx"
    file2 = "C:/Users/ARRON/Desktop/第二章 图表(后15).xlsx"

    print("开始绘制前15个图表...")
    plot_all_charts(file1)
    print("开始绘制后15个图表...")
    plot_all_charts(file2)
    print("所有图表已显示完毕。")