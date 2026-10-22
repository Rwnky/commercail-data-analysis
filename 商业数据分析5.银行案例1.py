import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
from matplotlib import cm

# ==========================================
# 1. 设置中文字体（解决图表中文乱码问题）
# ==========================================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 2. 读取数据与预处理
# ==========================================
file_name = '银行案例数据 - 学员用.xlsx'

# 读取维度表
df_risk = pd.read_excel(file_name, sheet_name='风险偏好说明表')
df_category = pd.read_excel(file_name, sheet_name='品类说明表')
df_edu = pd.read_excel(file_name, sheet_name='学历说明表')

# 读取事实表
df_sales = pd.read_excel(file_name, sheet_name='销售数据')

# 字段映射（关联维度表）
df_sales = df_sales.merge(df_category, on='品类编号', how='left')
df_sales = df_sales.merge(df_edu, on='学历编号', how='left')
# 修正列名
df_sales.rename(columns={'品类名称': '品类', '学历名称': '学历'}, inplace=True)

# ==========================================
# 3. 计算业务指标
# ==========================================
# 3.1 核心指标
total_sales = df_sales['购买金额'].sum()
sales_target = 25000000  # 2500万
completion_rate = total_sales / sales_target

# 3.2 客户画像漏斗数据 (按人数统计)
total_customers = len(df_sales)
income_dist = df_sales['家庭年收入'].value_counts(normalize=True).sort_values(ascending=False)
age_dist = df_sales['年龄'].value_counts(normalize=True).sort_values(ascending=False)
edu_dist = df_sales['学历'].value_counts(normalize=True).sort_values(ascending=False)
gender_dist = df_sales['性别'].value_counts(normalize=True).sort_values(ascending=False)

# 3.3 不同理财品类的销售占比 (按金额)
cat_sales = df_sales.groupby('品类')['购买金额'].sum().sort_values(ascending=False)

# 3.4 客单及期限均值分布
cat_stats = df_sales.groupby('品类').agg(
    客单=('购买金额', 'mean'),
    期限均值=('期限', 'mean')
).reindex(cat_sales.index)  # 按销售额排序

# 3.5 选择本行/产品原因词频
bank_reason_counts = df_sales['选择本行的原因'].value_counts()
product_reason_counts = df_sales['购买目的'].value_counts()

# ==========================================
# 4. 开始绘图
# ==========================================
fig = plt.figure(figsize=(16, 10), facecolor='white')
# 定义整体网格 3行2列
gs = gridspec.GridSpec(3, 2, figure=fig, height_ratios=[1.2, 2, 1.5], hspace=0.4, wspace=0.1)

# ----------------- 模块1：核心指标卡片 (左上) -----------------
ax1 = fig.add_subplot(gs[0, 0])
ax1.axis('off')
# 绘制外边框
rect1 = patches.Rectangle((0, 0), 0.8, 1, linewidth=1, edgecolor='gray', facecolor='#f8f9fa')
ax1.add_patch(rect1)
# 写入文字
ax1.text(0.05, 0.75, 'MTD销售额', fontsize=14, fontweight='bold', color='#333333')
ax1.text(0.05, 0.35, f'{total_sales}', fontsize=36, fontweight='bold', color='black')
ax1.text(0.05, 0.05, 'MTD销售目标达成率', fontsize=14, fontweight='bold', color='#333333')
ax1.text(0.05, -0.3, f'{completion_rate:.2%}', fontsize=36, fontweight='bold', color='black')

# ----------------- 模块2：客户画像漏斗 (右上) -----------------
ax2 = fig.add_subplot(gs[0, 1])
ax2.axis('off')
# 定义各层级标签
labels = ['家庭年收入', '年龄', '学历名称', '性别']
data_list = [income_dist, age_dist, edu_dist, gender_dist]
colors = ['#f39c12', '#f39c12', '#f39c12', '#f39c12']

# 手动绘制漏斗图效果
x_positions = [0.1, 0.35, 0.6, 0.85]
bar_width = 0.15
for i, (label, dist) in enumerate(zip(labels, data_list)):
    x = x_positions[i]
    # 顶部标签
    ax2.text(x, 0.95, label, fontsize=12, fontweight='bold', ha='center')

    # 绘制背景条和前景条模拟漏斗
    y_start = 0.8
    max_h = 0.5
    total_val = dist.sum()  # 1.0

    for j, (idx, val) in enumerate(dist.head(4).items()):  # 只显示前四名
        h = val * max_h
        y = y_start - j * (max_h / 3) - h  # 计算当前条的y坐标，形成阶梯

        # 绘制背景灰条
        ax2.barh(y, bar_width, height=0.08, color='#e0e0e0', align='center')
        # 绘制前景橙条
        ax2.barh(y, bar_width * val, height=0.08, color='#f39c12', align='center')

        # 文字标签
        if i == 0:
            ax2.text(x - 0.02, y, f"{idx}", ha='right', va='center', fontsize=9)
            ax2.text(x + 0.09, y, f"{val:.2%}", ha='left', va='center', fontsize=9, color='gray')
        else:
            ax2.text(x, y + 0.06, f"{idx}", ha='center', va='bottom', fontsize=9)
            ax2.text(x, y - 0.06, f"{val:.2%}", ha='center', va='top', fontsize=9, color='gray')

    # 绘制连接线
    if i < 3:
        next_x = x_positions[i + 1]
        y_top = y_start
        ax2.plot([x + bar_width / 2, next_x - bar_width / 2], [y_top, y_top], color='#f39c12', linewidth=2)

# ----------------- 模块3：不同理财品类的销售占比 (中左) -----------------
ax3 = fig.add_subplot(gs[1, 0])
cat_sales_wan = cat_sales / 10000  # 转换为万元
bars = ax3.bar(range(len(cat_sales_wan)), cat_sales_wan.values, color='#f39c12', width=0.6)

# 在柱子上显示数值
for bar in bars:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width() / 2, yval + 0.2, f'{yval:.1f} 百万', ha='center', va='bottom', fontsize=9)

ax3.set_xticks(range(len(cat_sales_wan)))
ax3.set_xticklabels(cat_sales_wan.index, rotation=35, ha='right', fontsize=9)
ax3.set_ylabel('MTD销售额')
ax3.set_title('不同理财品类的销售占比', fontsize=14, loc='center', pad=10)

# 去除边框
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# ----------------- 模块4：客单及期限均值分布 (中右) -----------------
ax4 = fig.add_subplot(gs[1, 1])
# 绘制柱状图（客单）
x = np.arange(len(cat_stats))
width = 0.5
rects1 = ax4.bar(x, cat_stats['客单'], width, color='#f39c12', label='客单')
ax4.set_ylabel('客单', fontsize=10)

# 添加柱状图数据标签
for rect in rects1:
    height = rect.get_height()
    ax4.text(rect.get_x() + rect.get_width() / 2, height / 2, f'{int(height)}', ha='center', va='center', color='white',
             fontsize=9)

# 绘制折线图（期限均值） - 使用双Y轴
ax5 = ax4.twinx()
rects2 = ax5.plot(x, cat_stats['期限均值'], color='#e67e22', marker='o', linewidth=2, label='期限均值')
ax5.set_ylabel('期限均值', fontsize=10)
ax5.set_ylim(0, 5)

# 折线图数据标签
for i, val in enumerate(cat_stats['期限均值']):
    ax5.text(i, val + 0.2, f'{val:.2f}', ha='center', va='bottom', color='#e67e22', fontsize=10, fontweight='bold')

# 设置X轴标签
ax4.set_xticks(x)
ax4.set_xticklabels(cat_stats.index, rotation=25, ha='right', fontsize=9)

ax4.set_title('客单及期限均值分布', fontsize=14, loc='center', pad=10)
# 图例合并
lines, labels = ax4.get_legend_handles_labels()
lines2, labels2 = ax5.get_legend_handles_labels()
ax4.legend(lines + lines2, labels + labels2, loc='upper right', frameon=False)

# 去除边框
ax4.spines['top'].set_visible(False)
ax5.spines['top'].set_visible(False)

# ----------------- 模块5：选择本行的原因 (左下 - 文字云) -----------------
ax6 = fig.add_subplot(gs[2, 0])
ax6.axis('off')
ax6.set_title('选择本行的原因', fontsize=14, loc='center', pad=10)

# 模拟文字云 - 根据频次设定字号和旋转
reasons = ['预期年化收益率高', '银行信誉', '银行人员服务', '理财产品风险评级', '理财产品种类多', '亲友选择']
frequencies = [bank_reason_counts.get(r, 0) for r in reasons]
# 为了视觉震撼，将排名第一的放大
colors_list = ['#f39c12', '#e74c3c', '#c0392b', '#d35400', '#e67e22', '#f1c40f']

# 手动布置位置和角度
positions = [(0.5, 0.5), (0.2, 0.8), (0.8, 0.8), (0.2, 0.2), (0.8, 0.2), (0.1, 0.5)]
angles = [-15, 20, -20, 30, -30, 10]
sizes = [45, 15, 18, 14, 16, 12]

for i, (txt, pos, angle, size, color) in enumerate(zip(reasons, positions, angles, sizes, colors_list)):
    ax6.text(pos[0], pos[1], txt, fontsize=size, rotation=angle,
             ha='center', va='center', color=color, fontweight='bold')

# ----------------- 模块6：选择产品原因 (右下 - 文字云) -----------------
ax7 = fig.add_subplot(gs[2, 1])
ax7.axis('off')
ax7.set_title('选择产品原因', fontsize=14, loc='center', pad=10)

# 这里用购买目的字段来模拟
p_reasons = ['合理安排资金、分担风险', '长期资产保值增值', '短期资产保值增值', '医疗、养老及教育', '流行趋势', '兴趣爱好',
             '其他']
p_freqs = [product_reason_counts.get(r, 0) for r in p_reasons]

p_positions = [(0.5, 0.5), (0.3, 0.7), (0.7, 0.7), (0.2, 0.3), (0.8, 0.3), (0.1, 0.6), (0.9, 0.6)]
p_angles = [-15, 10, -10, 25, -25, 40, -40]
p_sizes = [40, 25, 25, 16, 14, 12, 10]
p_colors = ['#f39c12', '#e74c3c', '#c0392b', '#d35400', '#e67e22', '#f1c40f', '#bdc3c7']

for i, (txt, pos, angle, size, color) in enumerate(zip(p_reasons, p_positions, p_angles, p_sizes, p_colors)):
    ax7.text(pos[0], pos[1], txt, fontsize=size, rotation=angle,
             ha='center', va='center', color=color, fontweight='bold')

# 展示并保存图表
plt.tight_layout()
plt.savefig('bank_bi_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()