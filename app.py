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

# 注入中国周易风格的CSS样式
zhouyi_css = """
<style>
/* 全局背景 - 宣纸色 */
.main .block-container {
    background-color: #F7F3E8;
    color: #2B2B2B;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 侧边栏样式 */
.css-1d391kg {
    background: linear-gradient(135deg, #EFEBE2 0%, #E8DDD0 100%);
    border-right: 3px solid #D4AF37;
    padding: 20px;
}

.css-1d391kg .stSelectbox > div > div {
    background-color: #FFFFFF;
    border: 2px solid #D4AF37;
    border-radius: 4px;
    color: #2B2B2B;
}

.css-1d391kg .stTextInput > div > div > input,
.css-1d391kg .stNumberInput > div > div > input {
    background-color: #FFFFFF;
    border: 2px solid #D4AF37;
    border-radius: 4px;
    color: #2B2B2B;
    padding: 8px 12px;
}

/* 主输入框样式 */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: #FFFFFF;
    border: 2px solid #D4AF37;
    border-radius: 6px;
    color: #2B2B2B;
    font-family: 'SimSun', '宋体', serif;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div:focus-within {
    border-color: #9E2A2B;
    box-shadow: 0 0 0 2px rgba(158, 42, 43, 0.2);
}

/* 按钮样式 - 朱砂红 */
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
}

.stButton > button:hover {
    background: linear-gradient(135deg, #B83640 0%, #9E2A2B 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

/* 主按钮（primary）样式 - 琉璃金 */
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

/* Tab标签页样式 */
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
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #9E2A2B 0%, #B83640 100%);
    color: #FFFFFF;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Expander样式 */
.streamlit-expanderHeader {
    background-color: #EFEBE2;
    border-radius: 6px;
    border: 1px solid #D4AF37;
    font-family: 'SimSun', '宋体', serif;
    font-weight: bold;
}

.streamlit-expanderContent {
    background-color: #FFFFFF;
    border-radius: 0 0 6px 6px;
    border: 1px solid #D4AF37;
    border-top: none;
}

/* 滑块样式 */
.stSlider > div > div > div {
    background: linear-gradient(90deg, #D4AF37 0%, #9E2A2B 100%);
}

/* 标题样式 */
h1, h2, h3, h4, h5, h6 {
    color: #2B2B2B;
    font-family: 'SimSun', '宋体', serif;
    font-weight: bold;
}

/* 侧边栏宽度自适应 */
@media (max-width: 768px) {
    .css-1d391kg {
        min-width: 280px !important;
        max-width: 320px !important;
    }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .css-1d391kg {
        min-width: 300px !important;
        max-width: 360px !important;
    }
}

@media (min-width: 1025px) {
    .css-1d391kg {
        min-width: 320px !important;
        max-width: 400px !important;
    }
}

/* 成功/警告/错误消息样式 */
.stSuccess {
    background-color: #E8F5E8;
    border-left: 4px solid #4CAF50;
    color: #2B2B2B;
}

.stWarning {
    background-color: #FFF3E0;
    border-left: 4px solid #D4AF37;
    color: #2B2B2B;
}

.stError {
    background-color: #FFEBEE;
    border-left: 4px solid #9E2A2B;
    color: #2B2B2B;
}

.stInfo {
    background-color: #E3F2FD;
    border-left: 4px solid #45B7D1;
    color: #2B2B2B;
}

/* 代码块样式 */
.stCode {
    background-color: #F5F5F5;
    border: 1px solid #D4AF37;
    border-radius: 4px;
    font-family: 'Consolas', monospace;
}

/* 分割线样式 */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #D4AF37, transparent);
    margin: 20px 0;
}
</style>
"""

st.markdown(zhouyi_css, unsafe_allow_html=True)
pan,booktext,oexample,update,links = st.tabs([' 🧮排盘 ',  ' 🚀占诀 ', ' 📜古占例 ', '🆕日志', ' 🔗连结 '])

with st.sidebar:
    pp_date=st.date_input("日期",pdlm.now(tz='Asia/Shanghai').date())
   

    # 设置时间初始值
    if 'pp_time' not in st.session_state:
        st.session_state.pp_time = pdlm.now(tz='Asia/Shanghai').time()

# 使用储存的时间初始值
    pp_time = st.time_input("时间", value=st.session_state.pp_time)
    st.session_state.pp_time = pp_time
    p = str(pp_date).split("-")
    pp = str(pp_time).split(":")
    y = int(p[0])
    m = int(p[1])
    d = int(p[2])
    h = int(pp[0])
    min = int(pp[1])
    st.write("")
    st.write("手动起爻︰(初爻由下而上)")

    # 正反爻定义说明
    st.markdown("**📖 正反爻定义**")
    st.markdown("""
    <div style="background-color: #F0F8FF; padding: 10px; border-radius: 5px; border-left: 4px solid #45B7D1; margin-bottom: 15px;">
    <strong>正爻</strong>：铜钱有汉字（或数字）的一面朝上<br>
    <strong>反爻</strong>：铜钱无字（或硬币菊花、国徽图案）的一面朝上
    </div>
    """, unsafe_allow_html=True)

    # 创建爻的显示映射（带颜色和正反数量）
    yao_options = {
        "老阴 (3正0反)": {
            "symbol": "⚋ ×",
            "color": "#FF6B6B",
            "description": "3枚铜钱正面朝上"
        },
        "少阴 (1正2反)": {
            "symbol": "⚋",
            "color": "#4ECDC4",
            "description": "1枚铜钱正面朝上，2枚反面朝上"
        },
        "少阳 (2正1反)": {
            "symbol": "⚊",
            "color": "#45B7D1",
            "description": "2枚铜钱正面朝上，1枚反面朝上"
        },
        "老阳 (0正3反)": {
            "symbol": "⚊ ○",
            "color": "#FFA07A",
            "description": "3枚铜钱反面朝上"
        }
    }

    def render_manual_yao_row(label: str, key: str) -> str:
        """渲染单行的手动爻选择，下拉框内显示爻象符号和正反数量。"""
        col_label, col_select = st.columns([2, 4])
        with col_label:
            st.write(f'**{label}**')
        with col_select:
            choice_key = st.selectbox(
                label=f'{label}选择',
                options=list(yao_options.keys()),
                key=key,
                label_visibility="collapsed",
                format_func=lambda x: f"{yao_options[x]['symbol']} {x}"
            )
        return choice_key

    option_sixth = render_manual_yao_row('上爻', 'option_sixth')
    option_fifth = render_manual_yao_row('五爻', 'option_fifth')
    option_forth = render_manual_yao_row('四爻', 'option_forth')
    option_third = render_manual_yao_row('三爻', 'option_third')
    option_second = render_manual_yao_row('二爻', 'option_second')
    option_first = render_manual_yao_row('初爻', 'option_first')
    # 从选择中提取爻象类型
    def extract_yao_type(choice_key: str) -> str:
        """从选择键中提取爻象类型"""
        if "老阴" in choice_key:
            return "老阴"
        elif "少阴" in choice_key:
            return "少阴"
        elif "少阳" in choice_key:
            return "少阳"
        elif "老阳" in choice_key:
            return "老阳"
        else:
            return "少阴"  # 默认值

    yaodict = {"老阴": "6", '少阳':"7", "老阳": "9", '少阴':"8" }
    combine = "".join([yaodict.get(extract_yao_type(i), "") for i in [option_first, option_second,option_third,option_forth,option_fifth,option_sixth]])
    manual = st.button('🎯 手动排盘')

    # 摇卦方法说明
    st.markdown("---")
    st.markdown("**🎲 摇卦方法详解**")

    with st.expander("📖 如何正确摇卦？", expanded=False):
        st.markdown("""
        ### 准备工具
        - **6枚铜钱**（或硬币，一面有字/数字，一面无字/图案）
        - **安静的环境**和专注的心态

        ### 摇卦步骤
        1. **静心凝神**：手握6枚铜钱，心中默念所问之事
        2. **第一次摇卦**（对应**初爻**）：抛出铜钱，统计正面数量
        3. **继续摇卦**：依次完成第二、三、四、五、六次摇卦
        4. **记录结果**：根据每次摇卦的正面数量确定爻象

        ### 爻象判定规则
        | 正面数量 | 反面数量 | 爻象 | 符号 | 含义 |
        |---------|---------|------|------|------|
        | 3枚 | 0枚 | 老阴 | ⚋ × | 阴中之阴，可能变阳 |
        | 2枚 | 1枚 | 少阳 | ⚊ | 阳爻，静而不变 |
        | 1枚 | 2枚 | 少阴 | ⚋ | 阴爻，静而不变 |
        | 0枚 | 3枚 | 老阳 | ⚊ ○ | 阳中之阳，可能变阴 |

        ### 📌 重要提示
        - **初爻**（第一次摇卦）对应最下面的爻
        - **上爻**（第六次摇卦）对应最上面的爻
        - 老阴、老阳为"动爻"，代表可能的变化
        - 少阴、少阳为"静爻"，代表稳定状态
        """)

    # AI设置区域
    st.write("---")

    # 初始化AI模块
    if "ai_module" not in st.session_state:
        st.session_state.ai_module = AIInterpretationModule()

    # 优先从浏览器 localStorage 恢复，其次读文件
    _ls_init()

    if "ai_settings" not in st.session_state:
        st.session_state.ai_settings = st.session_state.ai_module.load_settings()

    ai_module = st.session_state.ai_module
    current_settings = st.session_state.ai_settings

    with st.expander("🤖 AI解读设置", expanded=False):
        st.markdown("##### 🔧 基本配置")
        new_base_url = st.text_input(
            "Base URL",
            value=current_settings.get("base_url", ""),
            placeholder="自定义API地址（可选）",
            help="留空使用OpenAI默认地址"
        )

        new_model = st.text_input(
            "模型名称",
            value=current_settings.get("model", "gpt-3.5-turbo"),
            placeholder="如: gpt-3.5-turbo"
        )

        st.write("")  # 添加垂直间距

        new_api_key = st.text_input(
            "API Key",
            value=current_settings.get("api_key", ""),
            type="password",
            placeholder="请输入API密钥",
            help="支持OpenAI兼容接口"
        )

        new_temperature = st.slider(
            "创造性 (温度)",
            min_value=0.0,
            max_value=1.0,
            value=float(current_settings.get("temperature", 0.7)),
            step=0.1,
            help="数值越高回答越有创造性"
        )

        st.markdown("---")
        st.markdown("##### ✏️ 提示词配置")
        new_system_prompt = st.text_area(
            "系统提示词",
            value=current_settings.get("system_prompt", ""),
            height=200,
            help="AI助手的角色设定和专业背景"
        )

        new_user_prompt = st.text_area(
            "用户提示词模板",
            value=current_settings.get("user_prompt_template", ""),
            height=300,
            help="使用{pan_result}和{question}作为占位符"
        )

        st.markdown("---")
        st.markdown("##### ⚙️ 高级配置")
        new_max_tokens = st.number_input(
            "最大Token数",
            value=current_settings.get("max_tokens", None),
            min_value=None,
            max_value=None,
            help="留空表示不限制"
        )

        new_timeout = st.number_input(
            "请求超时（秒）",
            value=float(current_settings.get("timeout", 60.0)),
            min_value=1.0,
            max_value=300.0,
            step=1.0
        )

        new_max_retries = st.number_input(
            "最大重试次数",
            value=int(current_settings.get("max_retries", 3)),
            min_value=0,
            max_value=10,
            step=1
        )

        # 操作按钮
        col_save, col_reset, col_export = st.columns(3)
        with col_save:
            if st.button("💾 保存配置", use_container_width=True):
                new_settings = {
                    "base_url": str(new_base_url).strip(),
                    "api_key": str(new_api_key).strip(),
                    "model": str(new_model).strip() or "gpt-3.5-turbo",
                    "temperature": new_temperature,
                    "system_prompt": str(new_system_prompt).strip(),
                    "user_prompt_template": str(new_user_prompt).strip(),
                    "max_tokens": new_max_tokens if new_max_tokens else None,
                    "timeout": new_timeout,
                    "max_retries": new_max_retries
                }
                if ai_module.save_settings(new_settings):
                    st.session_state.ai_settings = new_settings
                    _ls_save(new_settings)
                    st.success("AI配置已保存到浏览器")
                    st.rerun()
                else:
                    st.error("配置保存失败")

        with col_reset:
            if st.button("🔄 重置默认", use_container_width=True):
                if ai_module.save_settings(ai_module.default_settings):
                    st.session_state.ai_settings = ai_module.default_settings.copy()
                    _ls_save(ai_module.default_settings)
                    st.success("已重置为默认配置")
                    st.rerun()
                else:
                    st.error("重置失败")

        with col_export:
            if st.button("📋 导出配置", use_container_width=True):
                config_text = json.dumps(current_settings, ensure_ascii=False, indent=2)
                st.code(config_text)
                st.info("配置已显示，您可以手动复制")

        # 显示当前配置状态
        current_api_key = current_settings.get("api_key", "").strip()
        if current_api_key:
            st.success("✅ API Key已配置")
        else:
            st.warning("⚠️ 请配置API Key以使用AI解读功能")

with links:
    st.header('连接')
    st.markdown(get_file_content_as_string1("update.md"), unsafe_allow_html=True)

with update:
    st.header('日志')
    st.markdown(get_file_content_as_string("update.md"))

with booktext:
    st.header('占诀')
    st.markdown(get_file_content_as_string("text.md"))
 
with oexample:
    st.header('古占例')
    st.markdown(get_file_content_as_string("example.md"))

with pan:
    st.header('坚六爻')

    # 创建两列布局：左列排盘，右列AI解读
    col_left, col_right = st.columns([2, 1])

    # 初始化session state
    if "latest_pan_result" not in st.session_state:
        st.session_state.latest_pan_result = ""
    if "ai_reading" not in st.session_state:
        st.session_state.ai_reading = ""
    if "current_yao_list" not in st.session_state:
        st.session_state.current_yao_list = []

    # 左列：排盘显示
    with col_left:
        st.subheader("📊 排盘结果")

        # 生成排盘结果
        try:
            pan_result_obj = ichingshifa.Iching().display_pan(y,m,d,h,min)
            qigua_result = ichingshifa.Iching().qigua_time(y,m,d,h,min)
            dayan_method = qigua_result.get("大衍筮法", [])
            combine1 = dayan_method[0] if dayan_method else "777777"  # 默认值
            pan_m_result = ichingshifa.Iching().display_pan_m(y,m,d,h,min,combine1)

            # 获取当前爻列表
            if manual:
                yao_list = [extract_yao_type(option) for option in [option_first, option_second, option_third, option_forth, option_fifth, option_sixth]]
            else:
                yao_numbers = list(combine1)
                yaodict_reverse = {"6": "老阴", "8": "少阴", "7": "少阳", "9": "老阳"}
                yao_list = [yaodict_reverse.get(num, "少阴") for num in yao_numbers]

            st.session_state.current_yao_list = yao_list

            # 确定显示内容
            display_result = pan_result_obj
            if manual:
                try:
                    display_result = pan_m_result
                except (ValueError, UnboundLocalError):
                    pass

            # 保存排盘结果供 AI 使用
            st.session_state.latest_pan_result = str(display_result)

            # 直接显示
            st.code(display_result)

        except Exception as e:
            st.error(f"排盘生成失败: {e}")
            st.session_state.latest_pan_result = ""
            st.session_state.current_yao_list = []

    # 右列：AI解读
    with col_right:
        st.subheader("🤖 AI解读")

        # 上方区域：问题输入
        st.markdown("##### 所问何事？")
        user_question = st.text_area(
            "请输入您要询问的问题",
            key="user_question",
            placeholder="例如：事业发展如何？感情走向怎样？",
            height=100,
            help="请详细描述您的问题，以便AI给出更精准的解读"
        )

        # 生成解读按钮
        generate_button = st.button(
            "🔮 生成AI解读",
            use_container_width=True,
            type="primary"
        )

        st.markdown("---")

        # 下方区域：解读结果显示
        st.markdown("##### LLM解读内容")
        ai_result_container = st.container()

        # 生成解读的逻辑
        if generate_button:
            # 验证输入
            if not st.session_state.latest_pan_result.strip():
                st.warning("请先生成排盘结果")
            elif not user_question.strip():
                st.warning("请输入您要询问的问题")
            else:
                # 检查API配置
                current_settings = st.session_state.get("ai_settings", {})
                if not current_settings.get("api_key", "").strip():
                    st.error("请先在侧边栏配置API Key")
                else:
                    # 显示加载状态
                    with st.spinner("🤖 AI正在解读中，请稍候..."):
                        try:
                            # 使用AI模块调用API
                            ai_response = ai_module.call_llm_api(
                                question=user_question.strip(),
                                pan_result=st.session_state.latest_pan_result,
                                settings=current_settings
                            )

                            # 保存解读结果
                            st.session_state.ai_reading = ai_response
                            st.success("✨ 解读完成！")

                        except ValueError as ve:
                            st.error(f"⚠️ {ve}")
                        except Exception as e:
                            st.error(f"❌ AI解读失败: {e}")

        # 显示解读结果
        with ai_result_container:
            if st.session_state.ai_reading:
                # 使用markdown显示格式化的解读结果
                st.markdown(st.session_state.ai_reading)

                # 添加操作按钮
                col_copy, col_download, col_refresh = st.columns(3)
                with col_copy:
                    if st.button("📋 复制到剪贴板", key="copy_result", use_container_width=True):
                        st.code(st.session_state.ai_reading, language="text")
                        st.info("解读结果已显示在上方代码框中，您可以点击复制按钮复制内容")

                with col_download:
                    # 提供下载功能
                    st.download_button(
                        label="💾 下载解读",
                        data=st.session_state.ai_reading,
                        file_name=f"周易解读_{pdlm.now(tz='Asia/Shanghai').format('YYYY-MM-DD_HH-mm-ss')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                with col_refresh:
                    if st.button("🔄 重新解读", key="refresh_result", use_container_width=True):
                        st.session_state.ai_reading = ""
                        st.rerun()
            else:
                st.info("💡 请先完成排盘并输入问题，然后点击'生成AI解读'")

        # 显示提示词信息（调试用）
        if st.checkbox("🔧 显示调试信息"):
            with st.expander("当前配置"):
                st.json(current_settings)


