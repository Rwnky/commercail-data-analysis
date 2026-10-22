import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.dates as mdates
import warnings

warnings.filterwarnings("ignore")

# ==========================================
# 全局图表样式设置（尽量还原 WPS/Excel 默认风格）
# ==========================================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # 支持中文
plt.rcParams['axes.unicode_minus'] = False


def plot_time_series(history_series, forecast_series, conf_int, title, ylabel, is_ln=False):
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='white')

    # 1. 绘制历史数据 (蓝色折线)
    ax.plot(history_series.index, history_series, color='#1a73e8', linewidth=2, label='历史数据')

    # 2. 绘制预测值的置信区间 (灰色阴影)
    # 截取最后一段历史数据使其与预测连线更平滑
    last_date = history_series.index[-1]
    last_val = history_series.iloc[-1]

    # 将预测数据的开头接上历史的结尾，为了图形连贯
    forecast_plot = pd.concat([pd.Series([last_val], index=[last_date]), forecast_series])
    ci_lower = pd.concat([pd.Series([last_val], index=[last_date]), conf_int.iloc[:, 0]])
    ci_upper = pd.concat([pd.Series([last_val], index=[last_date]), conf_int.iloc[:, 1]])

    ax.fill_between(ci_lower.index, ci_lower, ci_upper, color='#d3d3d3', alpha=0.6, label='95% 置信区间')

    # 3. 绘制预测均值 (深灰色折线)
    ax.plot(forecast_plot.index, forecast_plot, color='#555555', linewidth=1.5, linestyle='-', label='预测值')

    # 4. 图表装饰
    ax.set_title(title, loc='left', fontsize=12, pad=10)
    ax.set_ylabel(ylabel, fontsize=10)

    # 去除右边和上边的边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')

    # 设置网格线 (虚线)
    ax.grid(True, linestyle='--', color='#e0e0e0', alpha=0.7)

    # 设置X轴日期格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y年'))
    ax.xaxis.set_major_locator(mdates.YearLocator())

    # 添加图例
    ax.legend(loc='upper left', frameon=False)

    plt.tight_layout()
    plt.show()


# ==========================================
# 案例 1：航空乘客数据 (原始 AIR)
# ==========================================
print("正在生成图 1：AIR 的总和按 DATE...")
# 1. 读取数据
df_air = pd.read_excel('AirPassengers.xlsx', sheet_name='AirPassengers', usecols="A:B").dropna()
df_air['DATE'] = pd.to_datetime(df_air['DATE'])
df_air.set_index('DATE', inplace=True)
series_air = df_air['AIR']

# 2. 拟合 SARIMA 模型 (预测未来24个月)
model_air = SARIMAX(series_air, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12),
                    enforce_stationarity=False, enforce_invertibility=False)
results_air = model_air.fit(disp=False)
forecast_air = results_air.get_forecast(steps=24)
pred_air = forecast_air.predicted_mean
ci_air = forecast_air.conf_int()

# 3. 画图
plot_time_series(series_air, pred_air, ci_air,
                 title='AIR 的总和按 DATE', ylabel='AIR 的总和')

# ==========================================
# 案例 2：航空乘客数据 (取对数 ln_AIR)
# ==========================================
print("正在生成图 2：ln_AIR 的总和按 年和 月份...")
# 1. 读取数据 (提取C列 ln_AIR)
df_ln = pd.read_excel('AirPassengers.xlsx', sheet_name='AirPassengers', usecols="A,C").dropna()
df_ln.columns = ['DATE', 'ln_AIR']
df_ln['DATE'] = pd.to_datetime(df_ln['DATE'])
df_ln.set_index('DATE', inplace=True)
series_ln = df_ln['ln_AIR']

# 2. 拟合 SARIMA 模型
model_ln = SARIMAX(series_ln, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12),
                   enforce_stationarity=False, enforce_invertibility=False)
results_ln = model_ln.fit(disp=False)
forecast_ln = results_ln.get_forecast(steps=24)
pred_ln = forecast_ln.predicted_mean
ci_ln = forecast_ln.conf_int()

# 3. 画图
plot_time_series(series_ln, pred_ln, ci_ln,
                 title='ln_AIR 的总和按 年和 月份', ylabel='ln_AIR 的总和')