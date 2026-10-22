# -*- coding: utf-8 -*-
"""
财务费用分析看板：读取 案例2：财务费用分析-完整案例.xlsx
依赖：pandas, matplotlib, openpyxl
运行：python expense_analysis.py
输出：expense_analysis.png
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.gridspec import GridSpec

# ---------- 中文 ----------
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans CJK SC']
mpl.rcParams['axes.unicode_minus'] = False

# ---------- 读取数据 ----------
FILE = "案例2：财务费用分析-完整案例.xlsx"
df_total = pd.read_excel(FILE, sheet_name="总费用数据-原始数据")
df_period = pd.read_excel(FILE, sheet_name="财务三大期间费用-原始数据")
df_admin = pd.read_excel(FILE, sheet_name="管理费用-原始数据")

# 统一月份格式为 int（6/7）
def month_to_int(x):
    if isinstance(x, str):
        return int(x.replace("月", ""))
    return int(x)

df_total["月份"] = df_total["月份"].apply(month_to_int)
df_period["月份"] = df_period["月份"].astype(int)
df_admin["月份"] = df_admin["月份"].astype(int)

# ---------- 1. 总财务费用对比 ----------
total_pivot = df_total.pivot_table(index="月份", values="金额", aggfunc="sum").sort_index()
total_diff = total_pivot.loc[7, "金额"] - total_pivot.loc[6, "金额"]
total_rate = total_diff / total_pivot.loc[6, "金额"]

# ---------- 2. 三大期间费用 ----------
period_pivot = df_period.pivot_table(index="期间费用项", columns="月份",
                                     values="金额", aggfunc="sum").fillna(0)
period_pivot["环比差额"] = period_pivot[7] - period_pivot[6]
period_pivot["环比增长率"] = period_pivot["环比差额"] / period_pivot[6].replace(0, np.nan)
period_pivot = period_pivot.sort_values("环比差额", ascending=True)

# ---------- 3. 管理费用明细 ----------
admin_pivot = df_admin.pivot_table(index="管理费用项", columns="月份",
                                   values="金额", aggfunc="sum").fillna(0)
admin_pivot["环比差额"] = admin_pivot[7] - admin_pivot[6]
admin_pivot["环比增长率"] = admin_pivot["环比差额"] / admin_pivot[6].replace(0, np.nan)
admin_pivot = admin_pivot.sort_values("环比增长率", ascending=True)

# ---------- 画布 ----------
fig = plt.figure(figsize=(16, 11), facecolor="white")
gs = GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.28,
              left=0.07, right=0.96, top=0.94, bottom=0.07)

def style(ax, title):
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=8)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=9)

# ===== 1. 总财务费用对比 =====
ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.bar(["6月", "7月"],
               [total_pivot.loc[6, "金额"], total_pivot.loc[7, "金额"]],
               color=["#b0c4de", "#2d8cf0"], width=0.45)
for b, v in zip(bars, [total_pivot.loc[6, "金额"], total_pivot.loc[7, "金额"]]):
    ax1.text(b.get_x() + b.get_width()/2, v + max(total_pivot["金额"])*0.02,
             f"{v:,.0f}", ha="center", va="bottom", fontsize=10)
ax1.set_ylabel("金额（元）", fontsize=10)
style(ax1, "1、总财务费用对比分析（6月 vs 7月）")
ax1.set_ylim(0, max(total_pivot["金额"]) * 1.18)

# ===== 2. 三大期间费用 =====
ax2 = fig.add_subplot(gs[0, 1])
x = np.arange(len(period_pivot))
w = 0.36
b1 = ax2.bar(x - w/2, period_pivot[6], width=w, color="#b0c4de", label="6月")
b2 = ax2.bar(x + w/2, period_pivot[7], width=w, color="#2d8cf0", label="7月")
ax2.set_xticks(x)
ax2.set_xticklabels(period_pivot.index, fontsize=10)
ax2.set_ylabel("金额（元）", fontsize=10)
style(ax2, "2、三大期间财务费用7月较6月增长情况")
ax2.legend(loc="upper right", frameon=False, fontsize=9)

# 环比差额标签
for xi, diff in zip(x, period_pivot["环比差额"]):
    vmax = max(period_pivot.loc[period_pivot.index[xi], 6],
               period_pivot.loc[period_pivot.index[xi], 7])
    color = "#e2231a" if diff > 0 else "#2e8b57"
    sign = "+" if diff > 0 else ""
    ax2.text(xi + w/2, vmax + max(period_pivot[7].max(), period_pivot[6].max())*0.03,
             f"{sign}{diff:,.0f}", ha="center", va="bottom",
             fontsize=8.5, color=color)
ax2.set_ylim(0, max(period_pivot[6].max(), period_pivot[7].max()) * 1.20)

# ===== 3. 管理费用明细环比 =====
ax3 = fig.add_subplot(gs[1, :])
y = np.arange(len(admin_pivot))
colors = ["#e2231a" if v > 0 else "#2e8b57" for v in admin_pivot["环比增长率"].fillna(0)]
ax3.barh(y, admin_pivot["环比增长率"].fillna(0) * 100,
         color=colors, height=0.6)
ax3.set_yticks(y)
ax3.set_yticklabels(admin_pivot.index, fontsize=9.5)
ax3.axvline(0, color="#333333", linewidth=1)
style(ax3, "3、管理费用各明细项 7月环比增长分析")
ax3.set_xlabel("环比增长率（%）", fontsize=10)
ax3.grid(axis="x", linestyle="--", alpha=0.35)
ax3.grid(axis="y", visible=False)

# 增长率 + 差额标签
for yi, (name, row) in enumerate(admin_pivot.iterrows()):
    rate = row["环比增长率"]
    diff = row["环比差额"]
    if pd.notna(rate):
        txt = f"{rate*100:+.2f}%（{diff:+,.0f}元）"
        xpos = rate * 100
        if rate >= 0:
            ax3.text(xpos + 0.4, yi, txt, va="center", ha="left", fontsize=8)
        else:
            ax3.text(xpos - 0.4, yi, txt, va="center", ha="right", fontsize=8)

plt.savefig("expense_analysis.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.show()

# ---------- 控制台核对 ----------
print("总费用 6月/7月：")
print(total_pivot)
print(f"7月较6月差额：{total_diff:,.0f}，环比增长：{total_rate:.2%}\n")

print("三大期间费用：")
print(period_pivot.round(2))
print()

print("管理费用明细（按环比增长率升序）：")
print(admin_pivot.round(4))