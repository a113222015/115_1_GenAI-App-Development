# 社團公告行動清單

作者：蕭湘傑

## 使用者與問題

社團新成員每天被群組的長篇公告洗版，看不出自己要做什麼、哪些資訊沒寫清楚。
本工具把一則公告整理成「我要做的事」與「公告沒說清楚、需要去問的事」，並且不補造原文沒有的時間與地點。

## App 網址與雲端驗收

- App 網址：https://1151genai-app-development-7fn2tqkfw7a2cjhwagfhms.streamlit.app
- 部署：a113222015/115_1_GenAI-App-Development／main／`Midterm Mini-Project/app.py`
- Cloud Python 版本：3.14.10
- 驗收日期：2026-11-05，結果：成功（兩筆雲端真實 API 成功，見下方）
- 老師觀看權限：公開（任何人可開啟，未設定存取限制）

## 為什麼採用 Pydantic

欄位用 Python 類別定義，型別與 `extra="forbid"`（禁止多餘欄位）寫在同一處，
以 `responses.parse(text_format=ProjectResult)` 取得結構化結果，比手寫 JSON Schema 不易出錯。

## 輸入與輸出欄位

輸入：貼上純文字公告，上限 6000 字元。

| 欄位 | 型別 | 用途 | 畫面標籤 |
|---|---|---|---|
| event_name | str | 知道是什麼活動 | 活動名稱 |
| time_and_place | str | 知道何時何地，沒寫則「公告未提供」 | 時間與地點 |
| action_items | list[str] | 我下一步要做什麼 | 我要做的事 |
| missing_info | list[str] | 列出需要去問的事，防止補造 | 公告沒說清楚（需要去問） |

全部欄位必填。

## 安裝與啟動（本機）

```powershell
cd "Midterm Mini-Project"
python -m venv .venv
.venv\Scripts\activate
pip install streamlit openai pydantic python-dotenv
streamlit run app.py
```

## 設定方式

- 本機：複製 `.env.example` 為 `.env`，填入 `OPENAI_API_KEY`（`OPENAI_MODEL` 預設 gpt-5.4-mini）。
- 雲端：在 Streamlit Community Cloud 的 Secrets 填入，格式見 `.streamlit/secrets.example.toml`。
- `.env`、`.streamlit/secrets.toml`、`.venv/` 不提交。
- 依賴清單：因資料夾名稱含空格，雲端安裝程式無法解析 `Midterm Mini-Project/requirements.txt`，
  因此雲端改用 Repo 根目錄的 `requirements.txt`（已補上 pydantic）。

## 操作範例（虛構資料）

開啟「啟用 API」開關後貼上公告並按「整理公告」。

**正常**：「各位新社員好！本週六 11/14 下午兩點在學生活動中心 B2 舉辦迎新茶會，請於 11/10 前到表單填寫是否參加，並攜帶學生證入場。」
→ 活動名稱：迎新茶會；時間與地點：本週六 11/14 下午兩點在學生活動中心 B2；
行動：11/10 前填表單、帶學生證；需要去問：表單連結在哪裡？

**資訊不足**：「這週有迎新活動，大家記得來喔，要帶東西！」
→ 時間與地點：公告未提供；需要去問：活動時間、活動地點、需要帶什麼東西。沒有補造。

## 實測與未測項目

已測（2026-11-05，gpt-5.4-mini）：

| 項目 | 環境 | 結果 | 請求數 |
|---|---|---|---|
| 過長（6002 字） | 本機 | 請求前擋下 | 0 |
| 空白 | 雲端 | 請求前擋下 | 0 |
| API 關閉送「測試」 | 雲端 | 請求前擋下 | 0 |
| 成功後送空白（舊結果清除） | 雲端 | 舊結果消失，只剩錯誤 | 0 |
| 非公告輸入「123」 | 本機 | 活動名稱「無法判斷」，沒有補造 | 1 |
| 正常資料 | 雲端 | 四欄皆有原文依據 | 1 |
| 資訊不足 | 雲端 | 沒有補造，缺漏三項命中 | 1 |

未測：本機空白、雲端過長、缺金鑰／服務失敗。

完整輸入輸出與逐欄核對見 `第08週_課堂簡化版_專題設計與驗收紀錄.md`。

## 成本與限制

- 實際請求共 3 次（本機邊界 1、雲端正式 2）。每次提交最多 1 次請求，`max_retries=0`，API 預設關閉。
- 6000 字元是成本護欄，不是 token 上限。
- 格式合法不代表內容有用，例如曾出現「攜帶需要帶的東西」這類循環語句。
- 雲端與本機的套件版本不同，目前只實測過雲端的上述情境。
- 若 App 為公開，任何人拿到網址都能開啟 API 開關並消耗額度。

## AI 協助說明

使用 Claude 協助：整理專題要求、建議題目與欄位、提供 app.py 範本與 INSTRUCTIONS 初稿、引導環境建置、判讀部署錯誤 log、整理驗收紀錄與 README。
自己親自完成：建立專案與安裝、設定金鑰與 Secrets、操作本機與雲端測試、逐欄核對輸出、依雲端 log 執行部署解法。
自己的修改：程式主要採用 AI 提供的範本，目前尚未大幅修改。個人設計集中在題目與使用情境（社團公告）、四個欄位的取捨，以及依測試結果發現的問題（「攜帶需要帶的東西」循環語句）所做的觀察與記錄。測試資料皆為虛構。