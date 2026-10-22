import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker

# 设置中文字体（按你系统实际情况调整，Windows常用SimHei，Mac常用PingFang SC）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# ================= 1. 数据读取与处理 =================
# 请确保 csv 文件与代码在同一目录
orders = pd.read_csv('订单表.csv')
details = pd.read_csv('订单表明细表.csv')
products = pd.read_csv('商品表.csv')
categories = pd.read_csv('商品类型表.csv')

# 关联维表：明细 -> 商品 -> 商品类型
df = details.merge(products, on='ProductID', how='left') \
            .merge(categories, on='CategoryID', how='left')
# 关联订单主表：获取时间、省份
df = df.merge(orders, on='OrderID', how='left')

# 数据类型转换
df['OrderDate'] = pd.to_datetime(df['OrderDate'])
df['Year'] = df['OrderDate'].dt.year
df['Month'] = df['OrderDate'].dt.month
df['Profit'] = df['销售金额'] - df['销售成本']

# ================= 2. 计算核心指标 (KPI) =================
total_sales = df['销售金额'].sum()
total_profit = df['Profit'].sum()
order_count = df['OrderID'].nunique()

# ================= 3. 计算图表所需聚合数据 =================
# 3.1 按时间（日）的销售额趋势
daily_sales = df.groupby(df['OrderDate'].dt.date)['销售金额'].sum().reset_index()
daily_sales['OrderDate'] = pd.to_datetime(daily_sales['OrderDate'])

# 3.2 按 CategoryName 的销售额（饼图 & 柱状图）
cat_sales = df.groupby('CategoryName')['销售金额'].sum().reset_index()
cat_sales = cat_sales.sort_values('销售金额', ascending=False)

# 3.3 按 ShipProvince 的销售额（矩形树图）
prov_sales = df.groupby('ShipProvince')['销售金额'].sum().reset_index()
prov_sales = prov_sales.sort_values('销售金额', ascending=False).head(15) # 取前15大省份

# ================= 4. 构建仪表盘大屏 =================
fig = plt.figure(figsize=(16, 12), facecolor='#F4F5F7')
# 划分为上下两个大区域
gs = gridspec.GridSpec(3, 2, height_ratios=[1, 2.5, 2.5], hspace=0.3, wspace=0.2)

# ==================== 4.1 顶部 KPI 卡片 ====================
ax_kpi = fig.add_subplot(gs[0, :])
ax_kpi.axis('off')

# 绘制 3 个 KPI 卡片
card_texts = [
    (f"{total_sales / 1000:.0f} 千", "sales 的总和", 0.15),
    (f"{total_profit / 1000:.0f} 千", "利润的总和", 0.4),
    (f"{order_count}", "OrderID 的计数", 0.65)
]

for text_main, text_sub, x_pos in card_texts:
    # 卡片背景（使用 FancyBboxPatch 模拟阴影卡片）
    rect = plt.Rectangle((x_pos, 0.1), 0.15, 0.8,
                         facecolor='white', edgecolor='#D3D3D3', linewidth=2,
                         transform=ax_kpi.transAxes, zorder=1)
    ax_kpi.add_patch(rect)
    # 主数值
    ax_kpi.text(x_pos + 0.075, 0.65, text_main, ha='center', va='center',
                fontsize=36, fontweight='bold', color='#333333', transform=ax_kpi.transAxes, zorder=2)
    # 副标题
    ax_kpi.text(x_pos + 0.075, 0.3, text_sub, ha='center', va='center',
                fontsize=12, color='#666666', transform=ax_kpi.transAxes, zorder=2)

# 为右上角留出筛选器位置（此处省略绘图，仅用文字示意）
ax_kpi.text(0.9, 0.5, "ShipProvince\nCategoryName\norderYear\nordermonth",
            ha='center', va='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            transform=ax_kpi.transAxes)

# ==================== 4.2 中间行 (折线图 + 饼图) ====================

# --- 左侧：sales 的总和(按年、季度、月份和日) ---
ax_line = fig.add_subplot(gs[1, 0])
ax_line.plot(daily_sales['OrderDate'], daily_sales['销售金额'], color='#0078D7', linewidth=2)
ax_line.set_title('sales 的总和(按日)', fontsize=12, loc='left', fontweight='bold')
ax_line.set_ylabel('sales 的总和', fontsize=10)
# 格式化 Y 轴为 K（千）
ax_line.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x / 1000:.0f} 千'))
# 设置 X 轴格式
ax_line.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: pd.to_datetime(x).strftime('%m月%d日')))
ax_line.tick_params(axis='x', rotation=0)
ax_line.grid(True, linestyle='--', alpha=0.5)
ax_line.spines['top'].set_visible(False)
ax_line.spines['right'].set_visible(False)

# --- 右侧：sales 的总和(按 CategoryName) 饼图 ---
ax_pie = fig.add_subplot(gs[1, 1])
colors = ['#0078D7', '#1A5A8A', '#E95C42', '#A449A4', '#A3A300', '#8C8C3F', '#D97171', '#3F8C8C']
# 绘制饼图，外侧显示标签和百分比
wedges, texts, autotexts = ax_pie.pie(
    cat_sales['销售金额'],
    labels=cat_sales['CategoryName'],
    autopct=lambda p: f'{p:.1f}%' if p > 3 else '',  # 太小的不显示
    pctdistance=0.75,
    colors=colors,
    startangle=90,
    wedgeprops=dict(width=0.4, edgecolor='w')  # 环形图效果
)
ax_pie.set_title('sales 的总和(按 CategoryName)', fontsize=12, loc='left', fontweight='bold')
# 添加图例
ax_pie.legend(wedges, [f"{row['CategoryName']} {row['销售金额'] / 1000:.1f} 千" for _, row in cat_sales.iterrows()],
              title="CategoryName", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)

# ==================== 4.3 底部行 (柱状图 + 矩形树图) ====================

# --- 左侧：sales 的总和(按 CategoryName) 柱状图 ---
ax_bar = fig.add_subplot(gs[2, 0])
bars = ax_bar.bar(cat_sales['CategoryName'], cat_sales['销售金额'], color='#0078D7', width=0.6)
ax_bar.set_title('sales 的总和(按 CategoryName)', fontsize=12, loc='left', fontweight='bold')
ax_bar.set_ylabel('sales 的总和', fontsize=10)
ax_bar.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x / 1000:.0f} 千'))
ax_bar.tick_params(axis='x', rotation=0)
ax_bar.grid(axis='y', linestyle='--', alpha=0.5)
ax_bar.spines['top'].set_visible(False)
ax_bar.spines['right'].set_visible(False)
# 标签倾斜显示，防止重叠
for label in ax_bar.get_xticklabels():
    label.set_rotation(15)
    label.set_horizontalalignment('right')

# --- 右侧：sales 的总和(按 ShipProvince) 矩形树图 ---
# matplotlib 没有自带矩形树图，这里使用 squarify 库，如果没有安装请先 pip install squarify
try:
    import squarify

    ax_tree = fig.add_subplot(gs[2, 1])

    # 计算百分比标签
    labels = [f"{row['ShipProvince']}\n{row['销售金额'] / 1000:.1f} 千" for _, row in prov_sales.iterrows()]
    # 绘制矩形树图
    squarify.plot(sizes=prov_sales['销售金额'], label=labels, ax=ax_tree,
                  color=plt.cm.tab20.colors, alpha=0.9, text_kwargs={'fontsize': 9, 'color': 'white'})
    ax_tree.axis('off')
    ax_tree.set_title('sales 的总和(按 ShipProvince)', fontsize=12, loc='left', fontweight='bold')
except ImportError:
    ax_tree = fig.add_subplot(gs[2, 1])
    ax_tree.text(0.5, 0.5, "请安装 squarify 库:\npip install squarify", ha='center', va='center')
    ax_tree.axis('off')

# 最终展示
plt.suptitle("销售数据综合分析看板", fontsize=18, fontweight='bold', y=0.95)
plt.tight_layout(rect=[0, 0, 1, 0.93])  # 留出主标题空间
plt.show()