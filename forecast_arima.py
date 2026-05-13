import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

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

# 截取20140301到20140831的数据
print("截取数据阶段：20140301-20140831...")
train_data = daily_flow[(daily_flow['report_date'] >= '20140301') & 
                        (daily_flow['report_date'] <= '20140831')].copy()

print(f"训练数据范围：{train_data['report_date'].min()} 到 {train_data['report_date'].max()}")
print(f"训练数据记录数：{len(train_data)}")

# 准备预测日期：20140901到20140930
from datetime import datetime, timedelta

start_date = datetime(2014, 9, 1)
end_date = datetime(2014, 9, 30)
pred_dates = []
current_date = start_date

while current_date <= end_date:
    pred_dates.append(current_date.strftime('%Y%m%d'))
    current_date += timedelta(days=1)

print(f"\n预测日期数量：{len(pred_dates)}")

# 使用ARIMA(7,1,7)分别对两个指标进行建模和预测
print("\n开始ARIMA(7,1,7)建模...")

# 申购总金额ARIMA模型
print("建模 total_purchase_amt...")
try:
    model_purchase = ARIMA(train_data['total_purchase_amt'].values, order=(7, 1, 7))
    fitted_purchase = model_purchase.fit()
    pred_purchase = fitted_purchase.forecast(steps=len(pred_dates))
    print(f"申购总金额预测完成")
except Exception as e:
    print(f"申购总金额建模出错：{e}")
    # 如果ARIMA失败，使用均值作为预测值
    pred_purchase = [train_data['total_purchase_amt'].mean()] * len(pred_dates)

# 赎回总金额ARIMA模型
print("建模 total_redeem_amt...")
try:
    model_redeem = ARIMA(train_data['total_redeem_amt'].values, order=(7, 1, 7))
    fitted_redeem = model_redeem.fit()
    pred_redeem = fitted_redeem.forecast(steps=len(pred_dates))
    print(f"赎回总金额预测完成")
except Exception as e:
    print(f"赎回总金额建模出错：{e}")
    # 如果ARIMA失败，使用均值作为预测值
    pred_redeem = [train_data['total_redeem_amt'].mean()] * len(pred_dates)

# 创建结果DataFrame
result_df = pd.DataFrame({
    'report_date': pred_dates,
    'total_purchase_amt': pred_purchase,
    'total_redeem_amt': pred_redeem
})

# 转换为整数（参考comp_predict_table.csv的格式）
result_df['total_purchase_amt'] = result_df['total_purchase_amt'].astype(int)
result_df['total_redeem_amt'] = result_df['total_redeem_amt'].astype(int)

# 只保留需要的列，按照comp_predict_table.csv的格式
result_df = result_df[['report_date', 'total_purchase_amt', 'total_redeem_amt']]

# 写入CSV文件，不需要header和index
result_df.to_csv('result.csv', header=False, index=False)

print("\n预测结果已保存到 result.csv")
print("\n预测结果示例（前5行）：")
print(result_df.head())
print("\n预测结果统计：")
print(f"申购总金额预测平均值：{result_df['total_purchase_amt'].mean():,.0f}")
print(f"赎回总金额预测平均值：{result_df['total_redeem_amt'].mean():,.0f}")
