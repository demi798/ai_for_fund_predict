import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体 - macOS系统自带字体
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10

# 读取CSV文件，使用chunksize处理大文件
print("正在读取数据...")
chunksize = 50000
chunks = []

for chunk in pd.read_csv('user_balance_table.csv', chunksize=chunksize):
    chunks.append(chunk)

df = pd.concat(chunks, ignore_index=True)

# 转换report_date为日期格式
# report_date似乎是整数格式（如20130701），需要转换为datetime
df['report_date'] = pd.to_datetime(df['report_date'], format='%Y%m%d')

# 按report_date分组，对total_purchase_amt和total_redeem_amt求和
print("正在聚合数据...")
daily_flow = df.groupby('report_date').agg({
    'total_purchase_amt': 'sum',
    'total_redeem_amt': 'sum'
}).reset_index()

# 按日期排序
daily_flow = daily_flow.sort_values('report_date')

print(f"数据范围：{daily_flow['report_date'].min()} 到 {daily_flow['report_date'].max()}")
print(f"总记录数：{len(daily_flow)}")

# 绘制走势图
plt.figure(figsize=(14, 6))

# 绘制申购总金额
plt.plot(daily_flow['report_date'], daily_flow['total_purchase_amt'], 
         marker='o', linestyle='-', linewidth=2, label='申购总金额 (total_purchase_amt)', color='#2E86AB')

# 绘制赎回总金额
plt.plot(daily_flow['report_date'], daily_flow['total_redeem_amt'], 
         marker='s', linestyle='-', linewidth=2, label='赎回总金额 (total_redeem_amt)', color='#A23B72')

plt.xlabel('日期 (Report Date)', fontsize=12, fontweight='bold')
plt.ylabel('金额 (Amount)', fontsize=12, fontweight='bold')
plt.title('资金流入流出走势图 (Fund Inflow/Outflow Trend)', fontsize=14, fontweight='bold')
plt.legend(fontsize=11, loc='best')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

# 保存图片
plt.savefig('fund_flow_trend.png', dpi=300, bbox_inches='tight')
print("图片已保存为 fund_flow_trend.png")

plt.show()

# 输出统计信息
print("\n统计信息：")
print(f"申购总金额：{daily_flow['total_purchase_amt'].sum():,.2f}")
print(f"赎回总金额：{daily_flow['total_redeem_amt'].sum():,.2f}")
print(f"\n申购总金额平均值：{daily_flow['total_purchase_amt'].mean():,.2f}")
print(f"赎回总金额平均值：{daily_flow['total_redeem_amt'].mean():,.2f}")
