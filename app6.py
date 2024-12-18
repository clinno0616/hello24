import numpy as np
import cv2
import pyautogui
import time
from datetime import datetime
import os
import tkinter as tk
from PIL import ImageTk, Image
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from realesrgan import RealESRGANer

class RegionSelector:
    def __init__(self):
        """初始化區域選擇器"""
        # 創建全螢幕視窗
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # 設定透明度
        self.root.configure(cursor="cross")  # 設定滑鼠游標為十字

        # 初始化變數
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        self.selected_region = None

        # 創建畫布
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 綁定滑鼠事件
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Escape>", self.cancel_selection)

        # 顯示提示文字
        self.canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            30,
            text="請用滑鼠框選要擷取的區域\n按 ESC 取消選擇",
            fill="black",
            font=("Arial", 16),
            justify="center"
        )

    def on_mouse_down(self, event):
        """滑鼠按下時的處理"""
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_move(self, event):
        """滑鼠移動時的處理"""
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline="red", width=2
        )

    def on_mouse_up(self, event):
        """滑鼠放開時的處理"""
        if self.start_x and self.start_y:
            x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
            x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
            self.selected_region = (int(x1), int(y1), int(x2-x1), int(y2-y1))
            self.root.quit()

    def cancel_selection(self, event):
        """取消選擇"""
        self.selected_region = None
        self.root.quit()

    def get_region(self):
        """開始選擇區域並返回結果"""
        self.root.mainloop()
        self.root.destroy()
        return self.selected_region

class AIImageEnhancer:
    """AI圖像增強處理器"""
    def __init__(self):
        """初始化AI模型"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用設備: {self.device}")
        
        # 初始化 Real-ESRGAN 模型
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        
        # Windows 專案目錄下的 models 資料夾存放模型
        try:
            # 使用絕對路徑
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_dir = os.path.join(current_dir, 'models')
            model_path = os.path.join(model_dir, 'RealESRGAN_x4plus.pth')
            
            # 檢查並創建目錄
            if not os.path.exists(model_dir):
                try:
                    os.makedirs(model_dir, exist_ok=True)
                    print(f"已建立模型目錄: {model_dir}")
                except Exception as e:
                    print(f"建立模型目錄失敗: {e}")
                    # 如果無法在當前目錄建立，嘗試在臨時目錄建立
                    model_dir = os.path.join(os.environ.get('TEMP', '.'), 'screen_long_exposure_models')
                    model_path = os.path.join(model_dir, 'RealESRGAN_x4plus.pth')
                    os.makedirs(model_dir, exist_ok=True)
                    print(f"已在臨時目錄建立模型目錄: {model_dir}")
            
            # 檢查寫入權限
            test_file = os.path.join(model_dir, 'test_write.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                print(f"目錄無寫入權限，改用臨時目錄: {e}")
                model_dir = os.path.join(os.environ.get('TEMP', '.'), 'screen_long_exposure_models')
                model_path = os.path.join(model_dir, 'RealESRGAN_x4plus.pth')
                os.makedirs(model_dir, exist_ok=True)
                print(f"已改用臨時目錄: {model_dir}")
            
            print(f"使用模型路徑: {model_path}")
        except Exception as e:
                print(f"目錄無寫入權限，改用臨時目錄: {e}")
        if not os.path.exists(model_path):
            print("下載 Real-ESRGAN 模型...")
            try:
                print("開始下載 Real-ESRGAN 模型...")
                load_file_from_url(
                    'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
                    model_path
                )
                print("模型下載完成！")
            except Exception as e:
                print(f"模型下載失敗: {e}")
                raise Exception("無法下載模型檔案，請檢查網路連接或手動下載模型至 models 資料夾")
        
        self.upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            device=self.device
        )

    def enhance(self, image):
        """使用AI模型增強圖像"""
        print("正在使用 Real-ESRGAN 進行圖像增強...")
        
        # 前處理：增強車軌的可見度
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 增強亮部細節
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        v = clahe.apply(v)
        
        # 增加飽和度以突出車軌
        s = cv2.multiply(s, 1.5)
        s = np.clip(s, 0, 255).astype(np.uint8)
        
        hsv = cv2.merge([h, s, v])
        enhanced_input = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # 轉換為RGB格式（Real-ESRGAN需要）
        image_rgb = cv2.cvtColor(enhanced_input, cv2.COLOR_BGR2RGB)
        
        # 進行超解析度處理
        enhanced, _ = self.upsampler.enhance(image_rgb)
        
        # 轉回BGR格式
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)
        
        # 後處理：進一步增強車軌效果
        enhanced_hsv = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(enhanced_hsv)
        
        # 增強高光部分
        v = cv2.multiply(v, 1.2)
        v = np.clip(v, 0, 255).astype(np.uint8)
        
        enhanced_hsv = cv2.merge([h, s, v])
        final_enhanced = cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)
        
        return final_enhanced

class ScreenLongExposure:
    def __init__(self):
        """初始化螢幕長曝光處理器"""
        self.screen_width, self.screen_height = pyautogui.size()
        self.ai_enhancer = AIImageEnhancer()
        
    def capture_frames(self, duration, region=None):
        """擷取指定時間內的螢幕畫面"""
        frames = []
        start_time = time.time()
        frame_count = 0
        
        print(f"開始擷取畫面，持續 {duration} 秒...")
        
        while (time.time() - start_time) < duration:
            screenshot = pyautogui.screenshot(region=region)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frames.append(frame)
            frame_count += 1
            time.sleep(1/30)  # 約 30 FPS
        
        print(f"擷取完成，共 {frame_count} 幀")
        return frames

    def adjust_exposure(self, image, ev=1/3):
        """調整影像曝光值
        
        參數:
            image: 輸入影像
            ev: 曝光補償值（EV），+1 表示亮度翻倍，-1 表示亮度減半
        """
        # 計算曝光倍數：2^EV
        exposure_factor = np.power(2, ev)
        
        # 轉換為 LAB 色彩空間以調整亮度
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # 只調整亮度通道
        l = cv2.multiply(l.astype(float), exposure_factor)
        l = np.clip(l, 0, 255).astype(np.uint8)
        
        # 合併通道
        lab = cv2.merge([l, a, b])
        adjusted = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return adjusted

    def create_exposure(self, frames, method='max'):
        """建立長曝光效果"""
        if not frames:
            return None
            
        print("正在處理長曝光效果...")
        frames_float = [frame.astype(float) for frame in frames]
        
        # 使用最大值合成來強化車軌效果
        result = np.max(frames_float, axis=0)
            
        # 增強車軌的亮度和對比度
        min_val = np.min(result)
        max_val = np.max(result)
        
        # 拉伸對比度但保持整體亮度
        result = ((result - min_val) / (max_val - min_val) * 255)
        
        # 保持中性的 gamma 值
        result = np.power(result/255.0, 0.95) * 255
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        return result

    def process(self, duration, output_path=".", method='mean'):
        """執行完整的處理流程"""
        try:
            # 1. 選擇區域
            print("請框選要擷取的螢幕區域...")
            selector = RegionSelector()
            region = selector.get_region()
            
            if region is None:
                print("已取消區域選擇！")
                return False
                
            print(f"已選擇區域: {region}")
            time.sleep(1)  # 給使用者一點時間準備
            
            # 2. 擷取畫面
            frames = self.capture_frames(duration, region)
            
            if not frames:
                print("沒有擷取到畫面！")
                return False
            
            # 3. 建立長曝光效果
            long_exposure = self.create_exposure(frames, method)
            
            # 4. 使用AI進行圖像增強
            enhanced_image = self.ai_enhancer.enhance(long_exposure)
            
            # 5. 儲存結果
            if not os.path.exists(output_path):
                os.makedirs(output_path)
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 儲存原始長曝光
            original_file = os.path.join(output_path, f"original_{timestamp}.jpg")
            cv2.imwrite(original_file, long_exposure)
            
            # 儲存AI增強結果
            enhanced_file = os.path.join(output_path, f"ai_enhanced_{timestamp}.jpg")
            cv2.imwrite(enhanced_file, enhanced_image)
            
            print(f"已儲存原始長曝光至: {original_file}")
            print(f"已儲存AI增強結果至: {enhanced_file}")
            
            return True
            
        except Exception as e:
            print(f"處理過程發生錯誤: {e}")
            return False

def main():
    # 使用範例
    processor = ScreenLongExposure()
    
    # 設定參數
    duration = float(input("請輸入擷取時間（秒）: "))
    output_path = "./output"  # 輸出路徑
    
    # 執行處理
    processor.process(
        duration=duration,
        output_path=output_path,
        method='mean'  # 或使用 'max'
    )

if __name__ == "__main__":
    main()