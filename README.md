# Python IchingShifa Python 周易 筮法 六爻 卜卦 (stalk divination)

[![Python](https://img.shields.io/pypi/pyversions/ichingshifa)](https://pypi.org/project/ichingshifa/)
[![PIP](https://img.shields.io/pypi/v/ichingshifa)](https://pypi.org/project/ichingshifa/)
[![Downloads](https://img.shields.io/pypi/dm/ichingshifa)](https://pypi.org/project/ichingshifa/)
[![TG Me](https://img.shields.io/badge/chat-on%20telegram-blue)](https://t.me/haizhonggum)
[![TG Channel](https://img.shields.io/badge/chat-on%20telegram-red)](https://t.me/numerology_coding)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)&nbsp;

![alt text](https://upload.wikimedia.org/wikipedia/commons/a/af/French_Polished_Yarrow_stalks_from_LPKaster.jpg "Stalk divination")

"筮"是传统的周易起卦方式。古人以50根蓍草作为占卜工具，名为策，故此法亦称"筹策"占卜。《周易系辞上传》辞曰："大衍之数五十，其用四十有九。分而为二以像两，挂一以像三， 揲之以四以像四时，归奇于扐以像闰，五岁再闰，故再扐而后挂。 天一地二，天三地四，天五地六，天七地八，天九地十。天数五，地数五，五位相得而各有合。天数二十有五，地数三十，凡天地之数五十有五。此所以成变化而行鬼神也。"整个起卦过程是要求得十八个随机数目，当中包括"六次"(即六根爻)的"三变"。


**"Shi"(筮)** or so-called Stalk divination, one of the oldest IChing divination method in the Chinese society, in which the ancient Chinese used 50 sticks of yarrow stalks to do divination or prediction. According to Zhouyi 周易, the number of "Da Yan" (大衍) is 50 while 1 is taken away and 49 sticks of yarrow stalks were used in divination. 49 stalks were seperated into 2 bunches respectively held by both left hand and right hand, and then one stick would be extracted from the right hand, the bunch of stalks held by right hand was divided by four, until the remainder comes, that is called the change (or 'bian'), repeating thrice. The whole process of this divination includes getting 18 random numbers. The value of Line may come after  "Three Changes", that is  (49 stalks - first change - second change - third change) divided by 4, it will be either **6(old yin 老阴)**, **7(young yang 少阳)**, **8(young yin 少阴)**, or **9(old yang 老阳)**.  The BenGua (本卦) is formed when the value of Line is formed from the bottom to the top. If the line with value of either 6 or 9, meaning that line must have a change, like 6(old yin) change to 7(young yang), and 9 (old yang) change to 8 (old yin). Each of the lines has its own meaning or explantion. BianGua (变卦) or ZhiGua (之卦) is also formed after BenGua with value 6 or 9 has been changed. 

## **1. 大衍之数、太一、分二、挂一、揲四、归奇 The number of DaYan**︰

```python
#一变的过程
n=2
stalks_first = 50-1  #把太一拿走
dividers = sorted(random.sample(range(24, stalks_first), n - 1)) #分二
division  = [a - b for a, b in zip(dividers + [stalks_first+10], [10] + dividers)]
guayi = 1 #挂一
right = division[0] - guayi 
left_extract = division[1] % 4  #揲四
if left_extract == 0:
    left_extract = 4
right_extract = right % 4
if right_extract == 0:
    right_extract = 4 #归奇
bian  = left_extract + right_extract + guayi #一变，其余二变倣效此法，如果做for loop 这里的挂一可以拿走，不用加上。
```

## **2. 处理变(动)爻的方法︰The way in handling the change of line(s)(yao(s))**

1. 凡卦六爻皆不变，则占本卦彖辞，而以内卦为贞，外卦为悔，彖辞为卦下之辞。

2. 一爻变，则以本卦变爻辞

3. 二爻变，则以本卦二变爻辞占，仍以上爻为主

4. 三爻变，则占本卦及之卦之彖辞，即以本卦为贞，之卦为悔，前十卦(初爻出现变爻)主贞，后十卦(非初爻出现变爻)主悔

5. 四爻变，则以之卦二不变爻占，仍以下爻为主经，亦无文，今以例推之当如此。

6. 五爻变，则以之卦不变爻占。

7. 六爻变，则干、坤占二用，余卦占之卦彖辞。

_参考自【宋】‧朱熹、蔡元定《易学启蒙》卷下 考变占︰_

1. If the Six lines without any changed lines, the explantion of Gua is based on the general explanation of BenGua. 
2. If the Six lines with one line changed, the explanation is depended on there. 
3. If the Six lines with two lines changed, the upper one is the main explanation. 
4. If the Six lines with three lines changed, the explanation is lied on the BenGua's general explanation if the change line starts from the first line, while the explantion is base on BianGua's general explanation if the change line starts from the second line. 
5. If the Six lines with four lines changed,  the explanation is upon the lower line of BianGua. 
6. If the Six lines with five lines changed,  the explanation is upon the one line without change on BianGua. 
7. If the Six lines with six lines changed, except for QianGua and KunGua with explanation on 用, use the general explanation  
_The above method is advocated by ZhuXi, a Confucian of Song Dynasty_

![alt text](https://github.com/kentang2017/iching_shifa/blob/master/data/results.png?raw=true)

## **3. 纳甲 Najia**
其后汉元帝师从梁人焦延寿的京房开创京氏易学，把筮法加入干支纳甲，后世学者再加以五行、五星、六亲及二十八宿等加以详推。

Later on, an iching expert Jing Fang during the Han Dynasty created a najia method of hexagram interpretation among iching. which correlates their separate lines with elements of the Chinese calendar.


## **4. 安装套件 Installation（含依赖）**

项目依赖（来自 `requirements.txt`，并补充 `numpy`）：
- streamlit, streamlit-aggrid
- pendulum
- sxtwl
- ephem
- cn2an
- bidict
- openai
- eacal
- pytz
- numpy（`ichingshifa/ichingshifa.py` 中需要）

安装步骤（建议虚拟环境）：
```bash
# 创建并启用虚拟环境（示例）
python -m venv .venv
.\\.venv\\Scripts\\activate   # Windows

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install numpy  # 如未随环境自动安装，请单独补充
```

## **5. 快速起卦 Quick Start（含 Streamlit 启动）**

### 5.1 作为库使用（保留原示例）
```
from ichingshifa import ichingshifa #导入周易筮法套件库 Import ichingshifa

ichingshifa.Iching().mget_bookgua_details() #手动起卦，从下而上，适合以蓍草起卦者使用，譬如 "初爻7, 二爻8, 三爻9, 四爻7, 五爻8, 上爻9"，即 ichingshifa.mget_bookgua_details('789789') Manually input each of lines' value, e.g. Iching().mget_bookgua_details('789789')
ichingshifa.Iching().bookgua_details() #显示随机起卦结果 Making divination randomly
ichingshifa.Iching().datetime_bookgua('年', '月', '日', '时') #指定年月日时起卦 make divination with the specific datetime
ichingshifa.Iching().current_bookgua() #按现在的年月日时起卦，此法只有一动爻 make divination with the current datetime
ichingshifa.Iching().decode_gua("787987", "庚寅") #手动起卦，从下而上，起本卦之卦纳甲
ichingshifa.Iching().qigua_now() #返回完整的起卦结果
```

### 5.2 启动 Streamlit 应用

1) 保证当前工作目录为项目根目录（包含 `app.py`、`ai_module.py`、`ichingshifa/`）。

2) 安装依赖（见第4章）。

3) 配置 AI 参数：编辑根目录 `ai_settings.json`，填写 `base_url`、`api_key`、`model` 等。如果您已有 OpenAI API key，也可以设置环境变量：
```bash
export OPENAI_API_KEY=your_api_key_here  # Linux/Mac
set OPENAI_API_KEY=your_api_key_here    # Windows
```

4) 运行应用：
```bash
streamlit run app.py
```

默认浏览器将打开本地地址（通常 http://localhost:8501）。如果在服务器上运行，可以使用：
```bash
streamlit run app.py --server.port 8080 --server.address 0.0.0.0
```

### 5.3 运行注意

- 请在项目根目录执行命令，确保 Python 能找到本地包 `ichingshifa`。
- `ichingshifa/ichingshifa.py` 依赖同目录的 `data.pkl` 数据文件，请勿移动或删除。
- 需要外网访问以调用 OpenAI 兼容接口（如果网络受限，请在 `ai_settings.json` 配置可用的网关/代理）。

## **5.4 示例输出**

```python
print(Iching().display_pan(2023,5,27,16,0))
起卦时间︰2023年5月27日16时0分
农历︰二零二三年四月九日
干支︰癸卯年  丁巳月  乙酉日  甲申时
旬空︰　　　  　　　  午未    午未
月建︰丁巳
日干支长生十二运︰子　　丑　　寅　　卯　　辰　　巳　　午　　未　　申　　酉　　戌　　亥　　
　　　　　　　　　病　　衰　　帝旺　临冠　冠带　沐浴　长生　养　　胎　　绝　　墓　　死　　

　　　　　　　       　 　夬卦　　　　　　　　　　 　　　　　              　革卦                
六神　　   伏神　　       本卦　　　　　　　　　　　           伏神　　  　  之卦
　武 　　　　　　　　 角 兄丁未土 　▅▅　▅▅   　            　　　　　　 虚 官丁未土 应▅▅　▅▅  　
　虎 　　　　　　　　 亢 子丁酉金 世▅▅▅▅▅   　            　　　　　　 危 父丁酉金 　▅▅▅▅▅    
　蛇 　　　　　　　　 氐 妻丁亥水 　▅▅▅▅▅   身            　　　　　　 室 兄丁亥水 世▅▅▅▅▅    
　陈 　　　　　　　　 房 兄甲辰土 　▅▅▅▅▅   　            妻戊午火　　 壁 兄己亥水 　▅▅▅▅▅    
　雀 　　父乙巳火　　 心 官甲寅木 应▅▅▅▅▅ O 　            　　　　　　 奎 官己丑土 　▅▅　▅▅    
　龙 　　　　　　　　 尾 妻甲子水 　▅▅▅▅▅   　            　　　　　　 娄 子己卯木 　▅▅▅▅▅    


【大衍筮法】
求得【夬之革】，动爻有【1】根。主要看【九二】九二：惕号，莫夜有戎，勿恤。

夬卦
【卦辞】︰扬于王庭，孚号，有厉，告自邑，不利即戎，利有攸往。
【彖】︰夬，决也，刚决柔也。健而说，决而和，扬于王庭，柔乘五刚也。孚号有厉，其危乃光也。告自邑，不利即戎，所尚乃穷也。利有攸往，刚长乃终也。
上六：无号，终有凶。
九五：苋陆夬夬，中行无咎。
九四：臀无肤，其行次且。 牵羊悔亡，闻言不信。
九三：壮于頄，有凶。 君子夬夬，独行遇雨，若濡有愠，无咎。
九二：惕号，莫夜有戎，勿恤。
初九：壮于前趾，往不胜为咎。

【断主客胜负】
1.客队下卦为【干金】，主队上卦为【兑金】，主客关系为【比和】。
2.主队世爻为【子丁酉金】，原神持世，费心，客队应爻为【官甲寅木】，泄神持应，有利，主客关系为【我尅】。 
3.动爻在下卦，即客队，变为【离火】，主客关系为【我尅】。 
4.动爻【官甲寅木】，主队世爻【子丁酉金】，关系为【我尅】。 
5.动爻【官甲寅木】，客队应爻【官甲寅木】，关系为【比和】 
6.伏神爻【父乙巳火】，飞神【寅木】在【官甲寅木】，伏神【巳火】，飞伏关系为【我生我生】。 
7.日干下主队世爻临【绝　】，客队应爻临【帝旺】。

```

## **6. 在线使用与部署**

### 6.1 Hugging Face Spaces（推荐）

免费在线版，手机/电脑浏览器直接打开：

**[https://huggingface.co/spaces/zoushenhh/liuyao](https://huggingface.co/spaces/zoushenhh/liuyao)**

- 无需安装，打开即用
- 手机浏览器自动适配
- AI 解读需在侧边栏配置 API Key
- 私有部署，无需梯子

### 6.2 自行部署

参考第 4-5 章，支持 Streamlit Cloud、Hugging Face Spaces 或自建 VPS。关键部署要点：

1. `ichingshifa/data.pkl` 必须部署在同一目录层级
2. 删除 `.gitignore` 中 `.streamlit/` 排除项以包含主题配置
3. 云平台设置 `/data` 目录用于 AI 配置持久化（自动检测）
4. `ai_settings.json` 应加入 `.gitignore`，通过侧边栏输入 API Key

### 6.3 旧版应用

- Streamlit Cloud: https://iching.streamlitapp.com
- Kivy Android APK: https://github.com/kentang2017/iching_shifa/blob/master/kinshifa-0.2-release.apk
