import html
import json

import streamlit as st
import streamlit.components.v1 as components
import pendulum as pdlm
from ichingshifa import ichingshifa
from ai_module import AIInterpretationModule

# ---- localStorage bridge ----
LS_KEY = "liuyao_ai_settings"


def _ls_init():
    if "ai_settings" in st.session_state:
        return
    query = st.query_params
    ls_payload = query.get("_ls")
    if ls_payload is not None and ls_payload:
        try:
            st.session_state.ai_settings = json.loads(ls_payload)
        except (json.JSONDecodeError, TypeError):
            pass
        st.query_params.clear()
        return
    components.html(f"""
    <script>
    const d = localStorage.getItem('{LS_KEY}');
    if (d) {{
        const u = new URL(window.location);
        u.searchParams.set('_ls', d);
        window.location.replace(u.toString());
    }}
    </script>
    """, height=0)
    if ls_payload is not None:
        st.query_params.clear()


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
    "三枚正面": {"code": "6", "type": "老阴", "symbol": "⚋ x", "desc": "阴爻发动（变爻）"},
    "两正一反": {"code": "7", "type": "少阳", "symbol": "⚊", "desc": "阳爻不变（静爻）"},
    "两反一正": {"code": "8", "type": "少阴", "symbol": "⚋", "desc": "阴爻不变（静爻）"},
    "三枚反面": {"code": "9", "type": "老阳", "symbol": "⚊ o", "desc": "阳爻发动（变爻）"},
}

YAO_LABELS = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

# ---- CSS ----
st.set_page_config(layout="wide", page_title="坚六爻-周易排盘")

zhouyi_css = """
<style>
:root {
    --paper: #F7F3E8;
    --dark: #2B2B2B;
    --cinnabar: #9E2A2B;
    --cinnabar-hover: #B83640;
    --gold: #D4AF37;
    --gold-light: #F4E4C1;
}

* { box-sizing: border-box; }

/* body / block-container */
.main .block-container {
    background-color: var(--paper); color: var(--dark);
    border-radius: 0; padding: 0 !important; max-width: 100%; overflow-x: hidden;
}

/* Hide Streamlit header/footer chrome */
[data-testid="stHeader"] { display: none; }
[data-testid="stToolbar"] { display: none; }
footer { display: none; }

h1, h2, h3, h4, h5, h6 {
    color: var(--dark); font-family: 'SimSun', '宋体', serif; font-weight: bold;
}

/* ===== Header bar ===== */
.header-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 12px; gap: 8px;
    border-bottom: 2px solid var(--gold);
    background: rgba(247, 243, 232, 0.9);
    backdrop-filter: blur(8px);
}

/* ===== Card ===== */
.card {
    background: #FFFFFF; border: 1px solid var(--gold); border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* ===== Input fields ===== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTimeInput > div > div > input {
    background-color: #FFFFFF !important;
    border: 2px solid var(--gold) !important;
    border-radius: 6px !important;
    color: var(--dark) !important;
    font-family: 'SimSun', '宋体', serif !important;
    min-height: 44px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div:focus-within {
    border-color: var(--cinnabar) !important;
    box-shadow: 0 0 0 2px rgba(158, 42, 43, 0.2) !important;
}

/* ===== Buttons ===== */
.stButton > button {
    background: var(--cinnabar) !important; color: #FFFFFF !important;
    border: none !important; border-radius: 8px !important;
    padding: 8px 16px !important; font-weight: bold !important;
    font-family: 'SimSun', '宋体', serif !important;
    min-height: 44px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: var(--cinnabar-hover) !important;
}
.stButton > button:active {
    transform: scale(0.98) !important;
}

/* Gold secondary button */
.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%) !important;
    color: var(--dark) !important;
}

/* Icon buttons (back, ?, gear) */
.icon-btn > button {
    min-width: 44px !important; width: 44px !important;
    padding: 8px !important; font-size: 18px !important;
    background: transparent !important; color: var(--cinnabar) !important;
    box-shadow: none !important;
}
.icon-btn > button:hover {
    color: var(--cinnabar-hover) !important;
    background: transparent !important;
}

/* ===== Tabs ===== */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid var(--gold) !important;
    border-radius: 0 !important; padding: 0 !important;
    display: flex !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    flex: 1 1 0 !important; text-align: center !important;
    padding: 12px 4px !important; min-height: 44px !important;
    font-weight: bold !important; font-family: 'SimSun', '宋体', serif !important;
    font-size: 14px !important; color: var(--dark) !important;
    background: transparent !important; border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--cinnabar) 0%, var(--cinnabar-hover) 100%) !important;
    color: #FFFFFF !important;
}

/* Nested tabs (文档) */
.stTabs .stTabs [data-baseweb="tab-list"] {
    border: 1px solid var(--gold) !important; border-radius: 6px !important;
    padding: 2px !important; margin: 4px 0 !important;
}
.stTabs .stTabs [data-baseweb="tab"] {
    border-radius: 6px !important; padding: 8px 4px !important;
    min-height: 36px !important; font-size: 13px !important;
}

/* ===== Expander ===== */
[data-testid="stExpander"] details summary {
    font-family: 'SimSun', '宋体', serif; font-weight: bold;
    min-height: 44px; color: var(--cinnabar);
    border-bottom: 1px solid var(--gold);
}
[data-testid="stExpander"] details > div {
    padding: 8px 0 !important;
}

/* ===== Code blocks ===== */
.stCode {
    background: #F5F5F5 !important;
    border: none !important; border-radius: 0 !important;
    font-family: 'Consolas', 'SimSun', monospace !important;
}
.stCode pre, .stCode code {
    white-space: pre !important; overflow-x: auto !important;
    }

/* ===== Messages (success/error/warning/info) ===== */
.stSuccess, .stWarning, .stError, .stInfo {
    font-family: 'SimSun', '宋体', serif; border-radius: 6px;
}

hr {
    border: none; height: 1px;
    background: var(--gold); opacity: 0.3; margin: 12px 0;
}

/* ===== Column alignment ===== */
[data-testid="stHorizontalBlock"] { align-items: center !important; gap: 8px !important; }

/* ===== Yao grid ===== */
.yao-cell-label { font-size: 12px !important; color: var(--cinnabar) !important;
                  font-family: 'SimSun', '宋体', serif !important; font-weight: bold !important;
                  margin: 0 0 2px 0 !important; }

/* ===== Desktop max-width (matches React lg/xl breakpoints) ===== */
@media (min-width: 1024px) {
    .main .block-container {
        max-width: 720px; margin: 0 auto;
        border-left: 1px solid var(--gold);
        border-right: 1px solid var(--gold);
        min-height: 100vh;
    }
    [data-testid="stHorizontalBlock"] { gap: 12px !important; }
}
@media (min-width: 1280px) {
    .main .block-container { max-width: 900px; }
}

/* ===== Mobile portrait (≤640px) ===== */
@media (max-width: 640px) {
    .main .block-container { padding: 6px !important; }


    /* Tabs: horizontal scroll, compact */
    .stTabs [data-baseweb="tab"] {
        padding: 10px 2px !important; font-size: 12px !important;
        flex: 0 0 auto !important; min-width: fit-content !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto !important; flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
    }

    /* Nested tabs: smaller */
    .stTabs .stTabs [data-baseweb="tab"] {
        padding: 8px 4px !important; font-size: 11px !important;
        min-height: 36px !important;
    }

    /* Code: smaller font */
    .stCode code, .stCode pre { font-size: 11px !important; }

    /* Buttons: full-width */
    .stButton > button { padding: 8px 12px !important; }

    /* Info text: allow wrapping */
    .stCaption { white-space: normal !important; }

    /* Expander: compact */
    [data-testid="stExpander"] details summary { padding: 8px !important; }

    /* Selectbox in yao grid: compact */
    .stSelectbox [data-baseweb="select"] { min-height: 40px !important; }
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
    if "show_help" not in st.session_state:
        st.session_state.show_help = False


def generate_pan_result(y, m, d, h, minute, yao_code):
    return ichingshifa.Iching().display_pan_m(y, m, d, h, minute, yao_code)


def reset_cast():
    st.session_state.cast_data = None
    st.session_state.ai_reading = ""
    st.session_state.page = "home"
    st.rerun()


# ---- Help content ----
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


# ================================================================
#  Home page  —— 对照 React HomePage.tsx
# ================================================================
def render_home_page():
    now = pdlm.now(tz="Asia/Shanghai")
    pp_date = now.date()
    pp_time = st.session_state.pp_time

    # ---- Header bar: date | time | ? | gear ----
    hc1, hc2, hc3, hc4 = st.columns([2, 1.2, 0.5, 0.5])
    with hc1:
        pp_date = st.date_input("排盘日期", pp_date, label_visibility="collapsed")
    with hc2:
        pp_time = st.time_input("排盘时间", value=pp_time, label_visibility="collapsed")
        st.session_state.pp_time = pp_time
    with hc3:
        help_clicked = st.button("?", key="help_btn")
        if help_clicked:
            st.session_state.show_help = not st.session_state.get("show_help", False)
    with hc4:
        if st.button("⚙", key="cfg_home"):
            st.session_state.previous_page = "home"
            st.session_state.page = "ai_settings"
            st.rerun()

    st.markdown('<div class="header-bar-spacer" style="height:0;"></div>', unsafe_allow_html=True)

    if st.session_state.show_help:
        with st.expander("如何摇卦？", expanded=True):
            st.markdown(HELP_TEXT)

    # ---- Yao grid (matching React YaoSelector: grid-cols-3 gap-2) ----
    st.markdown("### 设定爻位")
    st.caption("从第一次（初爻）开始，依次向上填写到第六次（上爻）")

    yao_code = ""
    for row in range(2):
        cols = st.columns(3)
        for col_i in range(3):
            idx = row * 3 + col_i
            with cols[col_i]:
                choice = st.selectbox(
                    YAO_LABELS[idx],
                    options=list(YAO_OPTIONS.keys()),
                    key=f"yao_{idx}",
                    format_func=lambda name: f"{YAO_OPTIONS[name]['symbol']}  {name}",
                )
                yao_code += YAO_OPTIONS[choice]["code"]

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---- Question + Button same row ----
    qc1, qc2 = st.columns([3, 1])
    with qc1:
        question = st.text_area(
            "所问何事",
            key="question",
            placeholder="所问何事？如：近期事业发展如何？",
            height=48,
            label_visibility="collapsed",
        )
    with qc2:
        cast_btn = st.button("生成排盘", type="primary", use_container_width=True)

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
        st.session_state.ai_requested = True
        st.session_state.ai_error = ""
        st.session_state.page = "result"
        st.rerun()


# ================================================================
#  Result page  —— 自动调用 AI + 标签页
# ================================================================
def render_result_page():
    cast_data = st.session_state.get("cast_data")
    if not cast_data:
        reset_cast()
        return

    settings = st.session_state.get("ai_settings", {})
    has_key = bool(settings.get("api_key", "").strip())
    question = cast_data.get("question", "").strip()
    ai_ready = bool(st.session_state.get("ai_reading"))
    ai_error = st.session_state.get("ai_error", "")
    ai_waiting = (
        st.session_state.get("ai_requested")
        and not ai_ready
        and not ai_error
        and has_key
        and question
    )

    # ---- Auto AI call (before tabs render) ----
    if ai_waiting:
        st.session_state.ai_requested = False
        with st.spinner("AI 正在解读中，请稍候..."):
            try:
                st.session_state.ai_reading = (
                    st.session_state.ai_module.call_llm_api(
                        question=question,
                        pan_result=cast_data["pan_result"],
                        settings=settings,
                    )
                )
            except ValueError as ve:
                st.session_state.ai_error = str(ve)
            except Exception as e:
                st.session_state.ai_error = f"AI解读失败: {e}"
        st.rerun()

    # ---- Header: back | info | recast | gear ----
    hc1, hc2, hc3, hc4 = st.columns([0.2, 3, 1.5, 0.35])
    with hc1:
        if st.button("‹", key="back_home", help="返回首页"):
            reset_cast()
    with hc2:
        info = f"{cast_data['date']}  {cast_data['time']}  |  卦码: {cast_data['yao_code']}"
        if cast_data.get("question"):
            info += f"  |  {cast_data['question']}"
        st.markdown(
            f'<p style="font-size:12px;color:#666;margin:8px 0;overflow:hidden;'
            f'text-overflow:ellipsis;white-space:nowrap;">{info}</p>',
            unsafe_allow_html=True,
        )
    with hc3:
        if st.button("重新摇卦", key="recast", type="secondary", use_container_width=True):
            reset_cast()
    with hc4:
        if st.button("⚙", key="cfg_result"):
            st.session_state.previous_page = "result"
            st.session_state.page = "ai_settings"
            st.rerun()

    # ---- Disable 解读 tab when no content ----
    if not ai_ready:
        st.markdown(
            '<style>'
            '.stTabs > div > [role="tablist"] > [role="tab"]:nth-child(2) '
            '{pointer-events:none !important;opacity:0.45 !important;cursor:not-allowed !important;}'
            '</style>',
            unsafe_allow_html=True,
        )

    # ---- 3 Tabs ----
    pan_tab, ai_tab, doc_tab = st.tabs(["卦象", "解读", "文档"])

    with pan_tab:
        with st.container(height=450):
            st.code(cast_data["pan_result"])

    with ai_tab:
        if ai_ready:
            with st.container(height=450):
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
        elif ai_error:
            st.error(ai_error)
        elif not has_key:
            st.info("请先配置 API Key 以使用解读功能（点击右上角齿轮图标）")
        else:
            st.info("解读内容生成中，请稍候...")

    with doc_tab:
        sub1, sub2, sub3 = st.tabs(["占诀", "古占例", "日志"])
        with sub1:
            st.markdown(get_file_content_as_string("text.md"))
        with sub2:
            st.markdown(get_file_content_as_string("example.md"))
        with sub3:
            st.markdown(get_file_content_as_string("update.md"))


# ================================================================
#  Settings page  —— 对照 React SettingsPage.tsx
# ================================================================
def render_ai_settings_page():
    ai_module = st.session_state.ai_module
    current_settings = st.session_state.ai_settings

    # ---- Header: back | title ----
    hc1, hc2 = st.columns([0.12, 3])
    with hc1:
        if st.button("‹", key="back_settings", help="返回"):
            st.session_state.page = st.session_state.get("previous_page", "home")
            st.rerun()
    with hc2:
        st.markdown(
            '<h1 style="font-size:18px;color:#9E2A2B;margin:4px 0;">AI 配置</h1>',
            unsafe_allow_html=True,
        )

    # ---- 基础设置 ----
    with st.expander("基础设置", expanded=True):
        new_base_url = st.text_input(
            "Base URL", value=current_settings.get("base_url", ""),
            placeholder="自定义 API 地址（可选，留空使用 OpenAI 默认）",
        )
        new_api_key = st.text_input(
            "API Key", value=current_settings.get("api_key", ""),
            type="password", placeholder="请输入 API 密钥",
        )

        mc1, mc2 = st.columns([2, 1.2])
        with mc1:
            new_model = st.text_input(
                "模型名称", value=current_settings.get("model", "gpt-4o-mini"),
            )
        with mc2:
            new_temperature = st.slider(
                "温度", 0.0, 1.0,
                float(current_settings.get("temperature", 0.7)), 0.1,
            )

    # ---- 提示词设置 ----
    with st.expander("提示词设置"):
        new_system_prompt = st.text_area(
            "系统提示词", value=current_settings.get("system_prompt", ""),
            height=180,
        )
        new_user_prompt = st.text_area(
            "用户提示词模板",
            value=current_settings.get("user_prompt_template", ""),
            height=240,
            help="使用 {question} 和 {pan_result} 作为占位符",
        )

    # ---- 高级选项 (collapsible) ----
    with st.expander("高级选项"):
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            new_max_tokens_val = st.number_input(
                "Token 数", value=current_settings.get("max_tokens") or 0,
                min_value=0, help="0 = 不限制",
            )
        with ac2:
            new_timeout = st.number_input(
                "超时(秒)", value=float(current_settings.get("timeout", 60.0)),
                min_value=1.0, max_value=300.0,
            )
        with ac3:
            new_max_retries = st.number_input(
                "重试次数", value=int(current_settings.get("max_retries", 3)),
                min_value=0, max_value=10,
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---- Status ----
    if current_settings.get("api_key", "").strip():
        st.success("API Key 已配置")
    else:
        st.warning("请配置 API Key 以使用 AI 解读功能")

    # ---- Actions (Save / Reset) ----
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
