# Screen Long Exposure

這是一個基於 Python 的螢幕長曝光工具，專門用於創建夜間車軌、光軌等長曝光效果的照片。本工具使用 AI 增強技術（Real-ESRGAN）來提升圖像品質，並提供精確的曝光控制。

## 功能特色

- 自訂區域截圖和長曝光時間
- 使用 Real-ESRGAN AI 模型增強圖像品質
- 精確的曝光值控制（EV）
- 自動車軌優化
- 多種圖像處理選項
- 支援批次處理
- 自動存檔多個版本供比較

## 系統需求

- Windows 11
- Python 3.8 或更高版本
- NVIDIA 顯示卡（建議，可加速 AI 處理）

## 安裝指南

1. 安裝必要的 Python 套件：

```bash
pip install numpy opencv-python pyautogui pillow torch torchvision basicsr realesrgan
```

2. 下載專案：

```bash
git clone [專案網址]
cd screen-long-exposure
```

3. 建立模型目錄：

```bash
mkdir models
```

## 使用方法

1. 執行主程式：

```bash
python app6.py
```

2. 按照提示操作：
   - 輸入擷取時間（建議 10-30 秒）
   - 使用滑鼠框選要擷取的區域
   - 等待處理完成

### 基本使用範例

```python
from app import ScreenLongExposure

processor = ScreenLongExposure()
processor.process(
    duration=20,          # 擷取時間（秒）
    output_path="./output",
    method='max',         # 使用最大值合成
    ev=1/3               # 設定 EV=+1/3
)
```

## 拍攝建議

### 車軌拍攝

1. 時間選擇
   - 建議在夜間車流穩定時段
   - 根據車流量調整曝光時間：
     - 車流量大：10-15 秒
     - 車流量中：15-20 秒
     - 車流量小：20-30 秒

2. 構圖建議
   - 選擇車流穩定的路段
   - 避免強光源直接進入畫面
   - 盡量包含完整的行車路線
   - 可以包含一些固定的景物作為對比

3. 參數設定
   - 使用 `method='max'` 來最佳化車軌效果
   - 設定 `ev=1/3` 控制曝光度
   - 根據實際效果微調參數

## 輸出檔案說明

程式會產生三個版本的圖片：

1. `original_[timestamp].jpg`
   - 原始長曝光結果
   - 未經任何後製處理

2. `adjusted_ev+0.3_[timestamp].jpg`
   - 曝光調整後的結果
   - 已套用曝光補償

3. `enhanced_ev+0.3_[timestamp].jpg`
   - AI 增強後的結果
   - 最終成品

## 常見問題

1. **Q: 程式無法啟動？**
   - 確認是否已安裝所有必要套件
   - 檢查 Python 版本是否符合要求
   - 確認是否有足夠的系統權限

2. **Q: 照片太暗或太亮？**
   - 調整 EV 值（範圍：-2 到 +2）
   - 檢查原始場景的亮度是否合適
   - 考慮調整擷取時間

3. **Q: 車軌效果不明顯？**
   - 延長擷取時間
   - 確認使用 `method='max'`
   - 選擇車流更穩定的路段
   - 避免場景中有過強的光源

## 技術支援

如果遇到問題或需要協助，請：
1. 檢查上述常見問題
2. 查看程式執行時的錯誤訊息
3. 提供詳細的操作步驟和系統環境資訊

## 授權資訊

本專案採用 [授權類型] 授權。
Real-ESRGAN 模型版權歸原作者所有。

## 更新紀錄

### v1.0.0 (2024-12-18)
- 初始版本發布
- 加入 AI 增強功能
- 支援精確曝光控制
- 優化車軌效果
