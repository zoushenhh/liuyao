export interface CastRequest {
  date: string;
  time: string;
  yao_code: string;
  question: string;
}

export interface CastResponse {
  cast_id: string;
  date: string;
  time: string;
  yao_code: string;
  question: string;
  pan_result: string;
}

export interface AISettings {
  base_url: string;
  model: string;
  api_key: string;
  temperature: number;
  system_prompt: string;
  user_prompt_template: string;
  max_tokens: number | null;
  timeout: number;
  max_retries: number;
}

export interface InterpretRequest {
  question: string;
  pan_result: string;
  settings: AISettings;
}

export interface InterpretResponse {
  content: string;
}

export interface ValidateKeyRequest {
  base_url: string;
  api_key: string;
  model: string;
}

export interface ValidateKeyResponse {
  valid: boolean;
  message: string;
}

export interface TextItem {
  name: string;
  title: string;
}

export interface TextContent {
  name: string;
  title: string;
  content: string;
}

const DEFAULT_SYSTEM_PROMPT = `# Role: 资深六爻预测大师

# Profile:
- **背景**: 深研《增删卜易》、《卜筮正宗》、《易林补遗》及《周易本义》等历代易学经典，拥有三十年实战经验，累计解析卦例过万。
- **专长**: 精通纳甲筮法、五行生克、六神取象、世应关系及飞伏神理论。擅长捕捉"动爻"之玄机，断事准确率极高。
- **理念**: 秉持"天行健，君子以自强不息"的精神，拒绝宿命论，主张通过知晓天机来趋吉避凶，指导行动。

# Task:
根据用户提供的【所问之事】和【排盘结果】，运用正宗六爻技法进行综合推演，为用户提供结构化、专业且具有指导意义的解读。`;

const DEFAULT_USER_PROMPT = `# Input Data:
- **所问之事**: {question}
- **排盘结果**:
{pan_result}

# Analysis Framework (Step-by-Step):

请严格按照以下框架进行分析：

1.  **定用神与察旺衰 (核心基础)**:
    - 依据问事性质精准选取**用神**。若用神不上卦，需查**伏神**。
    - 分析用神在**月建**、**日辰**下的旺衰休囚状态，以及是否遭遇月破、日破、旬空或入墓。

2.  **辨世应与审动变 (事态推演)**:
    - 分析**世爻**与**应爻**的生克比和关系。
    - **重点解读动爻**：判定回头生、回头克、进神、退神、反吟、伏吟。

3.  **参六神与观神煞 (细节取象)**:
    - 结合**六神**辅助判断事物的性质、形态和细节特征。

4.  **断应期与给建议 (决策指导)**:
    - 推断吉凶发生的**应期**。
    - 提供**趋吉避凶**的具体策略。

# Output Format:

## 1. 核心断语
> *(一两句话给出吉凶定性和核心结论)*

## 2. 现状与前事验证
*(描述求测者当下的处境、心理状态或已发生的具体情况)*

## 3. 卦理深度解析
- **用神旺衰**: ...
- **世应博弈**: ...
- **动变玄机**: ...
- **六神细节**: ...

## 4. 趋势与应期
- **发展走势**: ...
- **关键应期**: ...

## 5. 决策建议
*(提供3-4条具体、客观的行动指南)*`;

export const DEFAULT_SETTINGS: AISettings = {
  base_url: "",
  model: "gpt-4o-mini",
  api_key: "",
  temperature: 0.7,
  system_prompt: DEFAULT_SYSTEM_PROMPT,
  user_prompt_template: DEFAULT_USER_PROMPT,
  max_tokens: null,
  timeout: 60,
  max_retries: 3,
};

export const YAO_OPTIONS: Record<string, { code: string; type: string; symbol: string; desc: string }> = {
  "三枚正面": { code: "6", type: "老阴", symbol: "⚊", desc: "三枚都是正面，阴爻发动（变爻）" },
  "两正一反": { code: "7", type: "少阳", symbol: "⚈", desc: "两枚正面一枚反面，阳爻不变（静爻）" },
  "两反一正": { code: "8", type: "少阴", symbol: "⚉", desc: "两枚反面一枚正面，阴爻不变（静爻）" },
  "三枚反面": { code: "9", type: "老阳", symbol: "⚋", desc: "三枚都是反面，阳爻发动（变爻）" },
};

export const YAO_LABELS = [
  "第一次（初爻）",
  "第二次（二爻）",
  "第三次（三爻）",
  "第四次（四爻）",
  "第五次（五爻）",
  "第六次（上爻）",
];

export const YAO_NAMES = ["三枚正面", "两正一反", "两反一正", "三枚反面"];
