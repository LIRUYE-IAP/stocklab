import type { Sector } from '@/types'

export const indices = [
  { name: '上证指数', code: '000001', value: '3,915.28', change: 0.82, amount: '6,842亿', points: [3862, 3874, 3859, 3888, 3892, 3906, 3898, 3915] },
  { name: '深证成指', code: '399001', value: '12,486.71', change: 1.23, amount: '9,174亿', points: [12240, 12285, 12264, 12320, 12388, 12402, 12487] },
  { name: '创业板指', code: '399006', value: '2,782.46', change: 1.67, amount: '4,162亿', points: [2708, 2722, 2716, 2742, 2760, 2754, 2782] },
  { name: '科创50', code: '000688', value: '1,186.34', change: -0.36, amount: '1,136亿', points: [1198, 1194, 1201, 1192, 1188, 1191, 1186] },
]

export const breadth = { rise: 3618, fall: 1482, flat: 106, limitUp: 76, limitDown: 9, amount: '1.60万亿' }

export const sentiment = {
  value: 72,
  level: '偏强',
  trend: [42, 46, 44, 51, 55, 58, 54, 62, 66, 64, 70, 74, 69, 72, 77, 75, 71, 73, 70, 72],
}

export const sectors: Sector[] = [
  { name: '机器人', change: 5.26, return5: 8.4, return20: 15.7, amount: 1286, strength: 92, stage: '加速' },
  { name: '存储芯片', change: 4.18, return5: 6.9, return20: 10.3, amount: 972, strength: 87, stage: '启动' },
  { name: '有色金属', change: 3.62, return5: 5.2, return20: 13.8, amount: 1460, strength: 85, stage: '加速' },
  { name: '商业航天', change: 2.96, return5: 9.7, return20: 21.4, amount: 835, strength: 83, stage: '高潮' },
  { name: '新能源', change: 1.74, return5: 3.1, return20: -2.8, amount: 1688, strength: 69, stage: '企稳' },
  { name: '创新药', change: 0.88, return5: -1.3, return20: 7.2, amount: 714, strength: 61, stage: '分歧' },
  { name: '白酒', change: -1.26, return5: -3.4, return20: -8.1, amount: 516, strength: 33, stage: '退潮' },
  { name: '银行', change: -0.72, return5: 1.1, return20: -1.6, amount: 482, strength: 47, stage: '企稳' },
]

export const scanCards = [
  { name: '底部放量', count: 23, delta: '+7', tone: 'violet' },
  { name: 'MACD金叉', count: 86, delta: '+18', tone: 'blue' },
  { name: '突破平台', count: 31, delta: '+12', tone: 'orange' },
  { name: '历史活跃股转强', count: 14, delta: '+4', tone: 'red' },
  { name: '缩量回踩', count: 42, delta: '-3', tone: 'green' },
]

export const marketDistribution = [
  { range: '≤-7%', value: 42 }, { range: '-7~-5%', value: 91 }, { range: '-5~-3%', value: 228 },
  { range: '-3~-1%', value: 621 }, { range: '-1~0%', value: 500 }, { range: '0~1%', value: 910 },
  { range: '1~3%', value: 1284 }, { range: '3~5%', value: 528 }, { range: '5~7%', value: 210 }, { range: '≥7%', value: 76 },
]

export const changes = [
  { label: '技术转强', value: 3, note: '自选股', color: '#5b5bd6' },
  { label: '新增风险', value: 2, note: '持仓股', color: '#d14343' },
  { label: '触发预警', value: 4, note: '今日', color: '#d99021' },
  { label: '策略新增', value: 5, note: '匹配标的', color: '#178f6e' },
]
