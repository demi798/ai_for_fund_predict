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

# 添加weekday和day信息
train_data['date'] = pd.to_datetime(train_data['report_date'], format='%Y%m%d')
train_data['weekday'] = train_data['date'].dt.weekday
train_data['day_of_month'] = train_data['date'].dt.day

# 步骤1：计算weekday因子（作为乘数）
print("\n步骤1：计算weekday因子...")
# 申购总金额
weekday_purchase_mean = train_data.groupby('weekday')['total_purchase_amt'].mean()
overall_purchase_mean = train_data['total_purchase_amt'].mean()
weekday_purchase_factor = weekday_purchase_mean / overall_purchase_mean

# 赎回总金额
weekday_redeem_mean = train_data.groupby('weekday')['total_redeem_amt'].mean()
overall_redeem_mean = train_data['total_redeem_amt'].mean()
weekday_redeem_factor = weekday_redeem_mean / overall_redeem_mean

print("申购总金额weekday因子（相对倍数，0=Monday, 6=Sunday）：")
for day in range(7):
    day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day]
    if day in weekday_purchase_factor.index:
        print(f"  {day_name}: {weekday_purchase_factor[day]:.4f}")

# 步骤2：计算day（日期号）因子（作为乘数）
print("\n步骤2：计算day（日期号）因子...")
# 申购总金额
day_purchase_mean = train_data.groupby('day_of_month')['total_purchase_amt'].mean()
day_purchase_factor = day_purchase_mean / overall_purchase_mean

# 赎回总金额
day_redeem_mean = train_data.groupby('day_of_month')['total_redeem_amt'].mean()
day_redeem_factor = day_redeem_mean / overall_redeem_mean

print("申购总金额day因子（相对倍数，1-31号）：")
for day in sorted(day_purchase_factor.index):
    if day <= 10:  # 只打印前10号
        print(f"  {day:2d}号: {day_purchase_factor[day]:.4f}")
print("  ...")

# 步骤3：计算长期趋势
print("\n步骤3：计算长期趋势...")
train_data['days_since_start'] = (train_data['date'] - train_data['date'].min()).dt.days
train_data_sorted = train_data.sort_values('days_since_start')

# 使用简单线性回归计算趋势
from numpy.polynomial import Polynomial

# 申购总金额趋势
p_purchase = Polynomial.fit(train_data_sorted['days_since_start'].values, 
                            train_data_sorted['total_purchase_amt'].values, 1)
coef_purchase = p_purchase.convert().coef
trend_purchase_slope = coef_purchase[1]

# 赎回总金额趋势
p_redeem = Polynomial.fit(train_data_sorted['days_since_start'].values, 
                          train_data_sorted['total_redeem_amt'].values, 1)
coef_redeem = p_redeem.convert().coef
trend_redeem_slope = coef_redeem[1]

print(f"申购总金额日均增长率：{trend_purchase_slope:,.2f}")
print(f"赎回总金额日均增长率：{trend_redeem_slope:,.2f}")
print(f"训练期申购总金额平均值：{overall_purchase_mean:,.0f}")
print(f"训练期赎回总金额平均值：{overall_redeem_mean:,.0f}")

# 步骤4：生成预测（使用weekday × day的乘法关系）
print("\n步骤4：生成预测...")
start_date = datetime(2014, 9, 1)
end_date = datetime(2014, 9, 30)
predictions = []

current_date = start_date
days_from_train_end = (start_date - train_data['date'].max()).days

while current_date <= end_date:
    report_date_str = current_date.strftime('%Y%m%d')
    weekday = current_date.weekday()
    day_of_month = current_date.day
    
    # 获取weekday因子
    if weekday in weekday_purchase_factor.index:
        weekday_factor_purchase = weekday_purchase_factor[weekday]
        weekday_factor_redeem = weekday_redeem_factor[weekday]
    else:
        weekday_factor_purchase = 1.0
        weekday_factor_redeem = 1.0
    
    # 获取day因子（注意9月只有30天）
    if day_of_month in day_purchase_factor.index:
        day_factor_purchase = day_purchase_factor[day_of_month]
        day_factor_redeem = day_redeem_factor[day_of_month]
    else:
        # 如果该天在历史数据中没有出现，使用平均因子
        day_factor_purchase = 1.0
        day_factor_redeem = 1.0
    
    # 计算趋势调整的基础值
    days_delta = (current_date - train_data['date'].max()).days
    base_purchase = overall_purchase_mean + trend_purchase_slope * days_delta
    base_redeem = overall_redeem_mean + trend_redeem_slope * days_delta
    
    # 使用weekday × day的乘法关系进行预测
    pred_purchase = base_purchase * weekday_factor_purchase * day_factor_purchase
    pred_redeem = base_redeem * weekday_factor_redeem * day_factor_redeem
    
    # 确保预测值为正数
    pred_purchase = max(pred_purchase, 0)
    pred_redeem = max(pred_redeem, 0)
    
    predictions.append({
        'report_date': report_date_str,
        'total_purchase_amt': int(pred_purchase),
        'total_redeem_amt': int(pred_redeem)
    })
    
    current_date += timedelta(days=1)

# 创建结果DataFrame
result_df = pd.DataFrame(predictions)

# 写入CSV文件，不需要header和index
result_df.to_csv('result3.csv', header=False, index=False)

print("\n预测结果已保存到 result3.csv")
print("\n预测结果示例（前10行）：")
print(result_df.head(10))
print("\n预测结果统计：")
print(f"申购总金额预测平均值：{result_df['total_purchase_amt'].mean():,.0f}")
print(f"赎回总金额预测平均值：{result_df['total_redeem_amt'].mean():,.0f}")
print(f"申购总金额预测范围：{result_df['total_purchase_amt'].min():,.0f} - {result_df['total_purchase_amt'].max():,.0f}")
print(f"赎回总金额预测范围：{result_df['total_redeem_amt'].min():,.0f} - {result_df['total_redeem_amt'].max():,.0f}")

# 输出周期因子详细信息
print("\n\n===== 周期因子详细信息 =====")
print("\n申购总金额weekday因子：")
for day in range(7):
    day_name = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][day]
    if day in weekday_purchase_factor.index:
        print(f"  {day_name}: {weekday_purchase_factor[day]:.4f}")

print("\n赎回总金额weekday因子：")
for day in range(7):
    day_name = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][day]
    if day in weekday_redeem_factor.index:
        print(f"  {day_name}: {weekday_redeem_factor[day]:.4f}")

print("\n申购总金额day因子（按日期号1-31）：")
for day in sorted(day_purchase_factor.index):
    print(f"  {day:2d}号: {day_purchase_factor[day]:.4f}", end="  ")
    if day % 5 == 0:
        print()

print("\n\n赎回总金额day因子（按日期号1-31）：")
for day in sorted(day_redeem_factor.index):
    print(f"  {day:2d}号: {day_redeem_factor[day]:.4f}", end="  ")
    if day % 5 == 0:
        print()
