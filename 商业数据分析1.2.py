import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 1. 读取数据 ====================
trans = pd.read_csv('trans.csv', encoding='utf-8')
loans = pd.read_csv('loans.csv', encoding='utf-8')
accounts = pd.read_csv('accounts.csv', encoding='utf-8')
orders = pd.read_csv('order.csv', encoding='utf-8')

# ==================== 2. 数据预处理 ====================

# --- trans.csv 处理 ---
trans['date'] = pd.to_datetime(trans['date'], errors='coerce')
# 金额列可能有逗号，需要清理
trans['amount'] = trans['amount'].astype(str).str.replace(',', '').str.strip()
trans['amount'] = pd.to_numeric(trans['amount'], errors='coerce').fillna(0)

# 提取年份和月份
trans['year'] = trans['date'].dt.year
trans['month'] = trans['date'].dt.month

print("trans.csv 列名:", trans.columns.tolist())
print("trans.csv 类型值:", trans['type'].unique()[:10])
print("trans.csv 操作值:", trans['operation'].unique()[:10])

# --- loans.csv 处理 ---
loans['date'] = pd.to_datetime(loans['date'], errors='coerce')
loans['year'] = loans['date'].dt.year
loans['month'] = loans['date'].dt.month
loans['amount'] = pd.to_numeric(loans['amount'], errors='coerce').fillna(0)

print("\nloans.csv 列名:", loans.columns.tolist())
print("loans.csv 状态值:", loans['status'].unique())

# --- orders.csv 处理 ---
orders['k_symbol'] = orders['k_symbol'].fillna('未知')
orders['amount'] = pd.to_numeric(orders['amount'], errors='coerce').fillna(0)


# ==================== 3. 图表1：按月统计交易金额（可切换年份）====================

def plot_monthly_transaction(year=1993, operation_type='信贷资金'):
    """
    按月统计指定操作类型的交易金额
    """
    df = trans[(trans['year'] == year) & (trans['operation'] == operation_type)]

    monthly = df.groupby('month')['amount'].sum().reindex(range(1, 13), fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 5))

    months = [f'{m}月' for m in range(1, 13)]
    bars = ax.bar(months, monthly.values, color='#4A90D9', edgecolor='#2C5F8A', width=0.7)

    # 在柱子上标注数值
    for bar, val in zip(bars, monthly.values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(monthly.values) * 0.01,
                    f'{val:,.0f}', ha='center', va='bottom', fontsize=8)

    ax.set_title(f'{year}年 各月「{operation_type}」交易总金额', fontsize=14, fontweight='bold')
    ax.set_xlabel('月份', fontsize=12)
    ax.set_ylabel('金额（元）', fontsize=12)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(f'chart1_{year}_{operation_type}.png', dpi=150, bbox_inches='tight')
    plt.show()


# 示例：生成1993年信贷资金月度图
plot_monthly_transaction(1993, '信贷资金')
plot_monthly_transaction(1994, '信贷资金')
plot_monthly_transaction(1993, '从他行收款')
plot_monthly_transaction(1993, '支取现金')


# ==================== 4. 图表2：按月统计交易笔数/金额（可切换指标）====================

def plot_monthly_stats(year=1993, metric='count', operation_type=None):
    """
    按月统计交易笔数或金额
    metric: 'count' 或 'amount'
    operation_type: None 表示全部
    """
    df = trans[trans['year'] == year]
    if operation_type:
        df = df[df['operation'] == operation_type]

    if metric == 'count':
        monthly = df.groupby('month').size().reindex(range(1, 13), fill_value=0)
        ylabel = '交易笔数'
        title = f'{year}年 各月交易笔数'
    else:
        monthly = df.groupby('month')['amount'].sum().reindex(range(1, 13), fill_value=0)
        ylabel = '金额（元）'
        title = f'{year}年 各月交易总金额'

    if operation_type:
        title += f'（{operation_type}）'

    fig, ax = plt.subplots(figsize=(12, 5))
    months = [f'{m}月' for m in range(1, 13)]

    # 折线 + 柱状组合
    ax.bar(months, monthly.values, color='#7BC8A4', edgecolor='#3D8B5E',
           width=0.6, alpha=0.7, label='柱状')
    ax.plot(months, monthly.values, 'o-', color='#E85D4A', linewidth=2,
            markersize=6, label='趋势')

    for i, val in enumerate(monthly.values):
        if val > 0:
            ax.text(i, val + max(monthly.values) * 0.01, f'{val:,.0f}',
                    ha='center', va='bottom', fontsize=7, color='#333')

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('月份', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(f'chart2_{year}_{metric}.png', dpi=150, bbox_inches='tight')
    plt.show()


# 示例
plot_monthly_stats(1993, metric='count')
plot_monthly_stats(1993, metric='amount')
plot_monthly_stats(1994, metric='count')

# ==================== 5. 交互式版本（带年份/月份切换控件）====================

from matplotlib.widgets import RadioButtons, Slider


def interactive_chart():
    """交互式图表 - 可切换年份和指标"""
    years = sorted(trans['year'].dropna().unique().astype(int).tolist())

    fig, ax = plt.subplots(figsize=(13, 6))
    plt.subplots_adjust(left=0.15, bottom=0.2, right=0.9, top=0.9)

    # 控件区域
    ax_year = plt.axes([0.02, 0.4, 0.1, 0.4])
    ax_metric = plt.axes([0.02, 0.15, 0.1, 0.2])

    radio_year = RadioButtons(ax_year, [str(y) for y in years])
    radio_metric = RadioButtons(ax_metric, ['笔数', '金额'])

    def update(_=None):
        year = int(radio_year.value_selected)
        metric = radio_metric.value_selected
        ax.clear()

        df = trans[trans['year'] == year]
        if metric == '笔数':
            monthly = df.groupby('month').size().reindex(range(1, 13), fill_value=0)
            ylabel = '交易笔数'
        else:
            monthly = df.groupby('month')['amount'].sum().reindex(range(1, 13), fill_value=0)
            ylabel = '金额（元）'

        months = [f'{m}月' for m in range(1, 13)]
        bars = ax.bar(months, monthly.values, color='#4A90D9', width=0.65)

        for bar, val in zip(bars, monthly.values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        f'{val:,.0f}', ha='center', va='bottom', fontsize=7)

        ax.set_title(f'{year}年 各月交易{ylabel}', fontsize=14, fontweight='bold')
        ax.set_xlabel('月份');
        ax.set_ylabel(ylabel)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        fig.canvas.draw_idle()

    radio_year.on_clicked(update)
    radio_metric.on_clicked(update)
    update()
    plt.show()


# 取消注释运行交互式图表
# interactive_chart()

# ==================== 6. 贷款相关统计图 ====================

def plot_loans_by_year():
    """按年统计贷款总额和笔数"""
    df = loans.dropna(subset=['year'])

    yearly = df.groupby('year').agg(
        总额=('amount', 'sum'),
        笔数=('amount', 'count')
    )

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    years = yearly.index.astype(int).astype(str)
    ax1.bar(years, yearly['总额'], color='#4A90D9', alpha=0.7, label='贷款总额')
    ax2.plot(years, yearly['笔数'], 'o-', color='#E85D4A', linewidth=2, label='贷款笔数')

    ax1.set_ylabel('贷款总额（元）', fontsize=12)
    ax2.set_ylabel('贷款笔数', fontsize=12)
    ax1.set_title('各年度贷款总额与笔数', fontsize=14, fontweight='bold')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.tight_layout()
    plt.savefig('chart3_loans_by_year.png', dpi=150, bbox_inches='tight')
    plt.show()


plot_loans_by_year()


# ==================== 7. 贷款状态饼图 ====================

def plot_loan_status():
    """贷款状态分布"""
    status_map = {'A': '正常', 'B': '已还清', 'C': '违约', 'D': '延期'}
    df = loans.copy()
    df['状态'] = df['status'].map(status_map).fillna(df['status'])

    counts = df['状态'].value_counts()

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ['#4A90D9', '#7BC8A4', '#E85D4A', '#F5A623']
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index, autopct='%1.1f%%',
        colors=colors[:len(counts)], startangle=90,
        textprops={'fontsize': 12}
    )

    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight('bold')

    ax.set_title('贷款状态分布', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('chart4_loan_status.png', dpi=150, bbox_inches='tight')
    plt.show()


plot_loan_status()


# ==================== 8. 订单按银行统计 ====================

def plot_orders_by_bank(top_n=10):
    """订单金额按银行统计"""
    df = orders.dropna(subset=['bank'])
    bank_stats = df.groupby('bank').agg(
        总额=('amount', 'sum'),
        笔数=('amount', 'count')
    ).sort_values('总额', ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(bank_stats))
    width = 0.35

    ax.bar(x - width / 2, bank_stats['总额'], width, label='总额', color='#4A90D9')
    ax.set_ylabel('金额（元）', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(bank_stats.index, rotation=45, ha='right')

    ax2 = ax.twinx()
    ax2.bar(x + width / 2, bank_stats['笔数'], width, label='笔数', color='#E85D4A', alpha=0.7)
    ax2.set_ylabel('笔数', fontsize=12)

    ax.set_title(f'订单金额Top{top_n}银行', fontsize=14, fontweight='bold')

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.tight_layout()
    plt.savefig('chart5_orders_by_bank.png', dpi=150, bbox_inches='tight')
    plt.show()


plot_orders_by_bank()

print("\n✅ 所有图表已生成完毕！")