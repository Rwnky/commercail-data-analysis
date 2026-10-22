
# -*- coding: utf-8 -*-
"""
小学考试成绩看板：读取 学生及老师信息.xlsx + 考试记录.xlsx
依赖：pandas, matplotlib, openpyxl
运行：python exam_dashboard.py
输出：exam_dashboard.png
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
stu = pd.read_excel("学生及老师信息.xlsx", sheet_name="学生信息")
tea = pd.read_excel("学生及老师信息.xlsx", sheet_name="教师信息")
score = pd.read_excel("考试记录.xlsx", sheet_name="考试记录")

# 合并
df = score.merge(stu, on="学号", how="left").merge(tea, on="班级", how="left")

# 总分 / 排名
df["总分"] = df["语文"] + df["数学"] + df["英语"]
df["总分排名"] = df["总分"].rank(ascending=False, method="min").astype(int)

# ---------- 全局 KPI ----------
max_score = df["总分"].max()
min_score = df["总分"].min()
avg_score = df["总分"].mean().round(2)

pass_line = 60
pass_chinese  = (df["语文"] >= pass_line).sum()
pass_math     = (df["数学"] >= pass_line).sum()
pass_english  = (df["英语"] >= pass_line).sum()
total_stu     = len(df)

rate_chinese = pass_chinese / total_stu
rate_math    = pass_math / total_stu
rate_english = pass_english / total_stu

# 任意一门挂科（<60）
fail_any = ((df["语文"] < 60) | (df["数学"] < 60) | (df["英语"] < 60)).sum()
# 数学 60-90 分人数
math_60_90 = ((df["数学"] >= 60) & (df["数学"] <= 90)).sum()

# 语文 60-80
chinese_60_80 = ((df["语文"] >= 60) & (df["语文"] <= 80)).sum()

# 参加考试人数（按总分分组）
bins   = [0, 180, 260, 9999]
labels = ["180分及以下", "181-220分", "221-260分", "261及以上"]
# 截图顺序：221-260、181-220、261及以上、180分及以下
group_counts = {
    "221-260分": ((df["总分"] >= 221) & (df["总分"] <= 260)).sum(),
    "181-220分": ((df["总分"] >= 181) & (df["总分"] <= 220)).sum(),
    "261分及以上": (df["总分"] >= 261).sum(),
    "180分及以下": (df["总分"] <= 180).sum(),
}
group_order = ["221-260分", "181-220分", "261分及以上", "180分及以下"]

# 班主任统计
teacher_stat = df.groupby("班主任姓名").agg(
    学生人数=("学号", "count"),
    一班学生人数=("班级", lambda s: (s == 1).sum()),
    学生总人数=("学号", "count"),
).reset_index()
teacher_stat.loc[len(teacher_stat)] = ["总计", len(df), (df["班级"] == 1).sum(), len(df)]

# 班级筛选条数据
class_counts = df["班级"].value_counts().sort_index()

# ---------- 画布 ----------
fig = plt.figure(figsize=(16, 10), facecolor="white")
gs = GridSpec(6, 3, figure=fig,
              height_ratios=[0.9, 0.8, 0.9, 0.9, 1.6, 2.6],
              width_ratios=[1.2, 1.0, 1.0],
              hspace=0.55, wspace=0.15,
              left=0.04, right=0.98, top=0.96, bottom=0.04)

def card(ax, pad=0.01):
    ax.add_patch(FancyBboxPatch((pad, pad), 1 - 2*pad, 1 - 2*pad,
                                boxstyle="round,pad=0.005,rounding_size=0.01",
                                facecolor="white", edgecolor="#cfcfcf",
                                linewidth=1.0, transform=ax.transAxes, zorder=0))
    ax.set_xticks([]); ax.set_yticks([])

# ===== 1. 标题 =====
ax_title = fig.add_subplot(gs[0, :])
ax_title.axis("off")
ax_title.add_patch(FancyBboxPatch((0.01, 0.05), 0.98, 0.9,
                                  boxstyle="round,pad=0.01,rounding_size=0.02",
                                  facecolor="white", edgecolor="#cfcfcf",
                                  linewidth=1.2, transform=ax_title.transAxes))
ax_title.text(0.5, 0.5, "小学考试成绩看板", ha="center", va="center",
              fontsize=26, fontweight="bold", color="#c00000",
              transform=ax_title.transAxes)

# ===== 2. 班级切换条 =====
ax_class = fig.add_subplot(gs[1, :])
ax_class.axis("off")
ax_class.text(0.0, 1.1, "班级", fontsize=9, transform=ax_class.transAxes)
box_w, gap = 0.30, 0.02
x0 = 0.01
for i, c in enumerate([1, 2, 3]):
    x = x0 + i * (box_w + gap)
    ax_class.add_patch(FancyBboxPatch((x, 0.1), box_w, 0.8,
                                      boxstyle="square,pad=0",
                                      facecolor="white", edgecolor="#999999",
                                      linewidth=1.0, transform=ax_class.transAxes))
    ax_class.text(x + box_w/2, 0.5, str(c), ha="center", va="center",
                  fontsize=16, fontweight="bold", transform=ax_class.transAxes)
# 底部横线
ax_class.plot([0.0, 0.99], [0.05, 0.05], color="#888888", linewidth=1.2, transform=ax_class.transAxes)

# ===== 3. 顶部 KPI（分数） =====
ax_kpi_score = fig.add_subplot(gs[2, :])
ax_kpi_score.axis("off")
card(ax_kpi_score)
kpis = [
    (0.05, f"{max_score}", "最高分"),
    (0.20, f"{min_score}", "最低分"),
    (0.38, f"{avg_score}", "平均分"),
    (0.60, f"{pass_chinese}", "语文及格人数"),
    (0.74, f"{pass_math}", "数学及格人数"),
    (0.88, f"{pass_english}", "英语及格人数"),
]
for x, v, lab in kpis:
    ax_kpi_score.text(x, 0.65, v, fontsize=17, fontweight="bold", transform=ax_kpi_score.transAxes)
    ax_kpi_score.text(x, 0.25, lab, fontsize=9, color="#555555", transform=ax_kpi_score.transAxes)

# ===== 4. 及格率 KPI =====
ax_kpi_rate = fig.add_subplot(gs[3, 1:])
ax_kpi_rate.axis("off")
card(ax_kpi_rate)
rates = [
    (0.05, f"{rate_chinese*100:.2f}%", "语文及格率"),
    (0.38, f"{rate_math*100:.2f}%", "数学及格率"),
    (0.70, f"{rate_english*100:.2f}%", "英语及格率"),
]
for x, v, lab in rates:
    ax_kpi_rate.text(x, 0.65, v, fontsize=17, fontweight="bold", transform=ax_kpi_rate.transAxes)
    ax_kpi_rate.text(x, 0.25, lab, fontsize=9, color="#555555", transform=ax_kpi_rate.transAxes)

# ===== 5. 分组柱状图 =====
ax_bar = fig.add_subplot(gs[4:6, 0])
card(ax_bar)
ax_bar.set_xticks([]); ax_bar.set_yticks([])  # 重置 card
card(ax_bar)
ax_bar_in = ax_bar.inset_axes([0.12, 0.15, 0.80, 0.70])
vals = [group_counts[k] for k in group_order]
bars = ax_bar_in.bar(group_order, vals, color="#2d8cf0", width=0.6)
for b, v in zip(bars, vals):
    ax_bar_in.text(b.get_x() + b.get_width()/2, v + 0.5, str(v),
                   ha="center", va="bottom", fontsize=9)
ax_bar_in.set_ylabel("考试人数", fontsize=9)
ax_bar_in.set_xlabel("分组", fontsize=9)
ax_bar_in.set_title("参加考试的学生人数(按 分组)", fontsize=12, loc="left", pad=6)
ax_bar_in.grid(axis="y", linestyle="--", alpha=0.4)
ax_bar_in.set_ylim(0, max(vals) * 1.25 + 1)
for s in ["top", "right"]:
    ax_bar_in.spines[s].set_visible(False)
ax_bar_in.tick_params(labelsize=8)

# ===== 6. 班主任统计表 =====
ax_tbl_tea = fig.add_subplot(gs[3, 0])
ax_tbl_tea.axis("off")
card(ax_tbl_tea)
ax_tbl_tea.text(0.02, 0.86, "班主任姓名  学生人数  一班的学生人数  学生总人数",
                fontsize=8, fontweight="bold", transform=ax_tbl_tea.transAxes)
ax_tbl_tea.plot([0.01, 0.99], [0.80, 0.80], color="#888888", linewidth=0.8,
                transform=ax_tbl_tea.transAxes)
row_y = 0.66
for _, r in teacher_stat.iterrows():
    ax_tbl_tea.text(0.03, row_y, str(r["班主任姓名"]), fontsize=8.5, transform=ax_tbl_tea.transAxes)
    ax_tbl_tea.text(0.30, row_y, str(r["学生人数"]), fontsize=8.5, transform=ax_tbl_tea.transAxes)
    ax_tbl_tea.text(0.55, row_y, str(r["一班学生人数"]), fontsize=8.5, transform=ax_tbl_tea.transAxes)
    ax_tbl_tea.text(0.80, row_y, str(r["学生总人数"]), fontsize=8.5, transform=ax_tbl_tea.transAxes)
    row_y -= 0.16

# ===== 7. 语文 60-80 / 任意挂科等 KPI =====
ax_kpi_mid = fig.add_subplot(gs[4, 1])
ax_kpi_mid.axis("off")
ax_kpi_mid.text(0.05, 0.70, f"{chinese_60_80}", fontsize=22, fontweight="bold", transform=ax_kpi_mid.transAxes)
ax_kpi_mid.text(0.05, 0.40, "语文60-80人数", fontsize=9, color="#555555", transform=ax_kpi_mid.transAxes)

ax_kpi_mid2 = fig.add_subplot(gs[4, 2])
ax_kpi_mid2.axis("off")
ax_kpi_mid2.text(0.05, 0.70, f"{fail_any}", fontsize=22, fontweight="bold", transform=ax_kpi_mid2.transAxes)
ax_kpi_mid2.text(0.05, 0.40, "有任意一门挂科的学生人数", fontsize=9, color="#555555", transform=ax_kpi_mid2.transAxes)

ax_kpi_mid3 = fig.add_subplot(gs[5, 1])
ax_kpi_mid3.axis("off")
ax_kpi_mid3.text(0.05, 0.70, f"{math_60_90}", fontsize=22, fontweight="bold", transform=ax_kpi_mid3.transAxes)
ax_kpi_mid3.text(0.05, 0.40, "数学60-90分的人数", fontsize=9, color="#555555", transform=ax_kpi_mid3.transAxes)

# ===== 8. 成绩明细表 =====
ax_tbl = fig.add_subplot(gs[4:6, 1:])
card(ax_tbl)
cols = ["学号", "语文", "数学", "英语", "总分", "总分排名"]
col_x = [0.03, 0.18, 0.32, 0.46, 0.60, 0.76]
ax_tbl.text(col_x[0], 0.93, cols[0], fontsize=10, fontweight="bold", transform=ax_tbl.transAxes)
for cx, c in zip(col_x[1:], cols[1:]):
    ax_tbl.text(cx, 0.93, c, fontsize=10, fontweight="bold", transform=ax_tbl.transAxes)
ax_tbl.plot([0.01, 0.99], [0.88, 0.88], color="#333333", linewidth=1.0, transform=ax_tbl.transAxes)

show = df[cols].sort_values("总分排名").head(13)
row_y = 0.80
row_h = 0.058
for i, (_, r) in enumerate(show.iterrows()):
    for cx, c in zip(col_x, cols):
        val = str(int(r[c])) if c in ("语文", "数学", "英语", "总分", "总分排名") else str(r[c])
        ax_tbl.text(cx, row_y, val, fontsize=8.5, transform=ax_tbl.transAxes)
    if i % 2 == 0:
        ax_tbl.add_patch(FancyBboxPatch((0.01, row_y - 0.018), 0.98, 0.048,
                                        boxstyle="square,pad=0", facecolor="#f3f3f3",
                                        edgecolor="none", transform=ax_tbl.transAxes, zorder=0))
    row_y -= row_h

# 滚动条示意
ax_tbl.add_patch(FancyBboxPatch((0.02, 0.0), 0.96, 0.012,
                                boxstyle="round,pad=0,rounding_size=0.004",
                                facecolor="#e0e0e0", edgecolor="none", transform=ax_tbl.transAxes))
ax_tbl.add_patch(FancyBboxPatch((0.02, 0.0), 0.70, 0.012,
                                boxstyle="round,pad=0,rounding_size=0.004",
                                facecolor="#999999", edgecolor="none", transform=ax_tbl.transAxes))

plt.savefig("exam_dashboard.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.show()
print("已生成 exam_dashboard.png")
print(f"最高分={max_score}, 最低分={min_score}, 平均分={avg_score}")
print(f"及格人数：语文={pass_chinese}, 数学={pass_math}, 英语={pass_english}")
print(f"及格率：语文={rate_chinese:.2%}, 数学={rate_math:.2%}, 英语={rate_english:.2%}")
print(f"任意挂科={fail_any}, 数学60-90={math_60_90}, 语文60-80={chinese_60_80}")