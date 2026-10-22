# -*- coding: utf-8 -*-
"""
复现截图：零售金额指标拆解树（杜邦分析图）
依赖：matplotlib
运行：python draw_retail_tree.py
输出：retail_tree.png
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib as mpl

# ---------- 中文与负号 ----------
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans CJK SC']
mpl.rcParams['axes.unicode_minus'] = False

# ---------- 画布 ----------
FIG_W, FIG_H = 10, 14
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, 100)
ax.set_ylim(0, 140)
ax.axis('off')

# ---------- 节点数据 ----------
# 结构：(x, y, 主值, 主标签, 副值, 副标签, 是否红色强调)
nodes = {
    "root":   (38, 125, "3333189", "零售金额",     "3.21%",  "零售金额环比", False),

    "disc":   (14, 100, "76.58%",  "折扣率",       "-1.04%", "折扣率环比",   True),
    "amt":    (48, 100, "2552700", "成交金额",     "1.83%",  "成交金额环比", False),

    "vip":    (28,  72, "1101",    "会员人数",     "-29",    "会员人数环比", True),
    "per":    (62,  72, "2076",    "会员人均消费", "3.31%",  "会员人均消费环比", False),

    "order":  (48,  46, "1664",    "订单数",       "5",      "订单数环比",   False),
    "atv":    (78,  46, "1534",    "客单价",       "1.53%",  "客单价环比",   False),

    "attach": (34,  18, "1.31",    "连带率",       "0.02",   "连带率环比",   False),
    "qty":    (55,  18, "2186",    "件数",         "41",     "件数环比",     False),
    "unitp":  (76,  18, "1168",    "件单价",       "-0.08%", "件单价环比",   True),
}

# 连线关系（父子）
edges = [
    ("root", "disc"), ("root", "amt"),
    ("amt", "vip"),   ("amt", "per"),
    ("per", "order"), ("per", "atv"),
    ("order", "attach"), ("order", "qty"), ("atv", "unitp"),
]

# ---------- 卡片绘制 ----------
BOX_W, BOX_H = 20, 13

def draw_card(x, y, main_val, main_label, sub_val, sub_label, highlight=False):
    """以 (x,y) 为中心画一张卡片"""
    left = x - BOX_W / 2
    bottom = y - BOX_H / 2

    # 阴影
    shadow = FancyBboxPatch(
        (left + 0.6, bottom - 0.6), BOX_W, BOX_H,
        boxstyle="round,pad=0.2,rounding_size=0.4",
        linewidth=0, facecolor="#cccccc", alpha=0.45, zorder=1
    )
    ax.add_patch(shadow)

    # 卡片主体
    card = FancyBboxPatch(
        (left, bottom), BOX_W, BOX_H,
        boxstyle="round,pad=0.2,rounding_size=0.4",
        linewidth=0.8, edgecolor="#dddddd", facecolor="white", zorder=2
    )
    ax.add_patch(card)

    # 左侧红色竖条（强调）
    if highlight:
        ax.plot([left - 0.1, left - 0.1], [bottom + 1, bottom + BOX_H - 1],
                color="#e2231a", linewidth=2.2, solid_capstyle="round", zorder=3)

    # 主值
    ax.text(left + 1.2, y + 3.2, main_val, fontsize=13, color="#000000",
            ha="left", va="center", zorder=4)
    # 主标签
    ax.text(left + 1.2, y + 0.2, main_label, fontsize=11, color="#333333",
            ha="left", va="center", zorder=4)
    # 副值
    ax.text(left + 1.2, y - 2.8, sub_val, fontsize=10.5,
            color="#e2231a" if highlight else "#333333",
            ha="left", va="center", zorder=4)
    # 副标签
    ax.text(left + 1.2, y - 5.2, sub_label, fontsize=10.5,
            color="#e2231a" if highlight else "#555555",
            ha="left", va="center", zorder=4)

# ---------- 先画连线（在卡片下层） ----------
for p, c in edges:
    px, py = nodes[p][0], nodes[p][1]
    cx, cy = nodes[c][0], nodes[c][1]
    # 从父卡片底部中点连到子卡片顶部中点，用折线更像截图
    x1, y1 = px, py - BOX_H / 2 - 0.2
    x2, y2 = cx, cy + BOX_H / 2 + 0.2
    mid_y = (y1 + y2) / 2
    ax.plot([x1, x1], [y1, mid_y], color="#c8a165", linewidth=1.1, zorder=0)
    ax.plot([x1, x2], [mid_y, mid_y], color="#c8a165", linewidth=1.1, zorder=0)
    ax.plot([x2, x2], [mid_y, y2], color="#c8a165", linewidth=1.1, zorder=0)

# ---------- 再画卡片 ----------
for key, (x, y, mv, ml, sv, sl, hl) in nodes.items():
    draw_card(x, y, mv, ml, sv, sl, highlight=hl)

# ---------- 标题区（可选，模拟顶部 tab） ----------
ax.text(50, 136, "指标分析", ha="center", va="center", fontsize=12,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#2d2d2d",
                  edgecolor="none"), color="white")
ax.text(78, 136, "店铺分析", ha="center", va="center", fontsize=11,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                  edgecolor="#2d2d2d"), color="#2d2d2d")

plt.tight_layout()
plt.savefig("retail_tree.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.show()