import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("正在读取数据...")
# 读取user_balance_table.csv
chunksize = 50000
chunks = []

for chunk in pd.read_csv('user_balance_table.csv', chunksize=chunksize):
    chunks.append(chunk)

df = pd.concat(chunks, ignore_index=True)

# 转换report_date为字符串格式，并确保是整数格式YYYYMMDD
df['report_date'] = df['report_date'].astype(str).str.zfill(8)

# 按report_date分组，对total_purchase_amt和total_redeem_amt求和
print("正在聚合数据...")
daily_flow = df.groupby('report_date').agg({
    'total_purchase_amt': 'sum',
    'total_redeem_amt': 'sum'
}).reset_index()

# 按日期排序
daily_flow = daily_flow.sort_values('report_date')

# 截取20140301到20140831的数据作为训练数据
print("截取数据阶段：20140301-20140831...")
train_data = daily_flow[(daily_flow['report_date'] >= '20140301') & 
                        (daily_flow['report_date'] <= '20140831')].copy()

print(f"训练数据范围：{train_data['report_date'].min()} 到 {train_data['report_date'].max()}")
print(f"训练数据记录数：{len(train_data)}")

# 添加weekday信息（0=Monday, 6=Sunday）
train_data['date'] = pd.to_datetime(train_data['report_date'], format='%Y%m%d')
train_data['weekday'] = train_data['date'].dt.weekday
train_data['day_of_month'] = train_data['date'].dt.day

# 步骤1：按weekday计算每个工作日的平均值
print("\n步骤1：计算weekday周期因子...")
weekday_purchase = train_data.groupby('weekday')['total_purchase_amt'].mean()
weekday_redeem = train_data.groupby('weekday')['total_redeem_amt'].mean()

print("申购总金额按weekday的平均值（0=Monday, 6=Sunday）：")
for day in range(7):
    day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day]
    if day in weekday_purchase.index:
        print(f"  {day_name}: {weekday_purchase[day]:,.0f}")

# 步骤2：计算长期趋势
print("\n步骤2：计算长期趋势...")
train_data['days_since_start'] = (train_data['date'] - train_data['date'].min()).dt.days
train_data_sorted = train_data.sort_values('days_since_start')

# 使用简单线性回归计算趋势
from numpy.polynomial import Polynomial

# 申购总金额趋势
p_purchase = Polynomial.fit(train_data_sorted['days_since_start'].values, 
                            train_data_sorted['total_purchase_amt'].values, 1)
coef_purchase = p_purchase.convert().coef
trend_purchase_slope = coef_purchase[1]  # 斜率

# 赎回总金额趋势
p_redeem = Polynomial.fit(train_data_sorted['days_since_start'].values, 
                          train_data_sorted['total_redeem_amt'].values, 1)
coef_redeem = p_redeem.convert().coef
trend_redeem_slope = coef_redeem[1]

print(f"申购总金额日均增长率：{trend_purchase_slope:,.2f}")
print(f"赎回总金额日均增长率：{trend_redeem_slope:,.2f}")

# 计算训练期的平均值
train_purchase_mean = train_data['total_purchase_amt'].mean()
train_redeem_mean = train_data['total_redeem_amt'].mean()

print(f"训练期申购总金额平均值：{train_purchase_mean:,.0f}")
print(f"训练期赎回总金额平均值：{train_redeem_mean:,.0f}")

# 步骤3：生成预测日期和预测
print("\n步骤3：生成预测...")
start_date = datetime(2014, 9, 1)
end_date = datetime(2014, 9, 30)
pred_dates = []
predictions = []

current_date = start_date
days_from_train_end = (start_date - train_data['date'].max()).days

while current_date <= end_date:
    report_date_str = current_date.strftime('%Y%m%d')
    weekday = current_date.weekday()
    
    # 基础预测：使用weekday的平均值
    if weekday in weekday_purchase.index:
        base_purchase = weekday_purchase[weekday]
        base_redeem = weekday_redeem[weekday]
    else:
        base_purchase = train_purchase_mean
        base_redeem = train_redeem_mean
    
    # 趋势调整：计算从训练期末到预测日期的天数，应用线性趋势
    days_delta = (current_date - train_data['date'].max()).days
    trend_purchase = base_purchase + trend_purchase_slope * days_delta
    trend_redeem = base_redeem + trend_redeem_slope * days_delta
    
    # 确保预测值为正数
    pred_purchase = max(trend_purchase, 0)
    pred_redeem = max(trend_redeem, 0)
    
    pred_dates.append(report_date_str)
    predictions.append({
        'report_date': report_date_str,
        'total_purchase_amt': int(pred_purchase),
        'total_redeem_amt': int(pred_redeem)
    })
    
    current_date += timedelta(days=1)

# 创建结果DataFrame
result_df = pd.DataFrame(predictions)

# 写入CSV文件，不需要header和index
result_df.to_csv('result2.csv', header=False, index=False)

print("\n预测结果已保存到 result2.csv")
print("\n预测结果示例（前10行）：")
print(result_df.head(10))
print("\n预测结果统计：")
print(f"申购总金额预测平均值：{result_df['total_purchase_amt'].mean():,.0f}")
print(f"赎回总金额预测平均值：{result_df['total_redeem_amt'].mean():,.0f}")
print(f"申购总金额预测范围：{result_df['total_purchase_amt'].min():,.0f} - {result_df['total_purchase_amt'].max():,.0f}")
print(f"赎回总金额预测范围：{result_df['total_redeem_amt'].min():,.0f} - {result_df['total_redeem_amt'].max():,.0f}")
