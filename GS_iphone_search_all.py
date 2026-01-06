from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random
import pandas as pd
import sqlite3 
import re

conn = sqlite3.connect('Iphone.db')

def get_series(model):
    model = str(model).upper()  # 轉大寫方便比對
    
    if 'SE' in model:
        return 'se'
    elif '17' in model:
        return '17'
    elif '16' in model:
        return '16'
    elif '15' in model:
        return '15'
    elif '14' in model:
        return '14'
    elif '13' in model:
        return '13'
    elif '12' in model:
        return '12'
    elif '11' in model:
        return '11'
    elif 'XS' in model or 'XR' in model or 'X' in model:
        return 'x'
    elif '8' in model:
        return '8'
    else:
        return '其他'
    

def categorize_iphone_model(model_str):
    """
    將 iPhone 型號字串歸類到標準型號
    """
    if pd.isna(model_str) or model_str.strip() == '':
        return None
    
    # 轉成小寫方便比對
    model_lower = str(model_str).lower().replace(' ', '')
    
    # 定義歸類規則（按優先順序）
    rules = [
        # iPhone 17 系列
        (['17', 'promax'], '17 Pro Max'),  # 統一使用有空格的格式
        (['17', 'pro'], '17 Pro'),
        (['17', 'air'], 'Air'),
        (['17'], '17'),
        
        # iPhone 16 系列
        (['16', 'promax'], '16 Pro Max'),
        (['16', 'pro'], '16 Pro'),
        (['16', 'plus'], '16 Plus'),
        (['16e'], '16e'),
        (['16'], '16'),
        
        # iPhone 15 系列
        (['15', 'promax'], '15 Pro Max'),
        (['15', 'pro'], '15 Pro'),
        (['15', 'plus'], '15 Plus'),
        (['15'], '15'),
        
        # iPhone 14 系列
        (['14', 'promax'], '14 Pro Max'),  # 統一使用有空格的格式
        (['14', 'pro'], '14 Pro'),
        (['14', 'plus'], '14 Plus'),
        (['14'], '14'),
        
        # iPhone 13 系列
        (['13', 'promax'], '13 Pro Max'),
        (['13', 'pro'], '13 Pro'),
        (['13', 'mini'], '13 Mini'),
        (['13'], '13'),
        
        # iPhone 12 系列
        (['12', 'promax'], '12 Pro Max'),
        (['12', 'pro'], '12 Pro'),
        (['12', 'mini'], '12 Mini'),
        (['12'], '12'),
        
        # iPhone 11 系列
        (['11', 'promax'], '11 Pro Max'),
        (['11', 'pro'], '11 Pro'),
        (['11'], '11'),
        
        # iPhone X 系列
        (['xsmax'], 'XS Max'),
        (['xs'], 'XS'),
        (['xr'], 'XR'),
        (['x'], 'X'),
        
        # iPhone 8 系列
        (['8', 'plus'], '8 Plus'),
        (['8'], '8'),
        
        # iPhone SE 系列
        (['se'], 'SE'),
    ]
    
    # 依規則檢查
    for keywords, category in rules:
        if all(keyword in model_lower for keyword in keywords):
            return category
    
    return None

def classify_appearance(x):
    if '優' in x:
        return '優'
    elif x == '正常':
        return '好'
    else:
        return x
    
def process_warranty(text):
    """處理保固欄位"""
    text = str(text)
    
    # 1. 包含"三個月"或"3個月"的，都變成"three month"
    if '三個月' in text or '3個月' in text:
        return 'three month'
    
    # 2. 處理日期格式：民國年轉西元年
    
    # 處理 2026年7月8日 或 115年7月8日 格式
    date_pattern_chinese = r'(\d+)年(\d+)月(\d+)日'
    match = re.search(date_pattern_chinese, text)
    
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        
        # 如果年份小於 1911，視為民國年
        if year < 1911:
            year = year + 1911
        
        # 格式化成 YYYY/MM/DD
        return f"{year}/{month:02d}/{day:02d}"
    
    # 處理 115.1.31、2026.03.2、115/4/10 等格式
    date_pattern = r'(\d+)[./](\d+)[./](\d+)'
    match = re.search(date_pattern, text)
    
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        
        # 如果年份小於 1911，視為民國年
        if year < 1911:
            year = year + 1911
        
        # 格式化成 YYYY/MM/DD
        return f"{year}/{month:02d}/{day:02d}"
    
    # 3. 去除所有中文字
    text = re.sub(r'[\u4e00-\u9fff]+', '', text)
    text = text.strip()
    
    return text


if __name__ == "__main__":
    # 設定 Chrome 選項以提升效能
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 無頭模式，不顯示瀏覽器
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # 停用圖片載入
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    # 啟動瀏覽器
    driver = webdriver.Chrome(options=chrome_options)

    try:
        all_data = []
        
        for series in ["se", 8, "x", 11, 12, 13, 14, 15, 16, 17]:
            page = 1
            series_product_count = 0
            
            while True:
                # 進入商品列表頁
                list_url = f"https://www.guardstation.com.tw/categories/second-hand-iphone-{series}-series?page={page}&sort_by=&order_by=&limit=72"
                driver.get(list_url)
                print(f"iPhone {series}: 第 {page} 頁")
                time.sleep(random.uniform(2, 3))
                # 等待商品載入（最多等5秒）
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/products/iphone"]'))
                    )
                except:
                    print(f"第 {page} 頁沒有商品，結束此系列")
                    break
                
                # 收集本頁所有商品網址
                products = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/products/iphone"]')
                product_urls = [p.get_attribute('href') for p in products]
                
                if not product_urls:
                    print(f"總共爬取了 {page - 1} 頁")
                    break
                
                print(f"找到 {len(product_urls)} 個商品")
                
                # 逐一訪問每個商品頁面
                for idx, url in enumerate(product_urls, 1):
                    try:
                        # 直接訪問商品網址
                        driver.get(url)
                        print(f"正在處理第 {idx}/{len(product_urls)} 個商品...")
                        time.sleep(random.uniform(1.5, 2.5))  
                        # 等待商品摘要載入
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "Product-summary"))
                        )
                        
                        # 初始化資料字典
                        data = {
                            "編號": "",
                            "機型": "",
                            "容量": "",
                            "顏色": "",
                            "保固": "",
                            "外觀": "",
                            "功能": "",
                            "分店位置": "",
                            "優惠價格": "",
                            "原價格": ""
                        }
                        
                        # 抓取商品摘要區塊
                        summary_block = driver.find_element(By.CLASS_NAME, "Product-summary")
                        lines = summary_block.text.split('\n')
                        
                        # 解析每一行資料
                        for line in lines:
                            if "編號" in line:
                                data["編號"] = line.split("：")[-1].strip()
                            elif "機型" in line:
                                data["機型"] = line.split("：")[-1].strip()   
                            elif "容量" in line:
                                data["容量"] = line.split("：")[-1].strip()                           
                            elif "顏色" in line:
                                data["顏色"] = line.split("：")[-1].strip()
                            elif "保固" in line:
                                data["保固"] = line.split("：")[-1].strip()
                            elif "外觀" in line:
                                data["外觀"] = line.split("：")[-1].strip()
                            elif "功能" in line:
                                data["功能"] = line.split("：")[-1].strip()
                            elif "分店位置" in line or "店位置" in line:
                                data["分店位置"] = line.split("：")[-1].strip()

                        # 抓取價格
                        try:
                            sale_price = driver.find_element(By.CSS_SELECTOR, ".price-sale").text
                            data["優惠價格"] = sale_price.replace("NT$", "").replace(",", "").strip()
                        except:
                            data["優惠價格"] = ""
                        
                        try:
                            regular_price = driver.find_element(By.CSS_SELECTOR, ".price-regular.price-crossed").text
                            data["原價格"] = regular_price.replace("NT$", "").replace(",", "").strip()
                        except:
                            try:
                                regular_price = driver.find_element(By.CSS_SELECTOR, ".price-regular.price").text
                                data["原價格"] = regular_price.replace("NT$", "").replace(",", "").strip()
                            except:
                                data["原價格"] = ""
                        
                        all_data.append(data)
                        series_product_count += 1
                        print(f"成功抓取: {data['編號']}")

                    except Exception as e:
                        print(f"處理商品時發生錯誤: {e}")
                        continue
                
                page += 1
            
            print(f"\niPhone {series} 系列抓取完成！共 {series_product_count} 個商品")
            print("=" * 60)

        # 將資料轉成 DataFrame
        df = pd.DataFrame(all_data)
        df['系列'] = df['機型'].apply(get_series)
        df['機型'] = df['機型'].str.replace('iPhone ', '')
        df['機型'] = df['機型'].apply(categorize_iphone_model)
        df['外觀'] = df['外觀'].apply(classify_appearance)
        df['保固'] = df['保固'].apply(process_warranty)
        df['保固'] = df['保固'].apply(lambda x: "no warranty" if x == "" else x)
        df['保固_類型'] = df['保固'].apply(lambda x: '店保' if x == 'three month' else ('no warranty' if x == 'no warranty' else '原廠保固'))

        df['價格'] = df['優惠價格'].fillna(df['原價格'])
        df["原價格"] = pd.to_numeric(df["原價格"], errors='coerce')
        df["優惠價格"] = pd.to_numeric(df["優惠價格"], errors='coerce')
        
        # 存入資料庫（使用 append 模式）
        df.to_sql("GS_iphone", con=conn, if_exists="replace", index=False)
        print(f"\n成功新增 {len(df)} 筆商品到資料庫")
        
        # 儲存 CSV
        df.to_csv("guardstation_iphone.csv.csv", index=False, encoding="utf-8-sig")
        print("已儲存至 guardstation_iphone.csv.csv")

        print("\n" + "=" * 60)
        print(f"總共抓取 {len(df)} 筆資料")
        print("=" * 60)
        print("\n抓取完成！")
        
    except Exception as e:
        print(f"發生錯誤: {e}")
        
    finally:
        conn.close()
        driver.quit()
