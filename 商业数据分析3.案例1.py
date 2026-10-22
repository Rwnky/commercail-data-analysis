# -*- coding: utf-8 -*-
"""
收入趋势分析看板：读取 案例1：收入趋势分析案例-完整.xlsx
依赖：pandas, matplotlib, openpyxl
运行：python revenue_trend.py
输出：revenue_trend.png
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec

# ---------- 中文 ----------
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans CJK SC']
mpl.rcParams['axes.unicode_minus'] = False

# ---------- 读取数据 ----------
FILE = "案例1：收入趋势分析案例-完整.xlsx"
df = pd.read_excel(FILE, sheet_name="原始数据")
df.columns = ["年份", "月份", "省份", "销售额"]
df["年份"] = df["年份"].astype(int)
df["月份"] = df["月份"].astype(int)
df["销售额"] = pd.to_numeric(df["销售额"], errors="coerce").fillna(0)

# ---------- 1. 年度销售趋势 ----------
year_sales = df.groupby("年份")["销售额"].sum().sort_index()

# ---------- 2. 2020 年月销售 ----------
m2020 = df[df["年份"] == 2020].groupby("月份")["销售额"].sum().reindex(range(1, 13), fill_value=0)

# ---------- 3. 2020 同比 ----------
m2019 = df[df["年份"] == 2019].groupby("月份")["销售额"].sum().reindex(range(1, 13), fill_value=0)
yoy = pd.DataFrame({"2019": m2019, "2020": m2020})
yoy["同比增长率"] = (yoy["2020"] - yoy["2019"]) / yoy["2019"]

# ---------- 4. 2020年11月各省同比 ----------
nov = df[(df["月份"] == 11) & (df["年份"].isin([2019, 2020]))]
nov_pivot = nov.pivot_table(index="省份", columns="年份", values="销售额",
                            aggfunc="sum", fill_value=0).reset_index()
nov_pivot.columns = ["省份", "2019", "2020"]
nov_pivot["同比增长率"] = (nov_pivot["2020"] - nov_pivot["2019"]) / nov_pivot["2019"].replace(0, np.nan)
nov_pivot = nov_pivot.sort_values("2020", ascending=True)

# ---------- 5. 四川省 2019 vs 2020 月度 ----------
sc = df[df["省份"] == "四川"]
sc_pivot = sc.pivot_table(index="月份", columns="年份", values="销售额",
                          aggfunc="sum", fill_value=0).reindex(range(1, 13), fill_value=0)

# ---------- 画布 ----------
fig = plt.figure(figsize=(16, 14), facecolor="white")
gs = GridSpec(3, 2, figure=fig, hspace=0.42, wspace=0.22,
              left=0.06, right=0.97, top=0.95, bottom=0.06)

def style(ax, title):
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=8)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=9)

# ===== 1. 年度销售 =====
ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.bar(year_sales.index.astype(str), year_sales.values,
               color="#2d8cf0", width=0.55)
for b, v in zip(bars, year_sales.values):
    ax1.text(b.get_x() + b.get_width()/2, v + year_sales.max()*0.02,
             f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
style(ax1, "1、年度销售趋势分析")
ax1.set_ylabel("销售额（元）", fontsize=10)
ax1.set_ylim(0, year_sales.max() * 1.15)

# ===== 2. 2020 年月销售 =====
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(m2020.index, m2020.values, color="#2d8cf0", linewidth=2,
         marker="o", markersize=4)
ax2.fill_between(m2020.index, m2020.values, color="#2d8cf0", alpha=0.18)
for x, v in m2020.items():
    ax2.text(x, v + m2020.max()*0.02, f"{v:,.0f}",
             ha="center", va="bottom", fontsize=7.5)
style(ax2, "2、2020年月销售趋势分析")
ax2.set_xticks(range(1, 13))
ax2.set_xlabel("月份", fontsize=10)
ax2.set_ylabel("销售额（元）", fontsize=10)
ax2.set_ylim(0, m2020.max() * 1.18)

# ===== 3. 2020 同比 =====
ax3 = fig.add_subplot(gs[1, :])
x = np.arange(1, 13)
w = 0.38
ax3.bar(x - w/2, yoy["2019"], width=w, color="#b0c4de", label="2019")
ax3.bar(x + w/2, yoy["2020"], width=w, color="#2d8cf0", label="2020")
ax3.set_xticks(x)
ax3.set_xlabel("月份", fontsize=10)
ax3.set_ylabel("销售额（元）", fontsize=10)
style(ax3, "3、2020年销售同比增长率趋势分析")

ax3b = ax3.twinx()
ax3b.plot(x, yoy["同比增长率"] * 100, color="#e2231a", linewidth=1.8,
          marker="o", markersize=4, label="同比增长率")
for xi, v in zip(x, yoy["同比增长率"] * 100):
    if pd.notna(v):
        ax3b.text(xi, v + 2, f"{v:.1f}%", ha="center", va="bottom",
                  fontsize=7.5, color="#e2231a")
ax3b.set_ylabel("同比增长率（%）", fontsize=10, color="#e2231a")
ax3b.tick_params(axis="y", colors="#e2231a")
ax3b.axhline(0, color="#999999", linewidth=0.8, linestyle="--")
for s in ["top"]:
    ax3b.spines[s].set_visible(False)
# 合并图例
h1, l1 = ax3.get_legend_handles_labels()
h2, l2 = ax3b.get_legend_handles_labels()
ax3.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=9)

# ===== 4. 2020年11月各省同比 =====
ax4 = fig.add_subplot(gs[2, 0])
colors = ["#e2231a" if v < 0 else "#2d8cf0" for v in nov_pivot["同比增长率"].fillna(0)]
ypos = np.arange(len(nov_pivot))
ax4.barh(ypos, nov_pivot["同比增长率"].fillna(0) * 100, color=colors, height=0.65)
ax4.set_yticks(ypos)
ax4.set_yticklabels(nov_pivot["省份"], fontsize=8)
ax4.axvline(0, color="#333333", linewidth=1)
style(ax4, "4、2020年11月各省份同比增长情况")
ax4.set_xlabel("同比增长率（%）", fontsize=9)
ax4.grid(axis="x", linestyle="--", alpha=0.35)
ax4.grid(axis="y", visible=False)

# ===== 5. 四川 2019 vs 2020 =====
ax5 = fig.add_subplot(gs[2, 1])
x = np.arange(1, 13)
w = 0.38
ax5.bar(x - w/2, sc_pivot.get(2019, pd.Series(0, index=range(1, 13))),
        width=w, color="#b0c4de", label="2019")
ax5.bar(x + w/2, sc_pivot.get(2020, pd.Series(0, index=range(1, 13))),
        width=w, color="#2d8cf0", label="2020")
ax5.set_xticks(x)
ax5.set_xlabel("月份", fontsize=10)
ax5.set_ylabel("销售额（元）", fontsize=10)
style(ax5, "5、四川省 2019 vs 2020 月度销售对比")
ax5.legend(loc="upper left", frameon=False, fontsize=9)

plt.savefig("revenue_trend.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.show()

# ---------- 控制台输出核对 ----------
print("年度销售：")
print(year_sales)
print("\n2020年月销售：")
print(m2020)
print("\n2020同比：")
print(yoy.round(4))
print("\n11月各省同比（前5）：")
print(nov_pivot.tail(5)[["省份", "2019", "2020", "同比增长率"]].round(4))