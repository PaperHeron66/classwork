# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt

# 1. 设置中文字体，避免图表乱码
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 2. 读取原始数据
# 请将路径替换为你电脑中的实际路径
file_path = r"C:\baidunetdiskdownload\案例3：电商平台的精准营销\案例3：电商平台的精准营销-原始数据.xlsx"
df = pd.read_excel(file_path, sheet_name='原始数据')

# 3. 计算年龄段
def get_age_group(age):
    if 18 <= age <= 25:
        return '18-25岁'
    elif 26 <= age <= 35:
        return '26-35岁'
    elif 36 <= age <= 49:
        return '36-49岁'
    else:
        return '50岁以上'

df['客户年龄段'] = df['年龄'].apply(get_age_group)

# ==========================================
# 分析1：购买客户的性别分布
# ==========================================
gender_counts = df['性别'].value_counts()
print("\n1、购买客户的性别分布：")
print(gender_counts)
print("总计：", gender_counts.sum())

plt.figure(figsize=(6, 4))
bars = plt.bar(gender_counts.index, gender_counts.values, color=['#FF9999', '#66B3FF'])
plt.title('1、购买客户的性别分布')
plt.ylabel('客户数')
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 20, f'{height}', ha='center')
plt.tight_layout()
plt.show()

# ==========================================
# 分析2：女性消费客户的年龄段分布
# ==========================================
female_df = df[df['性别'] == 'Female']
age_order = ['18-25岁', '26-35岁', '36-49岁', '50岁以上']
female_age_counts = female_df['客户年龄段'].value_counts().reindex(age_order).fillna(0).astype(int)

print("\n2、女性消费客户的年龄段分布：")
print(female_age_counts)
print("总计：", female_age_counts.sum())

plt.figure(figsize=(8, 4))
bars = plt.bar(female_age_counts.index, female_age_counts.values, color='#FFA07A')
plt.title('2、女性消费客户的年龄段分布')
plt.ylabel('客户数')
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 5, f'{height}', ha='center')
plt.tight_layout()
plt.show()

# ==========================================
# 分析3：50岁以上女性客户的消费品类分布
# ==========================================
female_50plus = female_df[female_df['客户年龄段'] == '50岁以上']
category_counts = female_50plus['品类'].value_counts().sort_values(ascending=True)

print("\n3、50岁以上女性客户的消费品类分布：")
print(category_counts.sort_values(ascending=False))
print("总计：", category_counts.sum())

plt.figure(figsize=(8, 5))
bars = plt.barh(category_counts.index, category_counts.values, color='#87CEEB')
plt.title('3、50岁以上女性客户的消费品类分布')
plt.xlabel('客户数')
for bar in bars:
    width = bar.get_width()
    plt.text(width + 3, bar.get_y() + bar.get_height()/2, f'{width}', va='center')
plt.tight_layout()
plt.show()

# ==========================================
# 分析4：50岁以上女性服饰和护肤品消费人群的支付方式分布
# ==========================================
target_df = female_50plus[female_50plus['品类'].isin(['Clothing', 'Cosmetics'])]
payment_counts = target_df['支付方式'].value_counts()

print("\n4、50岁以上女性服饰和护肤品消费人群的支付方式分布：")
print(payment_counts)
print("总计：", payment_counts.sum())

plt.figure(figsize=(6, 4))
plt.pie(payment_counts.values, labels=payment_counts.index, autopct='%1.1f%%',
        colors=['#FFD700', '#90EE90', '#87CEFA'], startangle=90)
plt.title('4、50岁以上女性服饰和护肤品消费支付方式分布')
plt.tight_layout()
plt.show()