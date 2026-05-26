import json
from typing import Dict, Any

import streamlit as st
import streamlit.components.v1 as components
import pendulum as pdlm
from ichingshifa import ichingshifa
from ai_module import AIInterpretationModule

# ---- localStorage bridge ----
LS_KEY = "liuyao_ai_settings"


def _ls_init():
    query = st.query_params
    ls_payload = query.get("_ls")
    if ls_payload is not None:
        if ls_payload:
            try:
                st.session_state.ai_settings = json.loads(ls_payload)
            except (json.JSONDecodeError, TypeError):
                pass
        st.query_params.clear()
        return
    if "ai_settings" not in st.session_state:
        components.html(f"""
        <script>
        const d = localStorage.getItem('{LS_KEY}');
        const u = new URL(window.location);
        u.searchParams.set('_ls', d || '');
        window.location.replace(u.toString());
        </script>
        """, height=0)
        st.stop()


def _ls_save(settings_dict):
    components.html(f"""
    <script>
    try {{ localStorage.setItem('{LS_KEY}', '{json.dumps(settings_dict, ensure_ascii=False)}'); }} catch(e) {{}}
    </script>
    """, height=0)


def get_file_content_as_string(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


YAO_OPTIONS = {
    "三枚正面": {"code": "6", "type": "老阴", "symbol": "⚊", "desc": "阴爻发动（变爻）"},
    "两正一反": {"code": "7", "type": "少阳", "symbol": "⚈", "desc": "阳爻不变（静爻）"},
    "两反一正": {"code": "8", "type": "少阴", "symbol": "⚉", "desc": "阴爻不变（静爻）"},
    "三枚反面": {"code": "9", "type": "老阳", "symbol": "⚋", "desc": "阳爻发动（变爻）"},
}

YAO_LABELS = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

# ---- CSS ----
st.set_page_config(layout="wide", page_title="坚六爻-周易排盘")

zhouyi_css = """
<style>
* { box-sizing: border-box; }

.main .block-container {
    background-color: #F7F3E8; color: #2B2B2B; border-radius: 8px;
    padding: 12px !important; max-width: 100%; overflow-x: hidden;
}

[data-testid="stVerticalBlock"] { max-width: 100%; overflow-x: hidden; }

h1, h2, h3, h4, h5, h6 { color: #2B2B2B; font-family: 'SimSun', '宋体', serif; font-weight: bold; }

/* Inputs */
.stTextInput > div > div > input, .stTextArea > div > div > textarea,
.stSelectbox > div > div, .stNumberInput > div > div > input, .stDateInput > div > div > input,
.stTimeInput > div > div > input {
    background-color: #FFFFFF; border: 2px solid #D4AF37; border-radius: 6px;
    color: #2B2B2B; font-family: 'SimSun', '宋体', serif; transition: all 0.3s ease; min-height: 44px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #9E2A2B 0%, #B83640 100%);
    color: #FFFFFF; border: none; border-radius: 6px; padding: 10px 20px;
    font-weight: bold; font-family: 'SimSun', '宋体', serif;
    transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.2); min-height: 44px;
}
.stButton > button:hover { background: linear-gradient(135deg, #B83640 0%, #9E2A2B 100%); transform: translateY(-1px); }

/* Gold secondary button */
.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #D4AF37 0%, #F4E4C1 100%); color: #2B2B2B;
}
.stButton > button[kind="secondary"]:hover { background: linear-gradient(135deg, #F4E4C1 0%, #D4AF37 100%); }

/* Popover (help guide) */
[data-testid="stPopover"] button { min-height: 44px; min-width: 44px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background-color: #EFEBE2; border-radius: 8px; padding: 4px; border: 2px solid #D4AF37; }
.stTabs [data-baseweb="tab"] {
    background-color: transparent; color: #2B2B2B; border-radius: 6px;
    padding: 12px 8px; font-weight: bold; font-family: 'SimSun', '宋体', serif;
    transition: all 0.3s ease; min-height: 44px; flex: 1; text-align: center;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #9E2A2B 0%, #B83640 100%); color: #FFFFFF;
}

/* Expander */
[data-testid="stExpander"] details summary {
    background-color: #EFEBE2; border-radius: 6px; border: 1px solid #D4AF37;
    font-family: 'SimSun', '宋体', serif; font-weight: bold; min-height: 44px;
}

/* Code */
.stCode {
    background-color: #F5F5F5; border: 1px solid #D4AF37; border-radius: 4px;
    font-family: 'Consolas', 'SimSun', monospace; max-width: 100%; overflow-x: auto;
}
.stCode pre, .stCode code { white-space: pre-wrap !important; word-break: break-all; overflow-wrap: break-word; }

hr { border: none; height: 2px; background: linear-gradient(90deg, transparent, #D4AF37, transparent); margin: 12px 0; }

/* Compact selects for yao grid */
.yao-select [data-baseweb="select"] { min-height: 36px !important; }
.yao-select label { font-size: 12px !important; }

/* Wide mode: constrain content */
@media (min-width: 1024px) {
    .main .block-container { max-width: 960px; margin: 0 auto; padding: 20px !important; }
}
@media (max-width: 480px) {
    .main .block-container { padding: 8px !important; }
}
</style>
"""

st.markdown(zhouyi_css, unsafe_allow_html=True)
_ls_init()


# ---- State ----
def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "ai_module" not in st.session_state:
        st.session_state.ai_module = AIInterpretationModule()
    if "ai_settings" not in st.session_state:
        st.session_state.ai_settings = st.session_state.ai_module.load_settings()
    if "ai_reading" not in st.session_state:
        st.session_state.ai_reading = ""
    if "cast_data" not in st.session_state:
        st.session_state.cast_data = None
    if "pp_time" not in st.session_state:
        st.session_state.pp_time = pdlm.now(tz="Asia/Shanghai").time()


def generate_pan_result(y, m, d, h, minute, yao_code):
    return ichingshifa.Iching().display_pan_m(y, m, d, h, minute, yao_code)


def reset_cast():
    st.session_state.cast_data = None
    st.session_state.ai_reading = ""
    st.session_state.page = "home"
    st.rerun()


# ---- Help popover content ----
HELP_TEXT = """
**准备工具**：3枚硬币

**步骤**：
1. 静心凝神，手握3枚硬币
2. 抛掷硬币，统计正反面数量
3. 重复6次，从初爻到上爻记录

| 结果 | 叫法 | 含义 |
|------|------|------|
| 三枚正面 | 老阴 | 变爻 |
| 两正一反 | 少阳 | 静爻 |
| 两反一正 | 少阴 | 静爻 |
| 三枚反面 | 老阳 | 变爻 |
"""


# ---- Home page ----
def render_home_page():
    now = pdlm.now(tz="Asia/Shanghai")
    pp_date = now.date()
    pp_time = st.session_state.pp_time

    # Header row: date | time | question mark | gear
    hc1, hc2, hc3, hc4, hc5 = st.columns([1.5, 1, 0.2, 0.2, 0.2])
    with hc1:
        pp_date = st.date_input("排盘日期", pp_date, label_visibility="collapsed")
    with hc2:
        pp_time = st.time_input("排盘时间", value=pp_time, label_visibility="collapsed")
        st.session_state.pp_time = pp_time
    with hc4:
        with st.popover("?", use_container_width=True):
            st.markdown(HELP_TEXT)
    with hc5:
        if st.button("⚙", key="cfg_home"):
            st.session_state.previous_page = "home"
            st.session_state.page = "ai_settings"
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Yao selector: 3 columns x 2 rows
    yao_code = ""
    for row in range(2):
        cols = st.columns(3)
        for col_i in range(3):
            idx = row * 3 + col_i  # 0-5
            with cols[col_i]:
                choice = st.selectbox(
                    f"第{idx+1}次（{YAO_LABELS[idx]}）",
                    options=list(YAO_OPTIONS.keys()),
                    key=f"yao_{idx}",
                    format_func=lambda name, i=idx: f"{YAO_OPTIONS[name]['symbol']} {name}",
                )
                yao_code += YAO_OPTIONS[choice]["code"]

    st.markdown("<hr>", unsafe_allow_html=True)

    # Question + Button same row
    qc1, qc2 = st.columns([3, 1.2])
    with qc1:
        question = st.text_area(
            "所问何事",
            key="question",
            placeholder="例如：近期事业发展如何？",
            height=60,
            label_visibility="collapsed",
        )
    with qc2:
        st.markdown("<div style='margin-top: 4px;'>", unsafe_allow_html=True)
        cast_btn = st.button("生成排盘", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if cast_btn:
        y, mo, d = pp_date.year, pp_date.month, pp_date.day
        h, minute = pp_time.hour, pp_time.minute
        pan_result = generate_pan_result(y, mo, d, h, minute, yao_code)
        st.session_state.cast_data = {
            "date": str(pp_date),
            "time": str(pp_time),
            "yao_code": yao_code,
            "question": question.strip(),
            "pan_result": str(pan_result),
        }
        st.session_state.ai_reading = ""
        st.session_state.page = "result"
        st.rerun()


# ---- AI Tab ----
def render_ai_tab(pan_result: str):
    if st.session_state.get("ai_reading"):
        # Result mode: show scrollable card + copy/download
        with st.container(height=500):
            st.markdown(st.session_state.ai_reading)

        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("复制结果", key="copy_result", use_container_width=True):
                st.code(st.session_state.ai_reading, language="text")
        with cc2:
            st.download_button(
                label="下载解读",
                data=st.session_state.ai_reading,
                file_name=f"周易解读_{pdlm.now(tz='Asia/Shanghai').format('YYYY-MM-DD_HH-mm-ss')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        return

    # Input mode
    question = st.session_state.get("cast_data", {}).get("question", "")
    question_input = st.text_area(
        "所问何事", value=question, key="result_question", height=60,
    )

    gen_btn = st.button("生成AI解读", type="primary", use_container_width=True)

    if gen_btn:
        settings = st.session_state.get("ai_settings", {})
        if not settings.get("api_key", "").strip():
            st.error("请先配置 API Key（点击右上角齿轮图标）")
            return
        if not question_input.strip():
            st.warning("请输入所问之事")
            return
        with st.spinner("AI正在解读中..."):
            try:
                st.session_state.ai_reading = st.session_state.ai_module.call_llm_api(
                    question=question_input.strip(),
                    pan_result=pan_result,
                    settings=settings,
                )
                st.rerun()
            except ValueError as ve:
                st.error(f"{ve}")
            except Exception as e:
                st.error(f"AI解读失败: {e}")
    else:
        st.info("输入问题后点击上方按钮生成 AI 解读")


# ---- Result page ----
def render_result_page():
    cast_data = st.session_state.get("cast_data")
    if not cast_data:
        reset_cast()
        return

    # Header row: back | info | recast button | gear
    hc1, hc2, hc3, hc4 = st.columns([0.2, 3, 1, 0.3])
    with hc1:
        if st.button("⬅", key="back_home"):
            reset_cast()
    with hc2:
        info = f"{cast_data['date']} {cast_data['time']} | 卦码:{cast_data['yao_code']}"
        if cast_data.get("question"):
            info += f" | {cast_data['question']}"
        st.caption(info)
    with hc3:
        if st.button("重新摇卦", key="recast", use_container_width=True):
            reset_cast()
    with hc4:
        if st.button("⚙", key="cfg_result"):
            st.session_state.previous_page = "result"
            st.session_state.page = "ai_settings"
            st.rerun()

    pan_tab, ai_tab, doc_tab = st.tabs(["卦象", "AI 解读", "文档"])

    with pan_tab:
        with st.container(height=500):
            st.code(cast_data["pan_result"])

    with ai_tab:
        render_ai_tab(cast_data["pan_result"])

    with doc_tab:
        sub1, sub2, sub3 = st.tabs(["占诀", "古占例", "日志"])
        with sub1:
            st.markdown(get_file_content_as_string("text.md"))
        with sub2:
            st.markdown(get_file_content_as_string("example.md"))
        with sub3:
            st.markdown(get_file_content_as_string("update.md"))


# ---- Settings page ----
def render_ai_settings_page():
    ai_module = st.session_state.ai_module
    current_settings = st.session_state.ai_settings

    # Header
    hc1, hc2, hc3 = st.columns([0.2, 3, 0.3])
    with hc1:
        if st.button("⬅", key="back_settings"):
            st.session_state.page = st.session_state.get("previous_page", "home")
            st.rerun()
    with hc2:
        st.markdown("### AI 配置")

    with st.expander("基础设置", expanded=True):
        new_base_url = st.text_input("Base URL", value=current_settings.get("base_url", ""),
                                     placeholder="留空使用 OpenAI 默认")
        new_api_key = st.text_input("API Key", value=current_settings.get("api_key", ""),
                                    type="password", placeholder="请输入API密钥")

        # Model + Temperature same row
        mc1, mc2 = st.columns([2, 1])
        with mc1:
            new_model = st.text_input("模型名称", value=current_settings.get("model", "gpt-4o-mini"))
        with mc2:
            new_temperature = st.slider("温度", 0.0, 1.0,
                                        float(current_settings.get("temperature", 0.7)), 0.1)

    with st.expander("提示词设置", expanded=False):
        new_system_prompt = st.text_area("系统提示词",
                                         value=current_settings.get("system_prompt", ""), height=180)
        new_user_prompt = st.text_area("用户提示词模板",
                                       value=current_settings.get("user_prompt_template", ""), height=300,
                                       help="使用 {question} 和 {pan_result} 作为占位符")

    with st.expander("高级选项", expanded=False):
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            new_max_tokens_val = st.number_input("最大Token数", value=current_settings.get("max_tokens") or 0,
                                                 min_value=0, help="0表示不限制")
        with ac2:
            new_timeout = st.number_input("超时(秒)", value=float(current_settings.get("timeout", 60.0)),
                                          min_value=1.0, max_value=300.0)
        with ac3:
            new_max_retries = st.number_input("重试次数", value=int(current_settings.get("max_retries", 3)),
                                              min_value=0, max_value=10)

    # Save / Reset
    sc1, sc2 = st.columns(2)
    with sc1:
        if st.button("重置默认", use_container_width=True, key="reset_defaults"):
            if ai_module.save_settings(ai_module.default_settings):
                st.session_state.ai_settings = ai_module.default_settings.copy()
                _ls_save(ai_module.default_settings)
                st.success("已重置为默认配置")
                st.rerun()
    with sc2:
        if st.button("保存配置", type="primary", use_container_width=True, key="save_cfg"):
            new_settings = {
                "base_url": str(new_base_url).strip(),
                "api_key": str(new_api_key).strip(),
                "model": str(new_model).strip() or "gpt-4o-mini",
                "temperature": new_temperature,
                "system_prompt": str(new_system_prompt).strip(),
                "user_prompt_template": str(new_user_prompt).strip(),
                "max_tokens": new_max_tokens_val if new_max_tokens_val else None,
                "timeout": new_timeout,
                "max_retries": new_max_retries,
            }
            if ai_module.save_settings(new_settings):
                st.session_state.ai_settings = new_settings
                _ls_save(new_settings)
                st.success("AI配置已保存到浏览器")
                st.rerun()

    current_api_key = current_settings.get("api_key", "").strip()
    if current_api_key:
        st.success("API Key 已配置")
    else:
        st.warning("请配置 API Key 以使用 AI 解读功能")


# ---- Main router ----
init_state()

if st.session_state.page == "home":
    render_home_page()
elif st.session_state.page == "result":
    render_result_page()
elif st.session_state.page == "ai_settings":
    render_ai_settings_page()
else:
    st.session_state.page = "home"
    st.rerun()
