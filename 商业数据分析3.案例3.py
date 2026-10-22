import pandas as pd
import numpy as np

# ============================================================
# 1. 读取原始数据
# ============================================================
# 假设原始数据在Excel的"原始数据"sheet中
df = pd.read_excel("案例3：电商平台的精准营销-完整案例.xlsx", sheet_name="原始数据")

# 查看数据基本信息
print("数据形状:", df.shape)
print("列名:", df.columns.tolist())
print(df.head())

# ============================================================
# 2. 数据清洗与年龄分段
# ============================================================
# 原始数据中"客户年龄段（计算）"列是公式，pandas读取时可能为NaN
# 需要用年龄列重新计算年龄段

def age_group(age):
    if 18 <= age <= 25:
        return "18-25岁"
    elif 26 <= age <= 35:
        return "26-35岁"
    elif 36 <= age <= 49:
        return "36-49岁"
    else:
        return "50岁以上"

df["客户年龄段（计算）"] = df["年龄"].apply(age_group)

# 检查年龄范围
print("年龄范围:", df["年龄"].min(), "-", df["年龄"].max())
print("年龄段分布:\n", df["客户年龄段（计算）"].value_counts())

# ============================================================
# 分析1：购买客户的性别分布
# ============================================================
print("\n" + "="*50)
print("1、购买客户的性别分布")
print("="*50)

gender_dist = df["性别"].value_counts().reset_index()
gender_dist.columns = ["性别", "客户数"]
# 调整顺序：Female在前
gender_dist = gender_dist.set_index("性别").reindex(["Female", "Male"]).reset_index()
total_gender = gender_dist["客户数"].sum()
gender_dist.loc[len(gender_dist)] = ["总计", total_gender]
print(gender_dist.to_string(index=False))

# ============================================================
# 分析2：女性消费客户的年龄段分布
# ============================================================
print("\n" + "="*50)
print("2、女性消费客户的年龄段分布")
print("="*50)

female_df = df[df["性别"] == "Female"]

# 年龄段分布
age_dist = female_df["客户年龄段（计算）"].value_counts().reset_index()
age_dist.columns = ["年龄段", "客户数"]
# 按年龄顺序排列
age_order = ["18-25岁", "26-35岁", "36-49岁", "50岁以上"]
age_dist = age_dist.set_index("年龄段").reindex(age_order).reset_index()
total_female = age_dist["客户数"].sum()
age_dist.loc[len(age_dist)] = ["总计", total_female]
print(age_dist.to_string(index=False))

# 附：按具体年龄的客户数分布（对应准备区A18:B72）
print("\n按具体年龄的客户数分布：")
age_detail = female_df["年龄"].value_counts().sort_index().reset_index()
age_detail.columns = ["年龄", "客户数"]
print(age_detail.to_string(index=False))

# ============================================================
# 分析3：50岁以上女性客户的消费品类分布
# ============================================================
print("\n" + "="*50)
print("3、50岁以上的女性客户的消费品类分布")
print("="*50)

female_50plus = female_df[female_df["客户年龄段（计算）"] == "50岁以上"]

category_dist = female_50plus["品类"].value_counts().reset_index()
category_dist.columns = ["品类", "客户数"]
category_dist = category_dist.sort_values("客户数", ascending=False)
total_cat = category_dist["客户数"].sum()
category_dist.loc[len(category_dist)] = ["总计", total_cat]
print(category_dist.to_string(index=False))

# ============================================================
# 分析4：50岁以上女性服饰和护肤品消费人群的支付方式分布
# ============================================================
print("\n" + "="*50)
print("4、50岁以上女性服饰和护肤品消费人群的支付方式分布")
print("="*50)

# 服饰(Clothing) + 护肤品(Cosmetics)
target_categories = ["Clothing", "Cosmetics"]
female_50plus_target = female_50plus[female_50plus["品类"].isin(target_categories)]

print(f"目标人群数量（服饰+护肤品）: {len(female_50plus_target)}")

payment_dist = female_50plus_target["支付方式"].value_counts().reset_index()
payment_dist.columns = ["支付方式", "客户数"]
payment_dist = payment_dist.sort_values("客户数", ascending=False)
total_pay = payment_dist["客户数"].sum()
payment_dist.loc[len(payment_dist)] = ["总计", total_pay]
print(payment_dist.to_string(index=False))

# ============================================================
# 验证与准备区结果对比
# ============================================================
print("\n" + "="*50)
print("结果验证（与准备区对比）")
print("="*50)

expected = {
    "Female客户数": 2371,
    "Male客户数": 1555,
    "18-25岁": 265,
    "26-35岁": 313,
    "36-49岁": 412,
    "50岁以上": 565,
    "50+女性Clothing": 310,
    "50+女性Cosmetics": 135,
    "50+女性服饰+护肤": 445,
    "Alipay": 150,
    "Card": 201,
    "WeChat Pay": 94,
}

actual = {
    "Female客户数": len(df[df["性别"]=="Female"]),
    "Male客户数": len(df[df["性别"]=="Male"]),
    "18-25岁": len(female_df[female_df["客户年龄段（计算）"]=="18-25岁"]),
    "26-35岁": len(female_df[female_df["客户年龄段（计算）"]=="26-35岁"]),
    "36-49岁": len(female_df[female_df["客户年龄段（计算）"]=="36-49岁"]),
    "50岁以上": len(female_50plus),
    "50+女性Clothing": len(female_50plus[female_50plus["品类"]=="Clothing"]),
    "50+女性Cosmetics": len(female_50plus[female_50plus["品类"]=="Cosmetics"]),
    "50+女性服饰+护肤": len(female_50plus_target),
    "Alipay": len(female_50plus_target[female_50plus_target["支付方式"]=="Alipay"]),
    "Card": len(female_50plus_target[female_50plus_target["支付方式"]=="Card"]),
    "WeChat Pay": len(female_50plus_target[female_50plus_target["支付方式"]=="WeChat Pay"]),
}

for k in expected:
    status = "✓" if expected[k] == actual[k] else "✗"
    print(f"{status} {k}: 期望={expected[k]}, 实际={actual[k]}")