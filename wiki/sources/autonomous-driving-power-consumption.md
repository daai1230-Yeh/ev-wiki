---
tags: [source]
sources: [2026-04-30-自駕技術耗電兇猛-現代電動車能否承擔.md]
updated: 2026-04-29
---


**來源**：[https://insideevs.com/features/794319/autonomous-car-power-consumption](https://insideevs.com/features/794319/autonomous-car-power-consumption)

# 自動駕駛技術耗電分析：從 3kW 降至 500W 目標（2026）

**原文**：InsideEVs／Lawrence Ulrich｜**發布**：2026-04-29

## 摘要
自動駕駛系統的功耗從早期 1.5~3kW 已大幅降至現代 ~1kW，業界目標進一步壓縮至 500W。若 10 億輛 AV 每天行駛 1 小時且功耗達 840W，其耗電量將等同 2023 年全球所有資料中心的總耗電量。

## 各代系統功耗對比

| 系統 | 時期 | 自駕功耗 | 備注 |
|------|------|---------|------|
| Chevy Bolt（Cruise）| 早期 | **1.5~3kW** | 20 小時班次耗 40kWh（2/3 電池）|
| Hyundai Ioniq 5 AV（Motional）| 2022 | 高 | EPA 續航 168 英里（vs 消費版 303 英里，-44.6%）|
| Waymo Jaguar I-Pace | 現役 | **~1kW** | 29 攝影機 + 5 LiDAR |
| Waymo 第六代（Ioniq 5 / Zeekr）| 測試中 | **~1kW** | |
| Rivian（Level 4 目標）| 2026~2028 | **~1.1kW** | RAP1 自製 SoC |
| Lucid / Nuro | 2026 | **~1kW** | 目標 500W |
| **業界共識目標** | 2026~2030 | **500W** | MIT 安全線 <1.2kW |

## MIT 規模推算

> 1B 輛 AV × 每日 1 小時 × 840W = **等同 2023 年全球所有資料中心耗電量**

MIT 教授 Sertac Karaman：「每輛車 1kW 是未來 3~5 年的合理目標，但計算占交通能耗的比重將越來越顯著。」

## 解決方案

1. **固態 LiDAR**：從機械旋轉式（高功耗、大體積）→ 固態（輕薄、低功耗）
2. **自製 SoC**（Rivian RAP1）：比 Nvidia Orin 計算力 4x，TOPS 利用率 2x
3. **傳感器減量**：Lucid「極致效率」方向（減少感測器數量）
4. **Watts per TOPS 成為關鍵 KPI**（計算量 / 瓦特比）

## Robotaxi 充電窗口挑戰

- 全天候 Robotaxi 使用率目標：**23 小時 / 天**（1 小時用於充電 + 清洗 + 維護）
- 每分鐘在充電站是沒有收入的時間
- 自駕功耗越低 → 更多里程用於服務 → 更高 ROI

## Uber 關聯大單

- Uber × **Lucid**：$5 億，35,000 輛 Gravity SUV（舊金山 2026 起）
- Uber × **Rivian**：最高 $12.5 億，10,000 輛 R2（2028 起，25 城市 2031）

## Related
- [[concepts/車輛類型/Robotaxi自動計程車]]
- [[concepts/電池與技術/ADAS智駕系統]]
- [[sources/china-robotaxi-cost-advantage]]
- [[sources/uber-ev-infrastructure-investment]]
