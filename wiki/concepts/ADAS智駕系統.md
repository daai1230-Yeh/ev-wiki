---
tags: [concept]
sources: [byd-dipilot-adas-2026, robotaxi-market-2026, toyota-adas-vs-fsd-subscription, hyundai-pleos-sdv-os, in-cabin-ai-sensing-2026, l2plus-adas-adoption-2026, rivian-lidar-china-partner-2026, hyundai-kia-atria-ai-gwangju-2026, hesai-color-lidar-2026, ev-news-digest-jun1-10-2026]
updated: 2026-06-10
---

# ADAS 智駕系統（Advanced Driver Assistance System）

先進駕駛輔助系統是 EV 差異化競爭的核心戰場，2026 年競爭重心從硬體部署轉向軟體能力與數據迭代效率。

## 技術路線
| 路線 | 代表 | 特徵 |
|------|------|------|
| 純視覺 | Tesla FSD、比亞迪 DiPilot 100 | 低成本、依賴算法 |
| 視覺 + 毫米波雷達 | 多數車廠 | 中階標配 |
| 視覺 + LiDAR | 比亞迪 DiPilot 300/600、蔚來等 | 高精度，高成本 |

## 關鍵競爭維度
1. **數據量與品質**：Tesla FSD 訓練數據 > 比亞迪 DiPilot（Piper Sandler）
2. **演算法架構**：端到端（E2E）vs 模組化
3. **OTA 迭代速度**
4. **法規合規性**：各國命名要求不同（Tesla 在中國須改名「智能輔助駕駛」）

## 比亞迪天神之眼（DiPilot）現況
- 裝車量：~250 萬輛（Tesla FSD 的 2 倍）
- 有效訓練數據：僅 Tesla 的一半
- 品質爭議：幽靈轉向、非預期加速、導航失誤

## Robotaxi 延伸應用
- 技術成熟後的終極應用，目前成本 >$8/km，需降至 $0.8/km 才具商業競爭力
- 見 [[concepts/Robotaxi自動計程車]]

## 豐田 Corolla vs Tesla FSD 訂閱制爭議（2026-04）

- 豐田 Corolla 標配車道置中 + 自適應巡航（**免費**）
- Tesla 2026-01 起，同類功能併入 FSD 訂閱（**$99/月**）
- 引發消費者對訂閱制的反彈：「買車即應買斷功能」
- 歷史案例：BMW 座椅加熱訂閱引爆反彈後撤回
- 對 Tesla 的影響：FSD 訂閱是軟體收入支柱，Corolla 效應侵蝕其基礎需求理由
- 參見：[[sources/toyota-adas-vs-fsd-subscription]]

## 現代汽車 Pleos OS：SDV 軟體差異化策略（2026-04）

現代在 Ioniq 3 首搭「Pleos」作業系統，與 Tesla 全觸控路線形成鮮明對比：

| 特點 | 細節 |
|------|------|
| 基礎平台 | Android Automotive OS（非手機投影 Android Auto）|
| App 生態 | 現代自有 App Market（更自主，非 Google GAS）|
| 架構 | 區域控制器（Zonal Controllers）→ 減少配線複雜度 |
| OTA | 真正整車 OTA（舊系統因多廠商拼接而受限）|
| **關鍵差異化** | **保留實體按鈕**（音量、溫控、座椅加熱冷卻 + 方向盤按鍵）|

- 現代論述：「永遠為重要功能提供實體控制」→ 對比 Tesla 轉向燈桿等全觸控爭議
- 同採 Android Automotive：Ford、Honda、BMW、Porsche
- 未來：所有新款現代 EV 陸續搭載 Pleos
- 參見：[[sources/hyundai-pleos-sdv-os]]

## 車內感測 AI：DMS → 全艙多模態（Smart Eye，2026-04）

瑞典 AI 公司 Smart Eye 展現車艙感知從「監控駕駛」擴展至「監控全艙」的趨勢：

| 指標 | 數值 |
|------|------|
| OEM 合作客戶 | **24 家** |
| 最新訂單 | 日本主流車廠 2 款車型（DMS → 全艙感知）|
| 量產時程 | **2027 年中** |
| 法規驅動 | 歐盟 GSR **2026 年 7 月**強制 ADDW；Euro NCAP 2026 五星需偵測疲勞/分心 |

### 技術演進：硬體讓位給 AI 演算法
- **感知範圍**：DMS（駕駛監控）→ 全艙（乘客、兒童、遺忘物件）
- **感測器精簡**：多鏡頭 → 單/少數鏡頭 + AI 演算法（降低成本與功耗）
- **商業模式**：硬體銷售 → OTA 升級 + 持續性軟體收入
- **個人化應用**：依乘客情緒自動調整空調、音響、音樂推薦

> 「全球技術競爭已由硬體感測器數量轉向 AI 解析能力」
> — 台系智慧座艙業者

### 隱私課題
- 全艙監控產生生物特徵數據（表情/眼神/行為），2027 年新車量產後將成核心議題
- 參見：[[sources/in-cabin-ai-sensing-2026]]

## L2/L2+：2035 年主導 ADAS 市場（Counterpoint，2026-05）

| 指標 | 2025 | 2035 |
|------|------|------|
| ADAS 整體採用率 | **66%** | **94%** |
| L2/L2+ 占比 | — | **≈65%** |

- 高階自動駕駛（L3-L5）進展緩慢（法規 + 成本），L2+ 成為主力
- L2+ 快速放量原因：可用性 + 成本效益 + 高頻使用 + 訂閱式 SaaS 收入模式
- **對車廠意義**：L2+ 成為「持續性收入（recurring revenue）」的關鍵
- 參見：[[sources/l2plus-adas-adoption-2026]]

## Rivian：中國 LiDAR 技術 × 美國本土生產（2026-05）

- Rivian R2 車款將搭載**小型 LiDAR**（非 Waymo 大型旋轉式）
- 合格低成本 LiDAR 幾乎全來自中國（禾賽科技、速騰聚創）
- 解決方案：與中國廠商合資，**在美國本土生產**→ 規避國安疑慮
- 其他美國車廠也表達對此模式的興趣
- 參見：[[sources/rivian-lidar-china-partner-2026]]

## 禾賽 EXT：全球首款顏色辨識 LiDAR（2026-04）

中國 LiDAR 大廠禾賽科技（Hesai）發布 EXT 感測器，標誌 LiDAR 競爭從成本轉向價值創新：

| 項目 | 細節 |
|------|------|
| 核心晶片 | Picasso（自研）|
| 技術突破 | 空間測距 + **顏色偵測**整合（全球首款）|
| 關鍵應用 | 精準辨識紅綠燈顏色 → 提升自駕安全性 |
| 量產時程 | **2027 年**旗艦車型 |
| 中國市占 | **>40%**（理想汽車、小米、比亞迪、NVIDIA 供應）|

- 禾賽 CEO：「若只追低價，將犧牲創造更高價值的創新機會」
- LiDAR 必要性仍有爭議：Tesla/小鵬偏好純視覺；禾賽兼做人形機器人（Kosmo 手持設備）
- 參見：[[sources/hesai-color-lidar-2026]]

## 韓國首次大規模自駕實證：現代 × 起亞 Atria AI（2026-05）

- 地點：南韓光州廣域市（501 平方公里）
- 規模：**約 200 輛**量產車改裝，2026 下半啟動，2027 年擴全市
- 核心技術：**Atria AI**（現代/起亞自研），**E2E 架構**（感知/判斷/控制整合至單一 AI 模型）
- 傳感配置：8 自駕攝影機 + 1 雷達（每輛）
- 服務平台：**Shucle**（AI 調度 + 叫車管控）
- 公私合作：現代/起亞 + 韓國 MOLIT + 光州市 + Autonomous A2Z
- 意義：韓國整車廠以自有 E2E 技術正式切入大規模城市自駕場景，不依賴 Waymo/Mobileye
- 參見：[[sources/hyundai-kia-atria-ai-gwangju-2026]]

## 比亞迪 4 奈米智駕晶片（2026-06-05）

比亞迪發布自研 **4 奈米製程智駕晶片**：
- 達到高通 Snapdragon 8295（4nm）同等製程等級
- 專為天神之眼（DiPilot）系統深度優化，降低對英偉達 DRIVE Orin 的依賴
- 在美國晶片出口管制壓力下，自研是中國車廠保障供應鏈的必要策略
- 中國車廠自研晶片趨勢：蔚來（NX9031「神璣」）、小鵬（XPILOT 系列）、比亞迪（本次）
- 參見：[[sources/ev-news-digest-jun1-10-2026]] | [[concepts/中國EV市場競爭格局]]

## Related
- [[entities/Tesla]]
- [[entities/比亞迪]]
- [[entities/豐田]]
- [[entities/蔚來]]
- [[entities/Rivian]]
- [[concepts/自動駕駛安全監管]]
- [[concepts/Robotaxi自動計程車]]
- [[sources/byd-dipilot-adas-2026]]
- [[sources/toyota-adas-vs-fsd-subscription]]
- [[sources/nio-self-chip-denvidia]]
- [[sources/hyundai-pleos-sdv-os]]
- [[sources/in-cabin-ai-sensing-2026]]
- [[sources/l2plus-adas-adoption-2026]]
- [[sources/rivian-lidar-china-partner-2026]]
- [[sources/hyundai-kia-atria-ai-gwangju-2026]]
- [[sources/hesai-color-lidar-2026]]
