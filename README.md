# 故宮繪畫桌布 (NPM Painting Wallpaper)

本專案透過 [故宮典藏資料檢索](https://digitalarchive.npm.gov.tw/Collection) 的 **Open Data 開放資料**，抓取**繪畫類**圖像，使用者可簡易取得隨機畫作並設定為桌布。

This project uses **Open Data** from the [National Palace Museum Collection](https://digitalarchive.npm.gov.tw/Collection) to fetch **painting** images. You can easily get a random artwork and set it as your wallpaper.

## 專案結構

```
npm-painting-wallpaper
├── start.py           # 主程式：HTTP 服務與故宮 API 串接
├── requirements.txt
├── Dockerfile         # Cloud Run 容器建置
├── .dockerignore
├── README.md
└── .gitignore
```

## 功能

- 從故宮數位典藏系統隨機取得繪畫類文物
- 以 IIIF 規格取得高解析度圖像
- 提供本地 HTTP 服務：`GET /` 或 `GET /random` 回傳 JSON（含 `title`、`image_url`、`height`、`width`），可搭配腳本或前端下載圖片並設為桌布

## 使用方式

### 環境需求

- Python 3.x
- 依賴：見 `requirements.txt`

```bash
pip install -r requirements.txt
```

### 啟動服務

```bash
python start.py
```

預設於 `http://localhost:8000/` 提供服務：

- **GET /** 或 **GET /random**：回傳一筆隨機繪畫資料（JSON），內含 `title`、`image_url`、`height`、`width`、`cc_title`（已含 CC BY 4.0 英文標示，可作為圖檔出處）等欄位，可依此下載圖片並設為桌布。

部署至 **Google Cloud Run** 的步驟請見 [DEPLOY_GCP.md](DEPLOY_GCP.md)。

---

## 資料來源與授權標示

本專案所使用之圖像來自**國立故宮博物院**開放資料，並使用**中階圖像**（約 600 萬畫素）。

依據故宮「網站資料開放宣告」：

- **低階圖像**（約 100 萬畫素）：以「公眾領域貢獻宣告」（CC0）規範，不須註明出處。
- **中階圖像**（約 600 萬畫素）：以 **CC 授權條款 4.0** 之 **CC BY 姓名標示**規範，無須申請、不限用途、不用付費即可公開使用，**惟需於適當位置呈現姓名標示**（中文或英文擇一）。

### 本專案之姓名標示（請於使用圖檔之適當位置呈現）

**中文表示型式：**

> [品名] 國立故宮博物院，臺北，CC BY 4.0 @ www.npm.gov.tw

**英文表示型式：**

> [Artwork Title] The National Palace Museum, Taipei, CC BY 4.0 @ www.npm.gov.tw

上述「品名」/「Artwork Title」請以本專案 API 回傳之 `title` 欄位（文物名稱）代入。  
例如：若 `title` 為「清 王翬 畫山水」，則標示為：

- 中文：**清 王翬 畫山水** 國立故宮博物院，臺北，CC BY 4.0 @ www.npm.gov.tw  
- 英文：**清 王翬 畫山水** The National Palace Museum, Taipei, CC BY 4.0 @ www.npm.gov.tw  

低階、中階圖像均無需申請、不限用途、不用付費，可直接下載與公開使用（不包括專利權及商標權）。使用開放資料圖檔製作之製成品，應避免使他人誤認為係國立故宮博物院所製作。

---

## 相關連結

- [故宮典藏資料檢索](https://digitalarchive.npm.gov.tw/Collection)
- [國立故宮博物院官網](https://www.npm.gov.tw)
