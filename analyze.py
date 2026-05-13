import pandas as pd
import numpy as np

# 读取CSV文件，使用chunksize处理大文件
chunksize = 10000  # 根据内存调整
chunks = pd.read_csv('user_balance_table.csv', chunksize=chunksize)

# 初始化一个列表来收集所有块
all_data = []

for chunk in chunks:
    all_data.append(chunk)

# 合并所有块为一个DataFrame（注意：对于非常大的文件，这可能不现实；考虑采样）
df = pd.concat(all_data, ignore_index=True)

# 如果文件太大，可以采样
# df = df.sample(frac=0.1, random_state=42)  # 采样10%

# 分析所有列的字段含义（推断）
column_descriptions = {
    'user_id': '用户ID',
    'report_date': '报告日期',
    'tBalance': '当天余额',
    'yBalance': '昨天余额',
    'total_purchase_amt': '总购买金额',
    'direct_purchase_amt': '直接购买金额',
    'purchase_bal_amt': '余额购买金额',
    'purchase_bank_amt': '银行购买金额',
    'total_redeem_amt': '总赎回金额',
    'consume_amt': '消费金额',
    'transfer_amt': '转账金额',
    'tftobal_amt': '转到余额金额',
    'tftocard_amt': '转到卡金额',
    'share_amt': '份额金额',
    'category1': '类别1（可能是基金类别）',
    'category2': '类别2（可能是基金类别）',
    'category3': '类别3（可能是基金类别）',
    'category4': '类别4（可能是基金类别）'
}

print("字段含义分析：")
for col, desc in column_descriptions.items():
    print(f"{col}: {desc}")
    if col in df.columns and df[col].dtype in ['int64', 'float64']:
        print(f"  描述性统计: {df[col].describe()}")
    print()

# 重点分析与 total_purchase_amt 和 total_redeem_amt 的相关性
numeric_cols = df.select_dtypes(include=[np.number]).columns
corr_matrix = df[numeric_cols].corr()

print("与 total_purchase_amt 相关性最高的列（前5）：")
purchase_corr = corr_matrix['total_purchase_amt'].sort_values(ascending=False)
print(purchase_corr.head(6))  # 包括自身

print("\n与 total_redeem_amt 相关性最高的列（前5）：")
redeem_corr = corr_matrix['total_redeem_amt'].sort_values(ascending=False)
print(redeem_corr.head(6))  # 包括自身