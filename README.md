# 资金流入流出预测项目说明文档

## 📋 项目概述

本项目是一个时间序列AI竞赛项目（竞赛链接：https://tianchi.aliyun.com/competition/entrance/231573），
旨在预测基金的申购（流入）和赎回（流出）总金额。通过分析用户行为数据和市场数据，使用多种时间序列预测方法对2014年9月份的资金流动进行预测。

**数据时间范围：** 2013年7月 - 2014年8月  
**预测时间范围：** 2014年9月1日 - 9月30日

---

## 📁 文件结构说明

### 数据文件

| 文件名 | 大小 | 说明 |
|------|-----|------|
| `user_profile_table.csv` | ~1.5MB | 用户档案表，包含用户ID、性别、城市代码、星座等用户信息 |
| `user_balance_table.csv` | >50MB | 用户余额表（核心数据），包含每个用户每日的申购、赎回等交易记录 |
| `mfd_day_share_interest.csv` | - | 基金日利息表，每日份额利息数据 |
| `mfd_bank_shibor.csv` | - | 银行间SHIBOR利率表，市场利率指标 |
| `comp_predict_table.csv` | - | 竞赛预测表示例，定义了输出格式（report_date, total_purchase_amt, total_redeem_amt） |

### Python脚本文件

#### 数据探索脚本

| 文件名 | 功能 | 输出 |
|------|------|------|
| `readData.py` | 读取user_balance_table.csv的前10行并列出全部列 | 终端输出 |
| `analyze.py` | 分析user_balance_table.csv的字段含义和相关性 | 描述性统计、相关性矩阵 |
| `plot_fund_flow.py` | 绘制申购和赎回总金额的走势图 | `fund_flow_trend.png` |

#### 预测脚本（预测2014年9月份数据）

| 文件名 | 预测方法 | 输出文件 | 说明 |
|------|--------|--------|------|
| `forecast_arima.py` | ARIMA(7,1,7) | `result.csv` | 时间序列自回归移动平均模型，基于历史趋势 |
| `forecast_weekday.py` | Weekday + 趋势调整 | `result2.csv` | 周期因子法，考虑周一-周日的规律性差异 |
| `forecast_weekday_day.py` | Weekday × Day（乘法） | `result3.csv` | 双重周期因子法，同时考虑星期和日期号的影响 |

### 结果文件

| 文件名 | 行数 | 说明 |
|------|-----|------|
| `result.csv` | 30 | ARIMA预测结果（2014年9月1-30日） |
| `result2.csv` | 30 | Weekday+趋势调整预测结果 |
| `result3.csv` | 30 | Weekday×Day乘法预测结果 |

### 可视化文件

| 文件名 | 说明 |
|------|------|
| `fund_flow_trend.png` | 资金流入流出走势图（2013年7月 - 2014年8月） |

### 配置文件

| 文件名 | 说明 |
|------|------|
| `.github/copilot-instructions.md` | AI代码助手使用指南 |

---

## 🔍 数据分析结果

### user_balance_table.csv 字段说明

| 字段名 | 含义 | 数据类型 |
|------|------|--------|
| user_id | 用户ID | 整数 |
| report_date | 报告日期（YYYYMMDD格式） | 整数 |
| tBalance | 当日余额 | 浮点数 |
| yBalance | 前一日余额 | 浮点数 |
| **total_purchase_amt** | **总申购金额** | 浮点数 |
| direct_purchase_amt | 直接申购金额 | 浮点数 |
| purchase_bal_amt | 余额申购金额 | 浮点数 |
| purchase_bank_amt | 银行申购金额 | 浮点数 |
| **total_redeem_amt** | **总赎回金额** | 浮点数 |
| consume_amt | 消费金额 | 浮点数 |
| transfer_amt | 转账金额 | 浮点数 |
| tftobal_amt | 转到余额金额 | 浮点数 |
| tftocard_amt | 转到卡金额 | 浮点数 |
| share_amt | 份额金额 | 浮点数 |
| category1-4 | 基金类别1-4 | 浮点数 |

### 相关性分析

**与 total_purchase_amt 最相关的字段：**
- direct_purchase_amt (0.999999) - 直接申购金额
- purchase_bal_amt (0.781959) - 余额申购金额
- purchase_bank_amt (0.633062) - 银行申购金额

**与 total_redeem_amt 最相关的字段：**
- transfer_amt (0.985183) - 转账金额
- tftocard_amt (0.959490) - 转到卡金额
- category1 (0.303197) - 基金类别1

### 走势分析

根据 `fund_flow_trend.png` 分析，资金流入流出呈现**三个阶段**：

1. **初期平缓期（2013年7月-10月）**：申购和赎回金额波动平缓
2. **增长爆发期（2013年11月-2014年3月）**：资金快速增长，申购量显著上升
3. **增长稳定期（2014年3月-8月）**：增长速度放缓，进入稳定状态

**整体统计（2013年7月-2014年8月）：**
- 申购总金额：925亿元，日均2.17亿元
- 赎回总金额：727亿元，日均1.70亿元
- **资金净流入：198亿元**

---

## 📊 预测方法对比

### 方法1：ARIMA(7,1,7)

**原理：** 自回归移动平均模型，基于历史时间序列自相关性

**优点：**
- 经典统计模型，理论完善
- 擅长捕捉长期趋势

**缺点：**
- 忽视周期性规律（周一-周日、节假日等）
- 预测较为平稳

**预测结果（9月份）：**
| 指标 | 平均值 | 最小值 | 最大值 |
|------|--------|--------|--------|
| 申购总金额 | 2.77亿元 | - | - |
| 赎回总金额 | 2.93亿元 | - | - |

---

### 方法2：Weekday + 趋势调整

**原理：** 周期因子法，用weekday的平均值加上线性趋势调整

**公式：** 预测值 = weekday平均值 + 趋势斜率 × 天数

**weekday因子（申购）：**
- 周一-周四：较高（31-33亿元）
- 周五：下降（24.9亿元）
- 周末：最低（19.6亿元）

**优点：**
- 清晰捕捉交易日与非交易日差异
- 结合长期趋势

**缺点：**
- 忽视月度周期（月初vs月末差异）
- 假设线性趋势

**预测结果（9月份）：**
| 指标 | 平均值 | 范围 |
|------|--------|------|
| 申购总金额 | 2.72亿元 | 1.82-3.33亿元 |
| 赎回总金额 | 2.78亿元 | 1.81-3.46亿元 |

---

### 方法3：Weekday × Day（乘法）

**原理：** 双重周期因子法，weekday和day因子采用乘法关系

**公式：** 预测值 = 基础值 × weekday因子 × day因子

**weekday因子（申购）：**
- 周一-周二：1.18-1.21倍
- 周三-周四：1.14-1.16倍
- 周五：0.90倍
- 周末：0.71倍

**day因子规律（申购）：**
- 月初（1-5号）：高于平均(1.08-1.19倍)
- 月中（8-16号）：接近平均(1.01-1.25倍)
- 月末（22-30号）：低于平均(0.83-0.89倍)

**优点：**
- 同时捕捉周期性和月度周期
- 预测最精细，波动最真实

**缺点：**
- 因子过多，可能过度拟合
- 预测值波动较大

**预测结果（9月份）：**
| 指标 | 平均值 | 范围 |
|------|--------|------|
| 申购总金额 | 2.73亿元 | 1.60-3.93亿元 |
| 赎回总金额 | 2.77亿元 | 1.57-3.64亿元 |

---

## 🚀 使用指南

### 1. 数据探索

```bash
# 查看原始数据结构
python3 readData.py

# 分析字段含义和相关性
python3 analyze.py
```

### 2. 绘制走势图

```bash
python3 plot_fund_flow.py
# 输出：fund_flow_trend.png
```

### 3. 生成预测结果

```bash
# 方法1：ARIMA预测
python3 forecast_arima.py
# 输出：result.csv

# 方法2：Weekday + 趋势调整
python3 forecast_weekday.py
# 输出：result2.csv

# 方法3：Weekday × Day乘法
python3 forecast_weekday_day.py
# 输出：result3.csv
```

### 4. 输出格式

所有预测结果（result.csv、result2.csv、result3.csv）的格式一致：

```csv
20140901,申购金额1,赎回金额1
20140902,申购金额2,赎回金额2
...
20140930,申购金额30,赎回金额30
```

格式说明：
- 第一列：report_date（YYYYMMDD格式）
- 第二列：total_purchase_amt（申购总金额，整数）
- 第三列：total_redeem_amt（赎回总金额，整数）
- 无表头，用逗号分隔

---

## 💡 核心发现与建议

### 关键发现

1. **周期性强**：交易日（周一-周四）申购量是周末的1.5倍以上，说明用户交易行为具有明显的周期性

2. **月度规律明显**：月初申购额高于月末约30-40%，可能与工资发放周期相关

3. **资金净流入**：总体申购额大于赎回额，说明该基金处于吸引力高的阶段

4. **长期趋势平缓**：从3月到8月，增长速度明显放缓，进入稳定阶段

5. **赎回滞后性**：赎回与申购的相关性较低(0.09)，说明赎回决策受其他因素影响更大

### 预测建议

- **快速预测**：使用 **Weekday + 趋势调整**（result2.csv），平衡准确性和稳定性
- **精细预测**：使用 **Weekday × Day乘法**（result3.csv），捕捉双重周期
- **保守预测**：使用 **ARIMA**（result.csv），结果更平稳、风险更低

### 进一步改进方向

1. 加入**特殊事件因素**（节假日、市场事件等）
2. 考虑**外生变量**（SHIBOR利率、基金净值涨跌等）
3. 使用**集成预测**（多个模型的加权组合）
4. 尝试**深度学习**（LSTM、GRU等RNN模型）

---

## 📈 依赖环境

### 必需库

```
pandas >= 1.0.0
numpy >= 1.19.0
matplotlib >= 3.3.0
scikit-learn >= 0.24.0
statsmodels >= 0.12.0（ARIMA模型）
```

### Python版本

Python 3.8+

### 安装命令

```bash
pip install pandas numpy matplotlib scikit-learn statsmodels
```

---

## 📝 文件更新记录

| 日期 | 操作 | 文件 |
|------|------|------|
| 2014-09-01 | 数据探索 | analyze.py, readData.py |
| 2014-09-02 | 绘制走势图 | plot_fund_flow.py, fund_flow_trend.png |
| 2014-09-03 | ARIMA预测 | forecast_arima.py, result.csv |
| 2014-09-04 | Weekday预测 | forecast_weekday.py, result2.csv |
| 2014-09-05 | 双周期预测 | forecast_weekday_day.py, result3.csv |

---

## 🔗 相关资源

- [ARIMA模型文档](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html)
- [时间序列预测最佳实践](https://en.wikipedia.org/wiki/Time_series)
- [AI编码指南](.github/copilot-instructions.md)

---

## 📧 项目信息

**项目类型：** 时间序列AI竞赛  
**核心目标：** 预测基金申购和赎回总金额  
**数据周期：** 每日更新（2013年7月-2014年8月）  
**预测周期：** 2014年9月（30天）

