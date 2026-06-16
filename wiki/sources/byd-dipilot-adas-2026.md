---
tags: [source]
sources: [ADAS競爭回歸軟體本質　比亞迪天神之眼凸顯數據與演算法落差.md, 科技1分鐘：比亞迪天神之眼.md]
updated: 2026-04-09
---


**來源**：[https://www.digitimes.com.tw/tech/dt/n/shwnws.asp?CnlID=&id=751475&grid_seq1=&grid_seq2=](https://www.digitimes.com.tw/tech/dt/n/shwnws.asp?CnlID=&id=751475&grid_seq1=&grid_seq2=)

# 比亞迪天神之眼（DiPilot）：ADAS 規模化與軟體品質的落差

**原文**：DIGITIMES／黃女瑛、林廷宇｜**發布**：2026-04-09

## 摘要
比亞迪天神之眼（DiPilot）2025 年 2 月發布，導入約 250 萬輛新車，裝車量約為 Tesla FSD 的 2 倍，但有效訓練數據量僅達 Tesla 的一半，顯示硬體規模不等於軟體能力。

## 三級架構

| 方案 | 代號 | 感測器 | 晶片 | 定位 |
|------|------|--------|------|------|
| DiPilot 600（A 方案）| — | 3 顆 LiDAR | — | 仰望品牌旗艦 |
| DiPilot 300（B 方案）| — | LiDAR + | Orin-X×1 | 騰勢及高階車款 |
| DiPilot 100（C 方案）| 二郎神 | 前視三目（2廣角+1長焦，偵測距離 350m）| — | 10 萬元級距普及化 |

- 首波導入 21 款車型，價格帶：人民幣約 7 萬～20 萬+元
- 支援高速 + 城市 NOA（導航輔助駕駛）
- 採端到端（E2E）資料驅動演算法架構

## 問題與挑戰
- **數據品質**：Piper Sandler 研究指出，有效訓練數據量僅為 Tesla FSD 的一半
- **品質爭議**：幽靈轉向、非預期加速、導航失誤 → 中國網路平台大量討論
- **市場影響**：2026 Q1 比亞迪失去中國銷售龍頭地位，市場認為與天神之眼品質爭議有關
- **標配風險**：大規模標配放大尚未成熟技術的風險，快速影響品牌信任

## Tesla 的對比
- Tesla FSD 軟體能力領先，但美國監管加強審查
- Tesla 計劃 2026 年 FSD 進入中國，被要求改名「智能輔助駕駛」

## Related
- [[entities/比亞迪]]
- [[entities/Tesla]]
- [[concepts/電池與技術/ADAS智駕系統]]
- [[concepts/電池與技術/自動駕駛安全監管]]
