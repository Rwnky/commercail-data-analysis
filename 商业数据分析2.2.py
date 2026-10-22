import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import PercentFormatter
from scipy import stats

# 中文字体（按你系统实际情况调整）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

np.random.seed(42)  # 可复现
# ============ 1.1 年度订单量 ============
years = list(range(2014, 2025))
annual_orders = np.random.randint(200, 501, size=len(years))

# 1.2 周平均处理时长
weeks = [f'week{i}' for i in range(1, 12)]
week_hours = np.random.randint(1, 41, size=len(weeks))
week_hours[-1] = np.random.randint(32, 41)   # week11 模拟异常（32-40）
week_avg = week_hours.mean()
warning_line = 35

# 1.3 月度订单 + 环比
months = list(range(1, 13))
month_orders = np.random.randint(200, 501, size=len(months))
mom_growth = np.concatenate([[np.nan],
                             np.diff(month_orders) / month_orders[:-1]])

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# --- 年度柱状图 ---
ax = axes[0, 0]
bars = ax.bar(years, annual_orders, color='#4C72B0', edgecolor='black')
for b, v in zip(bars, annual_orders):
    ax.text(b.get_x() + b.get_width()/2, v + 5, str(v),
            ha='center', fontsize=8)
ax.set_title('年度订单量趋势', fontsize=13, fontweight='bold')
ax.set_xlabel('年份'); ax.set_ylabel('订单量（个）')
ax.set_xticks(years); ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=0.3)

# --- 周处理时长+预警线 ---
ax = axes[0, 1]
ax.plot(weeks, week_hours, marker='o', color='#DD8452', linewidth=2,
        label='平均处理时长')
ax.axhline(week_avg, color='green', linestyle='--', label=f'平均 {week_avg:.1f}h')
ax.axhline(warning_line, color='red', linestyle=':', linewidth=2,
           label=f'预警值 {warning_line}h')
# 超过预警线的点标红
over_idx = [i for i, h in enumerate(week_hours) if h > warning_line]
ax.scatter([weeks[i] for i in over_idx],
           [week_hours[i] for i in over_idx],
           color='red', s=120, zorder=5, label='超预警')
ax.set_title('周平均处理时长 & 预警监控', fontsize=13, fontweight='bold')
ax.set_xlabel('周'); ax.set_ylabel('平均处理时长（小时）')
ax.tick_params(axis='x', rotation=45); ax.legend()
ax.grid(alpha=0.3)

# --- 月度订单量 ---
ax = axes[1, 0]
ax.plot(months, month_orders, marker='s', color='#55A868', linewidth=2)
ax.fill_between(months, month_orders, alpha=0.2, color='#55A868')
ax.set_title('月度订单量', fontsize=13, fontweight='bold')
ax.set_xlabel('月份'); ax.set_ylabel('订单量（个）')
ax.set_xticks(months); ax.grid(alpha=0.3)

# --- 月度环比 ---
ax = axes[1, 1]
colors = ['#C44E52' if v < 0 else '#55A868' for v in mom_growth[1:]]
ax.bar(months[1:], mom_growth[1:], color=colors, edgecolor='black')
ax.axhline(0, color='black', linewidth=0.8)
ax.yaxis.set_major_formatter(PercentFormatter(1.0))
ax.set_title('月度订单量环比增幅', fontsize=13, fontweight='bold')
ax.set_xlabel('月份'); ax.set_ylabel('环比增幅')
ax.set_xticks(months); ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('1_trend.png', dpi=150)
plt.show()

# ============ 2.1 产品订单量 ============
products = [f'产品 {i}' for i in range(1, 12)]
product_orders = np.random.randint(200, 501, size=len(products))

# 2.2 长名称产品（模拟排序后条形图数据，来自参考文件）
long_df = pd.DataFrame({
    '产品类型': [f'我的名字非常长{i}' for i in range(12, 1, -1)],
    '订单量': [205, 214, 258, 291, 295, 323, 375, 383, 400, 483, 494]
})

# 2.3 顾客画像（雷达图）
trait_labels = ['I', 'E', 'S', 'N', 'T', 'P']
trait_scores = [80, 10, 30, 60, 50, 40]
angles = np.linspace(0, 2*np.pi, len(trait_labels), endpoint=False).tolist()
angles += angles[:1]
scores_closed = trait_scores + trait_scores[:1]

fig = plt.figure(figsize=(18, 6))

# --- 产品订单量柱状图 ---
ax = fig.add_subplot(1, 3, 1)
bars = ax.bar(products, product_orders, color='#4C72B0', edgecolor='black')
for b, v in zip(bars, product_orders):
    ax.text(b.get_x() + b.get_width()/2, v + 5, str(v),
            ha='center', fontsize=8)
ax.set_title('各产品订单量对比', fontsize=13, fontweight='bold')
ax.set_ylabel('订单量（个）')
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=0.3)

# --- 长名称横向条形图（排序）---
ax = fig.add_subplot(1, 3, 2)
sorted_df = long_df.sort_values('订单量')
bars = ax.barh(sorted_df['产品类型'], sorted_df['订单量'],
               color='#DD8452', edgecolor='black')
for b, v in zip(bars, sorted_df['订单量']):
    ax.text(v + 5, b.get_y() + b.get_height()/2, str(v),
            va='center', fontsize=8)
ax.set_title('长名称产品订单量（横向排序）', fontsize=13, fontweight='bold')
ax.set_xlabel('订单量（个）')
ax.grid(axis='x', alpha=0.3)

# --- 顾客画像雷达图 ---
ax = fig.add_subplot(1, 3, 3, projection='polar')
ax.plot(angles, scores_closed, 'o-', linewidth=2, color='#55A868')
ax.fill(angles, scores_closed, alpha=0.25, color='#55A868')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(trait_labels, fontsize=11, fontweight='bold')
ax.set_ylim(0, 100)
ax.set_title('某顾客画像（雷达图）', fontsize=13, fontweight='bold', pad=20)
ax.grid(True)

plt.tight_layout()
plt.savefig('2_compare.png', dpi=150)
plt.show()

# ============ 3.1 时点客流量（30分钟粒度，一天48个点）============
times = pd.date_range('2020-01-01', periods=48, freq='30min')
traffic = np.random.normal(580, 60, size=48)

# 3.2 客单价（338 个用户）
df3 = pd.read_excel('3分布分析-参考.xlsx', sheet_name='分布分析', header=None)
# 取 U 列（客单价）有效数值
cust_price = pd.to_numeric(
    df3.iloc[:, 20], errors='coerce').dropna().values
# 若读不到，则模拟 338 个客单价
if len(cust_price) < 10:
    cust_price = np.random.normal(450, 130, size=338).clip(20, None)

# 四分位 & 离群点
q1, q2, q3 = np.percentile(cust_price, [25, 50, 75])
iqr = q3 - q1
upper_fence = q3 + 1.5 * iqr
lower_fence = q1 - 1.5 * iqr
outliers = cust_price[(cust_price > upper_fence) | (cust_price < lower_fence)]

# 3.3 年龄分布
ages = np.random.choice(range(1, 100), size=200, replace=True,
                        p=None).astype(int)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# --- 时点客流量 ---
ax = axes[0]
ax.plot(times, traffic, color='#4C72B0', linewidth=1.5)
ax.fill_between(times, traffic, alpha=0.2, color='#4C72B0')
ax.set_title('时点客流量（30分钟粒度）', fontsize=13, fontweight='bold')
ax.set_xlabel('时点'); ax.set_ylabel('门店客流量')
ax.tick_params(axis='x', rotation=45)
ax.grid(alpha=0.3)
# 每天平均参考线
ax.axhline(traffic.mean(), color='red', linestyle='--',
           label=f'均值 {traffic.mean():.1f}')
ax.legend()

# --- 客单价箱线图 + 四分位信息 ---
ax = axes[1]
bp = ax.boxplot(cust_price, vert=True, patch_artist=True,
                boxprops=dict(facecolor='#DD8452', alpha=0.6),
                medianprops=dict(color='red', linewidth=2),
                flierprops=dict(marker='o', markersize=4,
                                markerfacecolor='red', alpha=0.5))
# 标注四分位与上下限
info = (f'min={cust_price.min():.1f}\n'
        f'Q1={q1:.1f}\n'
        f'中位数={q2:.1f}\n'
        f'Q3={q3:.1f}\n'
        f'max={cust_price.max():.1f}\n'
        f'IQR={iqr:.1f}\n'
        f'上限={upper_fence:.1f}\n'
        f'离群点={len(outliers)}个')
ax.text(1.25, q2, info, fontsize=10, va='center',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
ax.set_title('客单价分布（箱线图+四分位）', fontsize=13, fontweight='bold')
ax.set_xticks([1]); ax.set_xticklabels(['客单价'])
ax.set_ylabel('金额'); ax.grid(axis='y', alpha=0.3)

# --- 年龄分布直方图 ---
ax = axes[2]
ax.hist(ages, bins=20, color='#55A868', edgecolor='black', alpha=0.8)
ax.set_title('年龄分布直方图', fontsize=13, fontweight='bold')
ax.set_xlabel('年龄'); ax.set_ylabel('下单人数')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('3_distribution.png', dpi=150)
plt.show()

# 离群点明细
print(f'四分位数: Q1={q1:.2f}, 中位数={q2:.2f}, Q3={q3:.2f}')
print(f'IQR={iqr:.2f}, 上限={upper_fence:.2f}, 下限={lower_fence:.2f}')
print(f'离群点数量: {len(outliers)}')

# ============ 4.1 产品销售量（构成占比）============
products4 = [f'产品 {i}' for i in range(1, 5)]
sales4 = np.random.randint(100, 800, size=len(products4))

# 4.2 年度×产品（普通堆叠）
years4 = list(range(2020, 2025))
year_product = pd.DataFrame(
    np.random.randint(200, 501, size=(len(years4), 3)),
    index=years4, columns=['产品 1', '产品 2', '产品 3']
)

# 4.3 年度×产品（100%堆叠）——参考文件中的"折线图数据"
year_product2 = pd.DataFrame(
    np.column_stack([
        np.random.randint(100, 201, size=5),
        np.random.randint(200, 301, size=5),
        np.random.randint(400, 501, size=5),
    ]),
    index=years4, columns=['产品 1', '产品 2', '产品 3']
)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# --- 饼图 ---
ax = axes[0]
total = sales4.sum()
ax.pie(sales4, labels=products4, autopct=lambda p: f'{p:.1f}%\n({p*total/100:.0f})',
       startangle=90, colors=plt.cm.Pastel1(np.linspace(0, 1, 4)))
ax.set_title('产品销售量构成（饼图）', fontsize=13, fontweight='bold')

# --- 年度×产品 堆叠柱状图 ---
ax = axes[1]
bottom = np.zeros(len(years4))
for col in year_product.columns:
    ax.bar(years4, year_product[col], bottom=bottom,
           label=col, edgecolor='black')
    bottom += year_product[col].values
ax.set_title('年度×产品 堆叠柱状图', fontsize=13, fontweight='bold')
ax.set_xlabel('年份'); ax.set_ylabel('销售量')
ax.legend(); ax.grid(axis='y', alpha=0.3)

# --- 100%堆叠面积图 ---
ax = axes[2]
pct = year_product2.div(year_product2.sum(axis=1), axis=0) * 100
ax.stackplot(years4, [pct[c] for c in pct.columns],
             labels=pct.columns, alpha=0.85)
ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(PercentFormatter())
ax.set_title('年度产品构成占比（100%堆叠）', fontsize=13, fontweight='bold')
ax.set_xlabel('年份'); ax.set_ylabel('占比')
ax.legend(loc='upper right'); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('4_composition.png', dpi=150)
plt.show()

# ============ 5.1 分类变量：营销活动 × 是否下单 ============
campaigns = [f'营销活动 {i}' for i in range(1, 6)]
ordered = np.random.randint(100, 501, size=len(campaigns))
unordered = np.random.randint(100, 501, size=len(campaigns))

# 5.2 分类变量 & 连续变量：营销活动 × 销售金额
n_users = 60
user_ids = [f'id{i}' for i in range(1, n_users + 1)]
campaign_amount = pd.DataFrame({
    '用户id': user_ids,
    '营销活动1': np.random.randint(50, 501, n_users),
    '营销活动2': np.random.randint(300, 1001, n_users),
    '营销活动3': np.random.randint(10, 201, n_users),
})
# 仅保留展示用长表（图示用营销活动1的分布）
amount_long = campaign_amount.melt(id_vars='用户id',
                                   var_name='营销活动',
                                   value_name='销售金额')

# 5.3 连续×连续：投入成本 vs 产出收益
n = 60
cost = np.random.randint(40, 460, n)
profit = cost * 1.8 + np.random.normal(0, 60, n) + 60
r, p = stats.pearsonr(cost, profit)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# --- 分类 × 分类 ---
ax = axes[0]
x = np.arange(len(campaigns))
w = 0.38
ax.bar(x - w/2, ordered, w, label='下单用户', color='#55A868')
ax.bar(x + w/2, unordered, w, label='未下单用户', color='#C44E52')
ax.set_xticks(x); ax.set_xticklabels(campaigns)
ax.set_title('各营销活动 下单/未下单 人数', fontsize=13, fontweight='bold')
ax.set_ylabel('人数'); ax.legend(); ax.grid(axis='y', alpha=0.3)

# --- 分类 × 连续（箱线图）---
ax = axes[1]
data_by_camp = [amount_long[amount_long['营销活动'] == c]['销售金额']
                for c in amount_long['营销活动'].unique()]
ax.boxplot(data_by_camp, patch_artist=True,
           boxprops=dict(facecolor='#4C72B0', alpha=0.6),
           medianprops=dict(color='red', linewidth=2))
ax.set_xticklabels(amount_long['营销活动'].unique(), rotation=0)
ax.set_title('不同营销活动 销售金额分布', fontsize=13, fontweight='bold')
ax.set_ylabel('销售金额'); ax.grid(axis='y', alpha=0.3)

# --- 连续 × 连续（散点 + 线性回归）---
ax = axes[2]
ax.scatter(cost, profit, s=50, alpha=0.7, color='#DD8452',
           edgecolors='black', linewidths=0.5)
k, b = np.polyfit(cost, profit, 1)
x_line = np.linspace(cost.min(), cost.max(), 100)
ax.plot(x_line, k * x_line + b, 'r--', linewidth=2,
        label=f'y={k:.2f}x+{b:.1f}\nr={r:.3f}, p={p:.2e}')
ax.set_title('投入成本 vs 产出收益', fontsize=13, fontweight='bold')
ax.set_xlabel('投入成本'); ax.set_ylabel('产出收益')
ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('5_relationship.png', dpi=150)
plt.show()

print(f'投入-产出 相关系数 r={r:.3f}, p值={p:.2e}')