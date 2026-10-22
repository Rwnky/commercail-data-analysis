import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==========================================
# 设置中文字体，防止图表中的中文变成方块
# ==========================================
# Windows 用户通常使用 'SimHei' (黑体) 或 'Microsoft YaHei' (微软雅黑)
# Mac 用户通常使用 'Arial Unicode MS' 或 'PingFang SC'
plt.rcParams['font.sans-serif'] = ['SimHei']  # 如果在 Mac 上运行报错，请换成 'Arial Unicode MS'
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 准备模拟数据
# ==========================================
# 图 1 数据：不同类型和性别的用户数量
type_data = ['普通卡', '青年卡', '金卡']
male_counts = [340, 70, 45]   # 模拟男性数量（浅蓝色）
female_counts = [315, 75, 45] # 模拟女性数量（深蓝色）

# 图 2 数据：不同年份和性别的总金额趋势 (单位：百万)
years = ['1993年', '1994年', '1995年', '1996年', '1997年', '1998年']
male_amount = [2, 6, 8, 10, 13, 12]    # 模拟男性金额趋势
female_amount = [1, 7, 5, 8, 18, 13]   # 模拟女性金额趋势

# ==========================================
# 开始绘制图表
# ==========================================
# 创建一个 1 行 2 列的画布，尺寸为 (16, 6)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.patch.set_facecolor('#f8f9fa') # 设置整体画布背景色（类似 Power BI 的浅灰背景）

# ----------------- 图 1：堆叠柱状图 (计数) -----------------
ax1 = axes[0]
ax1.set_facecolor('#f8f9fa')
ax1.grid(axis='y', linestyle=':', alpha=0.7) # 添加横向虚线网格

# 绘制底层（男）
bar1 = ax1.bar(type_data, male_counts, color='#1E90FF', label='男', width=0.5)
# 绘制顶层（女），bottom参数设为男的数量，实现堆叠
bar2 = ax1.bar(type_data, female_counts, bottom=male_counts, color='#000080', label='女', width=0.5)

# 设置标题和轴标签
ax1.set_title('sex 的计数(按 type 和 sex)', loc='left', fontsize=12)
ax1.set_xlabel('type', fontsize=11)
ax1.set_ylabel('sex 的计数', fontsize=11)
ax1.set_ylim(0, 700) # 设置 Y 轴范围匹配截图

# 设置图例 (放在左上角，水平排列)
ax1.legend(loc='upper left', ncol=2, frameon=False, bbox_to_anchor=(0, 1.05))

# 去除顶部和右侧的边框线
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)


# ----------------- 图 2：面积折线图 (金额总和) -----------------
ax2 = axes[1]
ax2.set_facecolor('#f8f9fa')
ax2.grid(linestyle=':', alpha=0.7)

# 绘制男性面积图
ax2.fill_between(years, male_amount, color='#1E90FF', alpha=0.6, label='男')
ax2.plot(years, male_amount, color='#1E90FF', linewidth=2)

# 绘制女性面积图
ax2.fill_between(years, female_amount, color='#000080', alpha=0.4, label='女')
ax2.plot(years, female_amount, color='#000080', linewidth=2)

# 截图中 1994 年有一条垂直参考线
ax2.axvline(x=1, color='gray', linestyle='-', linewidth=1)

# 设置标题和轴标签
ax2.set_title('amount 的总和(按 年 和 sex)', loc='left', fontsize=12)
ax2.set_xlabel('年', fontsize=11)
ax2.set_ylabel('amount 的总和', fontsize=11)

# 设置 Y 轴刻度标签格式为 "X 百万"
yticks = np.arange(0, 40000000, 5000000)
ax2.set_yticks(yticks)
ax2.set_yticklabels([f"{int(y/1000000)} 百万" for y in yticks])

# 设置图例 (放在左上角，水平排列)
ax2.legend(loc='upper left', ncol=2, frameon=False, bbox_to_anchor=(0, 1.05))

# 去除顶部和右侧的边框线
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color('#cccccc')
ax2.spines['bottom'].set_color('#cccccc')


# ==========================================
# 调整布局并显示/保存
# ==========================================
plt.tight_layout(pad=3.0) # 调整子图间距

# 如果你想把图片直接保存到本地，可以取消下面这行的注释
# plt.savefig('power_bi_charts.png', dpi=300, bbox_inches='tight')

plt.show()