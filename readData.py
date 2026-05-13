import pandas as pd

# 读取 user_balance_table.csv 的前10行
df = pd.read_csv('user_balance_table.csv', nrows=10)

# 列出全部列
print("Columns:", df.columns.tolist())

# 显示前10行数据
print(df)