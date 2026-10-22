import pandas as pd

# ==========================================
# 1. 读取数据并进行预处理
# ==========================================
# 读取原始数据
df = pd.read_excel('归因分析数据.xlsx', sheet_name='贷款申请表')

# 转换日期格式并提取年月
df['申请日期'] = pd.to_datetime(df['申请日期'])
df['申请年月'] = df['申请日期'].dt.strftime('%Y年%m月')

# 按年月和渠道进行透视统计
# 这里的 df_pivot 就是结果表中“发现问题”模块的渠道构成数据
df_pivot = pd.pivot_table(
    df,
    values='申请书编号（主键）',
    index='申请年月',
    columns='申请渠道',
    aggfunc='count',
    fill_value=0
).reset_index()

# 确保列顺序一致
channels = ['理财经理（柜台）', '手机银行', '自助机']
df_pivot = df_pivot[['申请年月'] + channels]
df_pivot['总计'] = df_pivot[channels].sum(axis=1)

# 计算环比变化率
df_pivot['环比变化率'] = df_pivot['总计'].pct_change()

# ==========================================
# 2. 归因分析计算 (对比 2021年4月 与 2021年5月)
# ==========================================
# 提取4月和5月的数据
apr_data = df_pivot[df_pivot['申请年月'] == '2021年04月'].iloc[0]
may_data = df_pivot[df_pivot['申请年月'] == '2021年05月'].iloc[0]

# 计算差异
diff_total = may_data['总计'] - apr_data['总计']
diff_counter = may_data['理财经理（柜台）'] - apr_data['理财经理（柜台）']
diff_app = may_data['手机银行'] - apr_data['手机银行']
diff_kiosk = may_data['自助机'] - apr_data['自助机']

# 计算贡献度
contrib_total = diff_total / diff_total
contrib_counter = diff_counter / diff_total
contrib_app = diff_app / diff_total
contrib_kiosk = diff_kiosk / diff_total

# 构建归因分析数据框
attribution_df = pd.DataFrame({
    '指标': ['贷款申请量', '理财经理（柜台）申请量', '手机银行申请量', '自助机申请量'],
    '2021年4月': [apr_data['总计'], apr_data['理财经理（柜台）'], apr_data['手机银行'], apr_data['自助机']],
    '2021年5月': [may_data['总计'], may_data['理财经理（柜台）'], may_data['手机银行'], may_data['自助机']],
    '差异': [diff_total, diff_counter, diff_app, diff_kiosk],
    '贡献度': [contrib_total, contrib_counter, contrib_app, contrib_kiosk]
})

# ==========================================
# 3. 计算各渠道贡献度占比趋势
# ==========================================
df_pivot['理财经理占比'] = df_pivot['理财经理（柜台）'] / df_pivot['总计']
df_pivot['手机银行占比'] = df_pivot['手机银行'] / df_pivot['总计']
df_pivot['自助机占比'] = df_pivot['自助机'] / df_pivot['总计']

# 计算整体总计占比
total_counter = df_pivot['理财经理（柜台）'].sum() / df_pivot['总计'].sum()
total_app = df_pivot['手机银行'].sum() / df_pivot['总计'].sum()
total_kiosk = df_pivot['自助机'].sum() / df_pivot['总计'].sum()

# 构建渠道占比数据框，包含总体总计行
ratio_df = df_pivot[['申请年月', '理财经理占比', '手机银行占比', '自助机占比']].copy()
ratio_df.loc[len(ratio_df)] = ['总计', total_counter, total_app, total_kiosk]

# ==========================================
# 4. 输出并保存结果到 Excel
# ==========================================
print("="*50)
print("1. 贷款申请量的变化趋势")
print("="*50)
# 只展示趋势表的前几列
print(df_pivot[['申请年月', '总计', '环比变化率']].to_string(index=False))

print("\n" + "="*50)
print("2. 贷款申请量的渠道构成情况")
print("="*50)
print(df_pivot[['申请年月'] + channels + ['总计']].to_string(index=False))

print("\n" + "="*50)
print("3. 归因分析：贷款申请量变化的原因")
print("="*50)
print(attribution_df.to_string(index=False))

print("\n" + "="*50)
print("4. 各渠道申请量占比趋势")
print("="*50)
print(ratio_df.to_string(index=False))

# 将结果导出为 Excel
with pd.ExcelWriter('归因分析_结果表_Python生成.xlsx') as writer:
    df_pivot[['申请年月', '总计', '环比变化率']].to_excel(writer, sheet_name='申请量趋势', index=False)
    df_pivot[['申请年月'] + channels + ['总计']].to_excel(writer, sheet_name='渠道构成', index=False)
    attribution_df.to_excel(writer, sheet_name='归因分析', index=False)
    ratio_df.to_excel(writer, sheet_name='渠道占比趋势', index=False)

print("\n文件已成功保存为：归因分析_结果表_Python生成.xlsx")