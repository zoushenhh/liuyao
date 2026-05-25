import urllib.request
import json
from typing import Dict, Any, List

import streamlit as st
import streamlit.components.v1 as components
import pendulum as pdlm
from ichingshifa import ichingshifa

# 导入自定义模块
from ai_module import AIInterpretationModule

# ---- localStorage 桥接：API 配置存浏览器 ----
LS_KEY = "liuyao_ai_settings"


def _ls_init():
    """页面首次加载时从浏览器 localStorage 恢复配置。"""
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
    """保存配置到浏览器 localStorage。"""
    components.html(f"""
    <script>
    try {{ localStorage.setItem('{LS_KEY}', '{json.dumps(settings_dict, ensure_ascii=False)}'); }} catch(e) {{}}
    </script>
    """, height=0)


def get_file_content_as_string(path):
    """优先读本地文件，不存在则从 ichingshifa 仓库拉取"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        try:
            url = 'https://raw.githubusercontent.com/kentang2017/ichingshifa/master/' + path
            response = urllib.request.urlopen(url)
            return response.read().decode("utf-8")
        except Exception:
            return ""

def get_file_content_as_string1(path):
    """优先读本地文件，不存在则从 kinliuren 仓库拉取"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        try:
            url = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/' + path
            response = urllib.request.urlopen(url)
            return response.read().decode("utf-8")
        except Exception:
            return ""

st.set_page_config(layout="wide",page_title="坚六爻-周易排盘")

# 注入中国周易风格的CSS样式（含移动端适配）
zhouyi_css = """
<style>
/* ============================================
   1. 全局背景与基础 - 宣纸色
   ============================================ */
.main .block-container {
    background-color: #F7F3E8;
    color: #2B2B2B;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1, h2, h3, h4, h5, h6 {
    color: #2B2B2B;
    font-family: 'SimSun', '宋体', serif;
    font-weight: bold;
}

/* ============================================
   2. 侧边栏样式（data-testid 替代过时 hash class）
   ============================================ */
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #EFEBE2 0%, #E8DDD0 100%);
    border-right: 3px solid #D4AF37;
}

[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stTextInput > div > div > input,
[data-testid="stSidebar"] .stNumberInput > div > div > input {
    background-color: #FFFFFF;
    border: 2px solid #D4AF37;
    border-radius: 4px;
    color: #2B2B2B;
}

/* ============================================
   3. 输入组件通用样式 + 触摸优化 (min-height: 44px)
   ============================================ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background-color: #FFFFFF;
    border: 2px solid #D4AF37;
    border-radius: 6px;
    color: #2B2B2B;
    font-family: 'SimSun', '宋体', serif;
    transition: all 0.3s ease;
    min-height: 44px;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div:focus-within,
.stNumberInput > div > div > input:focus {
    border-color: #9E2A2B;
    box-shadow: 0 0 0 2px rgba(158, 42, 43, 0.2);
}

/* ============================================
   4. 按钮样式 - 朱砂红 + 触摸优化
   ============================================ */
.stButton > button {
    background: linear-gradient(135deg, #9E2A2B 0%, #B83640 100%);
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-family: 'SimSun', '宋体', serif;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    min-height: 44px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #B83640 0%, #9E2A2B 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #D4AF37 0%, #F4E4C1 100%);
    color: #2B2B2B;
    box-shadow: 0 2px 6px rgba(212, 175, 55, 0.4);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #F4E4C1 0%, #D4AF37 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(212, 175, 55, 0.6);
}

/* ============================================
   5. Tab 标签页样式
   ============================================ */
.stTabs [data-baseweb="tab-list"] {
    background-color: #EFEBE2;
    border-radius: 8px;
    padding: 5px;
    border: 2px solid #D4AF37;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #2B2B2B;
    border-radius: 6px;
    padding: 12px 24px;
    font-weight: bold;
    font-family: 'SimSun', '宋体', serif;
    transition: all 0.3s ease;
    min-height: 44px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #9E2A2B 0%, #B83640 100%);
    color: #FFFFFF;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* ============================================
   6. Expander 样式（data-testid 替代过时 class）
   ============================================ */
[data-testid="stExpander"] details summary {
    background-color: #EFEBE2;
    border-radius: 6px;
    border: 1px solid #D4AF37;
    font-family: 'SimSun', '宋体', serif;
    font-weight: bold;
    min-height: 44px;
}

[data-testid="stExpander"] details[open] summary {
    border-radius: 6px 6px 0 0;
}

[data-testid="stExpander"] details > div {
    background-color: #FFFFFF;
    border-radius: 0 0 6px 6px;
    border: 1px solid #D4AF37;
    border-top: none;
    padding: 1rem;
}

/* ============================================
   7. 其他 UI 组件
   ============================================ */
.stSlider > div > div > div {
    background: linear-gradient(90deg, #D4AF37 0%, #9E2A2B 100%);
}

.stSuccess { background-color: #E8F5E8; border-left: 4px solid #4CAF50; color: #2B2B2B; }
.stWarning { background-color: #FFF3E0; border-left: 4px solid #D4AF37; color: #2B2B2B; }
.stError   { background-color: #FFEBEE; border-left: 4px solid #9E2A2B; color: #2B2B2B; }
.stInfo    { background-color: #E3F2FD; border-left: 4px solid #45B7D1; color: #2B2B2B; }

.stCode {
    background-color: #F5F5F5;
    border: 1px solid #D4AF37;
    border-radius: 4px;
    font-family: 'Consolas', monospace;
}

hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #D4AF37, transparent);
    margin: 20px 0;
}

/* ============================================
   8. 响应式断点 - 手机竖屏 (<=480px)
   ============================================ */
@media (max-width: 480px) {
    /* 多列布局强制堆叠 */
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }

    [data-testid="stHorizontalBlock"] > div {
        width: 100% !important;
        min-width: 100% !important;
        margin-bottom: 12px;
    }

    /* Tab 横向滚动 */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto;
        overflow-y: hidden;
        white-space: nowrap;
        display: flex;
        flex-wrap: nowrap;
        -webkit-overflow-scrolling: touch;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 4px;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
        background-color: #D4AF37;
        border-radius: 4px;
    }

    /* 按钮全宽 */
    .stButton > button {
        width: 100% !important;
    }

    /* 排盘代码块缩小字号 + 横向滚动 */
    .stCode code, .stCode pre {
        font-size: 11px !important;
        white-space: pre !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }

    /* 减小主区域两侧留白 */
    .main .block-container {
        padding: 10px;
    }
}

/* ============================================
   9. 响应式断点 - 平板/手机横屏 (481-768px)
   ============================================ */
@media (min-width: 481px) and (max-width: 768px) {
    [data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 320px !important;
    }

    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }

    [data-testid="stHorizontalBlock"] > div {
        width: 100% !important;
        min-width: 100% !important;
    }

    .stCode code, .stCode pre {
        font-size: 13px !important;
    }
}

/* ============================================
   10. 响应式断点 - 桌面端 (>=769px)
   ============================================ */
@media (min-width: 769px) and (max-width: 1024px) {
    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 360px !important;
    }
}

@media (min-width: 1025px) {
    [data-testid="stSidebar"] {
        min-width: 320px !important;
        max-width: 400px !important;
    }
}
</style>
"""

st.markdown(zhouyi_css, unsafe_allow_html=True)

# localStorage 恢复必须在任何 UI 渲染之前，否则 st.stop() 会阻止排盘内容
_ls_init()

# ============================================================
# 爻象选项（通俗化文案）
# ============================================================
YAO_OPTIONS = {
    "三枚正面": {"code": "6", "type": "老阴", "symbol": "⚋ ×", "desc": "三枚都是正面，阴爻发动（变爻）"},
    "两正一反": {"code": "7", "type": "少阳", "symbol": "⚊",   "desc": "两枚正面一枚反面，阳爻不变（静爻）"},
    "两反一正": {"code": "8", "type": "少阴", "symbol": "⚋",   "desc": "两枚反面一枚正面，阴爻不变（静爻）"},
    "三枚反面": {"code": "9", "type": "老阳", "symbol": "⚊ ○", "desc": "三枚都是反面，阳爻发动（变爻）"},
}


# ============================================================
# 状态初始化
# ============================================================
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


# ============================================================
# 排盘生成
# ============================================================
def generate_pan_result(y, m, d, h, minute, yao_code):
    return ichingshifa.Iching().display_pan_m(y, m, d, h, minute, yao_code)


# ============================================================
# 重置摇卦
# ============================================================
def reset_cast():
    st.session_state.cast_data = None
    st.session_state.ai_reading = ""
    st.session_state.page = "home"
    st.rerun()


# ============================================================
# 爻选择器
# ============================================================
def render_yao_selector():
    st.subheader("记录六次摇卦结果")
    st.caption("从第一次（初爻）开始，依次向上填写到第六次（上爻）。")

    keys = [
        ("第一次（初爻）", "yao_1"),
        ("第二次（二爻）", "yao_2"),
        ("第三次（三爻）", "yao_3"),
        ("第四次（四爻）", "yao_4"),
        ("第五次（五爻）", "yao_5"),
        ("第六次（上爻）", "yao_6"),
    ]

    values = []
    for label, key in keys:
        choice = st.selectbox(
            label,
            options=list(YAO_OPTIONS.keys()),
            key=key,
            format_func=lambda name: f"{YAO_OPTIONS[name]['symbol']}  {name} — {YAO_OPTIONS[name]['desc']}",
        )
        values.append(choice)

    return "".join(YAO_OPTIONS[name]["code"] for name in values)


# ============================================================
# 首页：摇卦界面
# ============================================================
def render_home_page():
    st.title("坚六爻")

    # 日期时间选择
    col_date, col_time = st.columns(2)
    with col_date:
        pp_date = st.date_input("排盘日期", pdlm.now(tz="Asia/Shanghai").date())
    with col_time:
        pp_time = st.time_input("排盘时间", value=st.session_state.pp_time)
        st.session_state.pp_time = pp_time

    st.markdown("---")

    # 爻选择
    yao_code = render_yao_selector()

    # 摇卦说明
    with st.expander("如何摇卦？", expanded=False):
        st.markdown("""
        **准备工具**：3枚硬币（一面有字/数字为正面，一面无字/图案为反面）

        **步骤**：
        1. 静心凝神，手握3枚硬币，心中默念所问之事
        2. 抛掷硬币，统计正面和反面数量
        3. 重复6次，从初爻到上爻依次记录结果

        | 结果 | 通俗叫法 | 含义 |
        |------|---------|------|
        | 三枚全是正面 | 三枚正面 | 阴爻发动（变爻） |
        | 两枚正一枚反 | 两正一反 | 阳爻不变（静爻） |
        | 两枚反一枚正 | 两反一正 | 阴爻不变（静爻） |
        | 三枚全是反面 | 三枚反面 | 阳爻发动（变爻） |
        """)

    st.markdown("---")

    # 问题输入
    question = st.text_area(
        "所问何事",
        key="question",
        placeholder="例如：近期事业发展如何？这次合作是否顺利？",
        height=100,
    )

    # 排盘按钮
    if st.button("生成排盘", type="primary", use_container_width=True):
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


# ============================================================
# AI 解读 Tab 内容
# ============================================================
def render_ai_tab(pan_result: str):
    question = st.session_state.get("cast_data", {}).get("question", "")

    question_input = st.text_area(
        "所问何事",
        value=question,
        key="result_question",
        height=100,
    )

    col_gen, col_cfg = st.columns([3, 1])
    with col_gen:
        generate = st.button("生成AI解读", type="primary", use_container_width=True)
    with col_cfg:
        if st.button("AI配置", use_container_width=True):
            st.session_state.previous_page = "result"
            st.session_state.page = "ai_settings"
            st.rerun()

    if generate:
        settings = st.session_state.get("ai_settings", {})
        if not settings.get("api_key", "").strip():
            st.error("请先配置 API Key（点击上方 AI配置 按钮）")
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
                st.success("解读完成")
            except ValueError as ve:
                st.error(f"{ve}")
            except Exception as e:
                st.error(f"AI解读失败: {e}")

    if st.session_state.get("ai_reading"):
        st.markdown("---")
        st.markdown(st.session_state.ai_reading)

        col_copy, col_download = st.columns(2)
        with col_copy:
            if st.button("复制结果", key="copy_result", use_container_width=True):
                st.code(st.session_state.ai_reading, language="text")
        with col_download:
            st.download_button(
                label="下载解读",
                data=st.session_state.ai_reading,
                file_name=f"周易解读_{pdlm.now(tz='Asia/Shanghai').format('YYYY-MM-DD_HH-mm-ss')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
    else:
        st.info("输入问题后点击上方按钮生成 AI 解读")


# ============================================================
# 结果页：排盘 + Tab
# ============================================================
def render_result_page():
    cast_data = st.session_state.get("cast_data")
    if not cast_data:
        reset_cast()
        return

    # 顶部导航
    col_title, col_back, col_cfg = st.columns([2, 1, 1])
    with col_title:
        st.title("排盘结果")
    with col_back:
        if st.button("重新摇卦", use_container_width=True):
            reset_cast()
    with col_cfg:
        if st.button("AI配置", use_container_width=True):
            st.session_state.previous_page = "result"
            st.session_state.page = "ai_settings"
            st.rerun()

    pan_tab, ai_tab, book_tab, example_tab, log_tab = st.tabs(
        ["排盘", "AI解读", "占诀", "古占例", "日志"]
    )

    with pan_tab:
        st.code(cast_data["pan_result"])

    with ai_tab:
        render_ai_tab(cast_data["pan_result"])

    with book_tab:
        st.markdown(get_file_content_as_string("text.md"))

    with example_tab:
        st.markdown(get_file_content_as_string("example.md"))

    with log_tab:
        st.markdown(get_file_content_as_string("update.md"))


# ============================================================
# AI 配置页
# ============================================================
def render_ai_settings_page():
    st.title("AI 配置")

    ai_module = st.session_state.ai_module
    current_settings = st.session_state.ai_settings

    new_base_url = st.text_input(
        "Base URL",
        value=current_settings.get("base_url", ""),
        placeholder="自定义API地址（可选，留空使用OpenAI默认）",
    )

    new_model = st.text_input(
        "模型名称",
        value=current_settings.get("model", "gpt-3.5-turbo"),
    )

    new_api_key = st.text_input(
        "API Key",
        value=current_settings.get("api_key", ""),
        type="password",
        placeholder="请输入API密钥",
    )

    new_temperature = st.slider(
        "创造性（温度）",
        min_value=0.0,
        max_value=1.0,
        value=float(current_settings.get("temperature", 0.7)),
        step=0.1,
    )

    st.markdown("---")
    new_system_prompt = st.text_area(
        "系统提示词",
        value=current_settings.get("system_prompt", ""),
        height=200,
    )

    new_user_prompt = st.text_area(
        "用户提示词模板",
        value=current_settings.get("user_prompt_template", ""),
        height=300,
        help="使用 {pan_result} 和 {question} 作为占位符",
    )

    st.markdown("---")
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        new_max_tokens_val = st.number_input(
            "最大Token数",
            value=current_settings.get("max_tokens") or 0,
            min_value=0,
            help="0表示不限制",
        )
    with col_opt2:
        new_timeout = st.number_input(
            "请求超时（秒）",
            value=float(current_settings.get("timeout", 60.0)),
            min_value=1.0,
            max_value=300.0,
        )
    with col_opt3:
        new_max_retries = st.number_input(
            "最大重试次数",
            value=int(current_settings.get("max_retries", 3)),
            min_value=0,
            max_value=10,
        )

    col_save, col_reset, col_back = st.columns(3)
    with col_save:
        if st.button("保存配置", type="primary", use_container_width=True):
            new_settings = {
                "base_url": str(new_base_url).strip(),
                "api_key": str(new_api_key).strip(),
                "model": str(new_model).strip() or "gpt-3.5-turbo",
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
            else:
                st.error("配置保存失败")

    with col_reset:
        if st.button("重置默认", use_container_width=True):
            if ai_module.save_settings(ai_module.default_settings):
                st.session_state.ai_settings = ai_module.default_settings.copy()
                _ls_save(ai_module.default_settings)
                st.success("已重置为默认配置")
                st.rerun()
            else:
                st.error("重置失败")

    with col_back:
        if st.button("返回", use_container_width=True):
            st.session_state.page = st.session_state.get("previous_page", "home")
            st.rerun()

    current_api_key = current_settings.get("api_key", "").strip()
    if current_api_key:
        st.success("API Key 已配置")
    else:
        st.warning("请配置 API Key 以使用 AI 解读功能")


# ============================================================
# 主路由
# ============================================================
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


