# -*- coding: utf-8 -*-
"""
人力资源看板：读取 员工信息.xlsx，复现截图的看板布局
依赖：pandas, matplotlib, openpyxl
运行：python hr_dashboard.py
输出：hr_dashboard.png
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec
from datetime import datetime

# ---------- 中文字体 ----------
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans CJK SC']
mpl.rcParams['axes.unicode_minus'] = False

# ---------- 读取数据 ----------
FILE = "员工信息.xlsx"
df = pd.read_excel(FILE, sheet_name="员工信息")

# 日期列转 datetime
for col in ["出生日期", "入职日期", "离职日期"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

# 查询区间（截图顶部日期）
START = pd.Timestamp("2022-01-01")
END   = pd.Timestamp("2022-12-31")
LAST_MONTH_START = pd.Timestamp("2022-11-01")
LAST_MONTH_END   = pd.Timestamp("2022-11-30")

# ---------- 计算指标 ----------
# 期末在职：在 END 时点，入职<=END 且（离职为空 或 离职>END）
mask_active_end = (df["入职日期"] <= END) & (df["离职日期"].isna() | (df["离职日期"] > END))
active_end = mask_active_end.sum()

# 员工人数：区间内曾在职过的人（入职<=END 且（离职为空 或 离职>=START））
mask_ever = (df["入职日期"] <= END) & (df["离职日期"].isna() | (df["离职日期"] >= START))
emp_total = mask_ever.sum()

# 离职人数：离职日期落在区间内
mask_leave = df["离职日期"].notna() & (df["离职日期"] >= START) & (df["离职日期"] <= END)
leave_total = mask_leave.sum()

# 上月离职人数
mask_leave_last = df["离职日期"].notna() & (df["离职日期"] >= LAST_MONTH_START) & (df["离职日期"] <= LAST_MONTH_END)
leave_last = mask_leave_last.sum()

# 离职人数月环比（相对上月）
leave_mom = (leave_total - leave_last) / leave_last if leave_last else np.nan

# ---------- 年龄段分布 ----------
def age_group(birth):
    if pd.isna(birth):
        return "未知"
    # 以 END 为基准算年龄
    age = END.year - birth.year - ((END.month, END.day) < (birth.month, birth.day))
    if age < 30:
        return "30岁以下"
    elif age < 40:
        return "30-40"
    elif age < 50:
        return "40-50"
    else:
        return "50岁以上"

df["年龄段"] = df["出生日期"].apply(age_group)
df["在职状态_end"] = mask_active_end
df["离职_区间"] = mask_leave

age_order = ["30岁以下", "30-40", "40-50", "50岁以上"]
age_stat = df.groupby("年龄段").agg(
    员工人数=("员工工号", lambda s: df.loc[s.index][mask_ever.loc[s.index]].shape[0]),
    离职人数=("员工工号", lambda s: df.loc[s.index][mask_leave.loc[s.index]].shape[0]),
    期末在职=("员工工号", lambda s: df.loc[s.index][mask_active_end.loc[s.index]].shape[0]),
).reindex(age_order).fillna(0).astype(int)

# ---------- 按月统计 ----------
months = pd.date_range("2022-01-01", "2022-12-01", freq="MS")
month_labels = [m.strftime("%Y-%m") for m in months]

emp_by_month = []
leave_by_month = []
for m in months:
    m_end = m + pd.offsets.MonthEnd(0)
    # 该月末在职人数
    act = ((df["入职日期"] <= m_end) &
           (df["离职日期"].isna() | (df["离职日期"] > m_end))).sum()
    # 该月离职人数
    lv = (df["离职日期"].notna() &
          (df["离职日期"] >= m) & (df["离职日期"] <= m_end)).sum()
    emp_by_month.append(act)
    leave_by_month.append(lv)

# ---------- 明细表（在职/离职天数） ----------
def days_in_company(row):
    start = row["入职日期"]
    if pd.isna(start):
        return np.nan
    end = row["离职日期"] if pd.notna(row["离职日期"]) else END
    return max((end - start).days, 0)

df["员工在职天数"] = df.apply(days_in_company, axis=1)

table_cols = ["部门", "员工工号", "姓名", "文化程度", "员工状态",
              "入职日期", "离职日期", "员工在职天数"]
table_df = df[table_cols].copy()
table_df["入职日期"] = table_df["入职日期"].dt.strftime("%Y年%m月%d日").fillna("")
table_df["离职日期"] = table_df["离职日期"].dt.strftime("%Y年%m月%d日").fillna("")
table_df = table_df.head(6)

# ---------- 画布 ----------
fig = plt.figure(figsize=(12, 9), facecolor="white")
gs = GridSpec(4, 2, figure=fig,
              height_ratios=[0.7, 0.7, 2.6, 3.0],
              width_ratios=[1.1, 1.0],
              hspace=0.45, wspace=0.12,
              left=0.05, right=0.97, top=0.97, bottom=0.05)

# ===== 1. 标题 =====
ax_title = fig.add_subplot(gs[0, 0])
ax_title.axis("off")
ax_title.add_patch(FancyBboxPatch((0.02, 0.1), 0.96, 0.8,
                                  boxstyle="round,pad=0.02,rounding_size=0.03",
                                  facecolor="white", edgecolor="#d0d0d0",
                                  linewidth=1.2, transform=ax_title.transAxes))
ax_title.text(0.5, 0.5, "XX公司人力资源看板", ha="center", va="center",
              fontsize=22, fontweight="bold", transform=ax_title.transAxes)

# ===== 2. 日期筛选区（示意） =====
ax_date = fig.add_subplot(gs[0, 1])
ax_date.axis("off")
ax_date.add_patch(FancyBboxPatch((0.02, 0.1), 0.96, 0.8,
                                 boxstyle="round,pad=0.02,rounding_size=0.03",
                                 facecolor="white", edgecolor="#d0d0d0",
                                 linewidth=1.2, transform=ax_date.transAxes))
ax_date.text(0.06, 0.82, "Date", fontsize=10, transform=ax_date.transAxes)
ax_date.text(0.06, 0.55, "2022/1/1", fontsize=11, transform=ax_date.transAxes,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#f5f5f5", edgecolor="#d0d0d0"))
ax_date.text(0.30, 0.55, "2022/12/31", fontsize=11, transform=ax_date.transAxes,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#f5f5f5", edgecolor="#d0d0d0"))
# 简单滑杆示意
ax_date.plot([0.55, 0.90], [0.45, 0.45], color="#cccccc", linewidth=2, transform=ax_date.transAxes)
ax_date.scatter([0.65, 0.85], [0.45, 0.45], s=120, facecolor="white",
                edgecolor="#888888", linewidth=1.5, transform=ax_date.transAxes, zorder=3)

# ===== 3. 顶部 KPI 卡片 =====
ax_kpi = fig.add_subplot(gs[1, 1])
ax_kpi.axis("off")
ax_kpi.add_patch(FancyBboxPatch((0.02, 0.05), 0.96, 0.9,
                                boxstyle="round,pad=0.02,rounding_size=0.03",
                                facecolor="white", edgecolor="#d0d0d0",
                                linewidth=1.2, transform=ax_kpi.transAxes))
kpis = [
    (0.08, "82", "期末在职的人数"),
    (0.38, "31", "员工人数"),
    (0.68, "42", "离职的人数"),
]
# 注：以上固定数字仅为版式示意，实际值见下方动态值
kpis = [
    (0.08, f"{active_end}", "期末在职的人数"),
    (0.38, f"{emp_total}", "员工人数"),
    (0.68, f"{leave_total}", "离职的人数"),
]
for x, val, label in kpis:
    ax_kpi.text(x, 0.68, val, fontsize=14, fontweight="bold",
                transform=ax_kpi.transAxes)
    ax_kpi.text(x, 0.38, label, fontsize=9, color="#555555",
                transform=ax_kpi.transAxes)
# 下方两个数字
ax_kpi.text(0.08, 0.20, f"{leave_last}", fontsize=12, fontweight="bold",
            transform=ax_kpi.transAxes)
ax_kpi.text(0.08, 0.02, "离职人数上月", fontsize=9, color="#555555",
            transform=ax_kpi.transAxes)
mom_str = f"{leave_mom*100:.2f}%" if pd.notna(leave_mom) else "-"
ax_kpi.text(0.38, 0.20, mom_str, fontsize=12, fontweight="bold",
            color="#e2231a" if (pd.notna(leave_mom) and leave_mom < 0) else "#2d6bb5",
            transform=ax_kpi.transAxes)
ax_kpi.text(0.38, 0.02, "离职人数月环比", fontsize=9, color="#555555",
            transform=ax_kpi.transAxes)

# ===== 4. 各年龄段数据分布（水平堆叠条形图） =====
ax_age = fig.add_subplot(gs[1:3, 0])
ax_age.add_patch(FancyBboxPatch((0.01, 0.01), 0.98, 0.98,
                                boxstyle="round,pad=0.01,rounding_size=0.02",
                                facecolor="white", edgecolor="#d0d0d0",
                                linewidth=1.0, transform=ax_age.transAxes, zorder=0))

y = np.arange(len(age_order))
h = 0.26
colors = {"员工人数": "#111111", "离职的人数": "#d94b4b", "期末在职的人数": "#e8772e"}

ax_age.barh(y + h, age_stat["员工人数"], height=h, color=colors["员工人数"],
            label="员工人数", zorder=2)
ax_age.barh(y,     age_stat["离职人数"], height=h, color=colors["离职的人数"],
            label="离职的人数", zorder=2)
ax_age.barh(y - h, age_stat["期末在职"], height=h, color=colors["期末在职的人数"],
            label="期末在职的人数", zorder=2)

# 数值标签
for i, v in enumerate(age_stat["员工人数"]):
    ax_age.text(v + 0.5, i + h, str(v), va="center", fontsize=9)
for i, v in enumerate(age_stat["离职人数"]):
    ax_age.text(v + 0.5, i, str(v), va="center", fontsize=9)
for i, v in enumerate(age_stat["期末在职"]):
    ax_age.text(v + 0.5, i - h, str(v), va="center", fontsize=9)

ax_age.set_yticks(y)
ax_age.set_yticklabels(age_order, fontsize=10)
ax_age.set_xlabel("员工人数，离职的人数和 期末在职的…", fontsize=9)
ax_age.set_title("各年龄段数据分布", fontsize=14, pad=10)
ax_age.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=3,
              frameon=False, fontsize=8, markerscale=0.8)
ax_age.grid(axis="x", linestyle="--", alpha=0.4, zorder=1)
ax_age.set_xlim(0, max(age_stat.max()) * 1.25 + 1)
# 去掉上/右边框
for s in ["top", "right"]:
    ax_age.spines[s].set_visible(False)

# ===== 5. 员工人数和离职人数（按月）面积折线图 =====
ax_line = fig.add_subplot(gs[2, 1])
ax_line.add_patch(FancyBboxPatch((0.01, 0.01), 0.98, 0.98,
                                 boxstyle="round,pad=0.01,rounding_size=0.02",
                                 facecolor="white", edgecolor="#d0d0d0",
                                 linewidth=1.0, transform=ax_line.transAxes, zorder=0))

x = np.arange(len(month_labels))
ax_line.plot(x, emp_by_month, color="#2d6bb5", linewidth=1.8, marker="o",
             markersize=3, label="员工人数", zorder=3)
ax_line.plot(x, leave_by_month, color="#1f3a93", linewidth=1.8, marker="o",
             markersize=3, label="离职的人数", zorder=3)
ax_line.fill_between(x, emp_by_month, color="#2d6bb5", alpha=0.25, zorder=2)
ax_line.fill_between(x, leave_by_month, color="#1f3a93", alpha=0.25, zorder=2)

ax_line.set_xticks(x[::2])
ax_line.set_xticklabels([m[5:] for m in month_labels][::2], fontsize=8)
ax_line.set_ylabel("员工人数", fontsize=9)
ax_line.set_title("员工人数和 离职的人数(按 年月)", fontsize=14, pad=8, loc="left")
ax_line.legend(loc="upper left", frameon=False, fontsize=8)
ax_line.grid(axis="y", linestyle="--", alpha=0.4)
for s in ["top", "right"]:
    ax_line.spines[s].set_visible(False)

# ===== 6. 明细表 =====
ax_tbl = fig.add_subplot(gs[3, :])
ax_tbl.axis("off")
ax_tbl.add_patch(FancyBboxPatch((0.005, 0.02), 0.99, 0.96,
                                boxstyle="round,pad=0.005,rounding_size=0.01",
                                facecolor="white", edgecolor="#d0d0d0",
                                linewidth=1.0, transform=ax_tbl.transAxes, zorder=0))

# 表头
headers = ["部门", "员工\n工号", "姓名", "文化\n程度", "员工\n状态",
           "入职日期", "离职日\n期", "员工在\n职天数"]
col_x = [0.02, 0.12, 0.20, 0.29, 0.37, 0.45, 0.57, 0.69]
header_y = 0.90
for cx, h in zip(col_x, headers):
    ax_tbl.text(cx, header_y, h, fontsize=9, fontweight="bold",
                va="center", transform=ax_tbl.transAxes)
ax_tbl.plot([0.01, 0.99], [0.85, 0.85], color="#999999", linewidth=0.8,
            transform=ax_tbl.transAxes)

# 行
row_y_start = 0.78
row_h = 0.105
for i, (_, row) in enumerate(table_df.iterrows()):
    ry = row_y_start - i * row_h
    vals = [
        str(row["部门"]),
        str(row["员工工号"]),
        str(row["姓名"]),
        str(row["文化程度"]),
        str(row["员工状态"]),
        str(row["入职日期"]),
        str(row["离职日期"]) if row["离职日期"] else "",
        str(int(row["员工在职天数"])) if pd.notna(row["员工在职天数"]) else "",
    ]
    for cx, v in zip(col_x, vals):
        ax_tbl.text(cx, ry, v, fontsize=8.5, va="center",
                    transform=ax_tbl.transAxes)
    if i < len(table_df) - 1:
        ax_tbl.plot([0.01, 0.99], [ry - row_h * 0.55, ry - row_h * 0.55],
                    color="#eeeeee", linewidth=0.6, transform=ax_tbl.transAxes)

# 简单的滚动条示意
ax_tbl.add_patch(FancyBboxPatch((0.01, 0.0), 0.98, 0.015,
                                boxstyle="round,pad=0.0,rounding_size=0.005",
                                facecolor="#e0e0e0", edgecolor="none",
                                transform=ax_tbl.transAxes))
ax_tbl.add_patch(FancyBboxPatch((0.01, 0.0), 0.75, 0.015,
                                boxstyle="round,pad=0.0,rounding_size=0.005",
                                facecolor="#999999", edgecolor="none",
                                transform=ax_tbl.transAxes))

plt.savefig("hr_dashboard.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.show()
print("已生成 hr_dashboard.png")
print(f"期末在职={active_end}, 员工人数={emp_total}, 离职人数={leave_total}, "
      f"上月离职={leave_last}, 月环比={mom_str}")