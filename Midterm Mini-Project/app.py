import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict

load_dotenv()

# ---------- A：任務定位 ----------
APP_TITLE = "社團公告行動清單"
INSTRUCTIONS = """你是社團公告整理助手，使用者是看不完群組長訊息的新社員。
只能依據「原文」整理，不得補造原文沒有的時間、地點、人名、金額。
原文沒寫的資訊，不要猜；在 missing_info 列出『我需要去問的事』。
time_and_place 若原文沒有，填「公告未提供」。
action_items 只放使用者需要採取的行動，每項一句話。
若原文完全不是活動公告，event_name 填「無法判斷」，其餘照規則處理。"""

# ---------- B：資料契約 ----------
class ProjectResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_name: str
    time_and_place: str
    action_items: list[str]
    missing_info: list[str]

# ---------- C：顯示標籤 ----------
FIELD_LABELS = {
    "event_name": "活動名稱",
    "time_and_place": "時間與地點",
    "action_items": "我要做的事",
    "missing_info": "公告沒說清楚（需要去問）",
}

MAX_CHARS = 6000
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")


def get_api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def check_input(text: str):
    if not text.strip():
        return "請先貼上公告內容。"
    if len(text) > MAX_CHARS:
        return f"內容過長（{len(text)} 字），上限 {MAX_CHARS} 字。"
    return None


def call_model(text: str, key: str) -> dict:
    client = OpenAI(api_key=key, max_retries=0, timeout=60)
    resp = client.responses.parse(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=f"原文：\n{text}",
        text_format=ProjectResult,
    )
    if resp.status != "completed" or resp.output_parsed is None:
        raise ValueError("模型未完成或拒答，沒有可用結果。")
    return resp.output_parsed.model_dump()


# ---------- 主流程 ----------
st.set_page_config(page_title=APP_TITLE)
st.title(APP_TITLE)
st.caption("貼上社團公告，整理成『我要做什麼』與『還缺什麼資訊』。")

api_on = st.toggle("啟用 API（會產生請求）", value=False)

with st.form("main_form"):
    text = st.text_area("公告原文", height=220)
    submitted = st.form_submit_button("整理公告")

if submitted:
    st.session_state.pop("record", None)
    st.session_state.pop("error", None)
    err = check_input(text)
    key = get_api_key()
    if err:
        st.session_state.error = err
    elif not api_on:
        st.session_state.error = "API 目前關閉，請先開啟開關。"
    elif not key:
        st.session_state.error = "找不到 OPENAI_API_KEY，請檢查 .env 或 Secrets。"
    else:
        try:
            with st.spinner("整理中…"):
                data = call_model(text, key)
            st.session_state.record = {"text": text, "data": data}
        except Exception as e:
            st.session_state.error = f"發生錯誤：{type(e).__name__}"

if "error" in st.session_state:
    st.error(st.session_state.error)

if "record" in st.session_state:
    rec = st.session_state.record
    st.success("整理完成（請對照原文逐欄核對）")
    for field, value in rec["data"].items():
        st.subheader(FIELD_LABELS.get(field, field))
        if isinstance(value, list):
            if value:
                for item in value:
                    st.markdown(f"- {item}")
            else:
                st.write("（無）")
        else:
            st.write(value)
    with st.expander("本次原文"):
        st.write(rec["text"])