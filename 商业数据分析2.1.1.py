import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ============ 1. 读取数据 ============
df = pd.read_excel('1-1波士顿矩阵-参考.xlsx', sheet_name='销售表')

# ============ 2. 数据处理 ============
df['销售日期'] = pd.to_datetime(df['销售日期'])
df['月份'] = df['销售日期'].dt.month

# 计算每个品牌每月销售额
brand_month = df.groupby(['品牌', '月份'])['订单金额'].sum().reset_index()

# 透视表：品牌 × 月份
pivot = brand_month.pivot(index='品牌', columns='月份', values='订单金额').fillna(0)
pivot.columns = [f'{m}月' for m in pivot.columns]

# ============ 3. 计算指标 ============
# 3.1 市场占有率 = 品牌总销售额 / 总销售额
total_sales = df['订单金额'].sum()
brand_sales = df.groupby('品牌')['订单金额'].sum()
market_share = brand_sales / total_sales

# 3.2 销售增长率 = (8月销售额 - 7月销售额) / 7月销售额
july = pivot.get('7月', pd.Series(0, index=pivot.index))
aug = pivot.get('8月', pd.Series(0, index=pivot.index))
growth_rate = (aug - july) / july.replace(0, np.nan)

# 3.3 阈值
total_july = df[df['月份'] == 7]['订单金额'].sum()
total_aug = df[df['月份'] == 8]['订单金额'].sum()
total_growth = (total_aug - total_july) / total_july
avg_market_share = market_share.mean()

print(f"总市场环比增长率: {total_growth:.4f}")
print(f"品牌平均市场占有率: {avg_market_share:.4f}")

# ============ 4. 构建结果表 ============
result = pd.DataFrame({
    '品牌': market_share.index,
    '销售额占比': market_share.values,
    '销售额环比': growth_rate.values
})

# ============ 5. 波士顿矩阵分类 ============
def bcg_classify(row):
    high_share = row['销售额占比'] >= avg_market_share
    high_growth = row['销售额环比'] >= total_growth
    if high_share and high_growth:
        return '明星业务'
    elif high_share and not high_growth:
        return '现金牛业务'
    elif not high_share and high_growth:
        return '问题业务'
    else:
        return '瘦狗业务'

result['业务类型'] = result.apply(bcg_classify, axis=1)

print("\n========== 波士顿矩阵分类结果 ==========")
print(result.to_string(index=False))

# ============ 6. 可视化 ============
fig, ax = plt.subplots(figsize=(10, 8))

colors = {
    '明星业务': '#FFD700',
    '现金牛业务': '#90EE90',
    '问题业务': '#87CEEB',
    '瘦狗业务': '#FF6B6B'
}

for _, row in result.iterrows():
    ax.scatter(row['销售额占比'], row['销售额环比'],
               s=300, c=colors[row['业务类型']],
               edgecolors='black', zorder=5)
    ax.annotate(row['品牌'], (row['销售额占比'], row['销售额环比']),
                textcoords="offset points", xytext=(0, 12),
                ha='center', fontsize=11, fontweight='bold')

ax.axvline(x=avg_market_share, color='gray', linestyle='--', linewidth=1.5)
ax.axhline(y=total_growth, color='gray', linestyle='--', linewidth=1.5)

# 象限标签
x_max = result['销售额占比'].max() * 1.15
y_max = result['销售额环比'].max() * 1.15
y_min = result['销售额环比'].min() * 1.15

ax.text(x_max*0.75, y_max*0.85, '明星业务', fontsize=14, color='#B8860B',
        ha='center', fontweight='bold', alpha=0.7)
ax.text(avg_market_share*0.2, y_max*0.85, '问题业务', fontsize=14, color='#4682B4',
        ha='center', fontweight='bold', alpha=0.7)
ax.text(x_max*0.75, y_min*0.85, '现金牛业务', fontsize=14, color='#228B22',
        ha='center', fontweight='bold', alpha=0.7)
ax.text(avg_market_share*0.2, y_min*0.85, '瘦狗业务', fontsize=14, color='#B22222',
        ha='center', fontweight='bold', alpha=0.7)

ax.set_xlabel('市场占有率（销售额占比）', fontsize=13)
ax.set_ylabel('销售增长率（销售额环比）', fontsize=13)
ax.set_title('波士顿矩阵（BCG Matrix）', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('bcg_matrix.png', dpi=150)
plt.show()