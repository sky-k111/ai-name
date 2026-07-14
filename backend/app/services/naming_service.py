"""取名服务 — prompt 拼装与结果解析."""
import json
import logging
import re
import uuid

from app.utils.deepseek import DeepSeekClient, DeepSeekError

logger = logging.getLogger(__name__)
MAX_PROMPT_CHARS = 12_000

# ── System Prompt ─────────────────────────────────────────────
SYSTEM_PROMPT = """\
你是一位专业的中国取名大师，精通五行八字、诗词典故、音律美学。
你的任务是根据用户提供的信息，生成高质量的中文名字建议。

要求：
1. 生成 5 个名字备选
2. 名字字数灵活，根据用户要求来（常规2-3字，用户可要求4字或更多）。姓氏+名字的总字数以用户期望为准
3. 名字要好听上口、有文化内涵、避免生僻字
4. 每个名字提供：寓意解释、五行属性、文化出处、逐字释义和典故语境
5. 典故必须真实可核验；不确定原句时将 source_quote 留空，不得杜撰

你必须严格按以下 JSON 格式返回，不要包含任何其他文字：
{
  "names": [
    {
      "full_name": "姓名",
      "meaning": "寓意解释",
      "wuxing": "五行属性",
      "source": "文化出处",
      "source_quote": "典故原句（40字以内，不确定则留空）",
      "source_context": "典故原句的语境，以及它与名字的关系（80字以内）",
      "character_meaning": "逐字释义，例如：知：求知明辨；远：志向高远",
      "naming_story": "将字义、出处和气质串联成一段命名故事（80字以内）",
      "usage_advice": "读写、称呼或重名方面的简短使用建议（40字以内）"
    }
  ]
}

【重要警告】JSON 值内部绝对禁止使用英文双引号 "，这会破坏 JSON 格式。
如需引用诗文典籍，请使用书名号《》或单引号 ' 代替，例如：
正确：source 字段写「出自《诗经》高山仰止」
错误：source 字段写「出自"诗经"高山仰止」
确保返回的是合法 JSON，逗号、花括号、方括号一个都不能错。"""

# ── Service ────────────────────────────────────────────────────


class NamingService:
    """取名业务逻辑."""

    def __init__(self):
        self._client = DeepSeekClient()

    @staticmethod
    def _enforce_prompt_budget(prompt: str) -> str:
        if len(prompt) > MAX_PROMPT_CHARS:
            raise DeepSeekError("输入内容过长，请缩短后重试", status_code=413)
        return prompt

    def _build_generate_prompt(self, request: dict) -> str:
        """拼装首次生成 prompt."""
        gender_text = "男" if request.get("gender") == "male" else "女"
        parts = [
            f"- 姓氏：{request.get('surname', '')}",
            f"- 性别：{gender_text}",
        ]
        if request.get("birthday"):
            parts.append(f"- 出生日期：{request['birthday']}")
        if request.get("birth_time"):
            parts.append(f"- 出生时辰：{request['birth_time']}")
        if request.get("style"):
            parts.append(f"- 期望风格：{request['style']}")
        if request.get("expectations"):
            parts.append(f"- 其他期望：{request['expectations']}")

        user_text = "请为以下信息生成名字：\n" + "\n".join(parts)
        return self._enforce_prompt_budget(user_text)

    def _build_refine_prompt(
        self,
        original_request: dict,
        history: list[dict],
        feedback: str,
    ) -> str:
        """拼装微调 prompt."""
        parts = []

        # 原始需求
        orig_text = self._build_generate_prompt(original_request)
        parts.append(f"原始需求：\n{orig_text}")

        # 对话历史
        if history:
            parts.append("\n之前的调整过程：")
            for msg in history:
                role = "用户" if msg["role"] == "user" else "AI"
                parts.append(f"{role}：{msg['content']}")

        # 新反馈
        parts.append(f"\n用户的新反馈：{feedback}")
        parts.append("\n请根据以上反馈重新生成名字，保持 JSON 格式。")

        return self._enforce_prompt_budget("\n".join(parts))

    def _clean_json(self, raw: str) -> str:
        """清理 LLM 常见 JSON 错误."""
        # 替换中文弯引号为直角引号（避免破坏 JSON 字符串边界）
        raw = raw.replace("“", "「")  # " → 「
        raw = raw.replace("”", "」")  # " → 」
        # 替换中文单弯引号
        raw = raw.replace("‘", "『")  # ' → 『
        raw = raw.replace("’", "』")  # ' → 』
        return raw

    def _parse_response(self, raw: str) -> list[dict]:
        """解析 DeepSeek 返回的 JSON."""
        raw = self._clean_json(raw)
        logger.debug("DeepSeek raw response (%d chars): %s", len(raw), raw[:300])

        # 尝试直接解析
        try:
            data = json.loads(raw)
            return data.get("names", [])
        except json.JSONDecodeError as e:
            logger.debug("direct parse failed: %s", e)

        # 尝试从 markdown code block 中提取
        match = re.search(r"```(?:json)?\s*\n?(.*?)```", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return data.get("names", [])
            except json.JSONDecodeError:
                pass

        # 尝试找 JSON：从第一个 { 到最后一个 }
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(raw[start:end + 1])
                return data.get("names", [])
            except json.JSONDecodeError:
                pass

        # 最后兜底：正则匹配
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return data.get("names", [])
            except json.JSONDecodeError:
                pass

        raise DeepSeekError("无法解析 AI 返回的名字数据，请重试", status_code=502)

    async def generate(self, request: dict, api_key: str | None = None) -> dict:
        """首次生成名字."""
        user_prompt = self._build_generate_prompt(request)
        raw = await self._client.chat(SYSTEM_PROMPT, user_prompt, api_key)
        names = self._parse_response(raw)
        return {
            "conversation_id": str(uuid.uuid4()),
            "names": names,
        }

    async def analyze(self, full_name: str, gender: str = "male", api_key: str | None = None) -> dict:
        """分析已有名字."""
        gender_text = "男" if gender == "male" else "女"
        user_prompt = f"""请分析以下名字：
- 名字：{full_name}
- 性别：{gender_text}

请从以下维度分析这个名字（JSON格式）：
{{
  "score": 85,
  "summary": "综合评价（50字内）",
  "meaning": "名字寓意",
  "wuxing": "五行属性",
  "source": "文化出处",
  "pros": ["优点1", "优点2"],
  "cons": ["不足1"]
}}"""

        analyze_system = """你是一位专业的中国取名大师。请客观分析用户提供的名字。
从寓意、音韵、五行、文化内涵等角度评价，给出0-100的评分。
必须严格按 JSON 格式返回，不要包含任何其他文字。"""

        raw = await self._client.chat(analyze_system, user_prompt, api_key)
        try:
            data = json.loads(self._clean_json(raw))
            return data
        except json.JSONDecodeError:
            # 降级
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1:
                return json.loads(raw[start:end + 1])
            raise DeepSeekError("无法解析分析结果", status_code=502)

    async def compare(self, names: list[str], gender: str = "male", api_key: str | None = None) -> dict:
        """对比多个名字."""
        gender_text = "男" if gender == "male" else "女"
        names_text = "、".join(names)
        if any(len(name) > 20 for name in names) or len(names_text) > MAX_PROMPT_CHARS:
            raise DeepSeekError("输入内容过长，请缩短后重试", status_code=413)
        user_prompt = f"""请横向对比以下 {len(names)} 个名字：
名字：{names_text}
性别：{gender_text}

请从寓意、音韵、字形、五行四个维度打分（每项1-10分），给出总分（0-100），并排名。

必须严格按 JSON 格式返回：
{{"rankings":[{{"rank":1,"full_name":"名字","score":92,"meaning_score":9,"sound_score":9,"wuxing_score":8,"char_score":8,"summary":"综合评价"}}]}}"""

        compare_system = """你是一位专业的中国取名大师。请客观对比多个名字，从多维度评分排名。必须严格按 JSON 格式返回。"""
        raw = await self._client.chat(compare_system, user_prompt, api_key)
        return self._parse_compare(raw)

    async def premium(self, request: dict, api_key: str | None = None) -> dict:
        """精品取名——比普通取名多：八字详批、音律/字形评分、重名概率、名字故事."""
        sys_prompt = """你是一位专业的中国取名大师，精通八字命理、音律美学、汉字字形分析。

你必须为每个名字提供比普通取名更丰富的分析，严格按以下 JSON 返回：
{
  "names": [
    {
      "full_name": "姓名",
      "meaning": "寓意解释（100字，比普通版详细一倍）",
      "wuxing": "五行属性及分析",
      "source": "文化出处",
      "source_quote": "典故原句（40字以内，不确定则留空）",
      "source_context": "典故语境与名字关联（100字）",
      "character_meaning": "逐字释义",
      "naming_story": "完整命名故事（120字）",
      "usage_advice": "读写、称呼和使用建议（60字）",
      "bazi": "结合出生信息的八字分析（80字）",
      "sound_analysis": "音律分析：声调组合、平仄、读音响亮度（60字）",
      "char_analysis": "字形分析：笔画数、结构、书写美感（60字）",
      "popularity": "重名概率低/中/高"
    }
  ]
}"""

        user_prompt = self._enforce_prompt_budget(self._build_generate_prompt(request) + "\n请进行精品深度分析，每个名字提供完整八字、音律、字形、重名分析和命名故事。")
        raw = await self._client.chat(sys_prompt, user_prompt, api_key)
        names = self._parse_response(raw)
        return {"names": names, "is_premium": True}

    def _parse_compare(self, raw: str) -> dict:
        cleaned = self._clean_json(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                return json.loads(cleaned[start:end + 1])
            raise DeepSeekError("无法解析对比结果", status_code=502)

    async def refine(
        self,
        original_request: dict,
        history: list[dict],
        feedback: str,
        api_key: str | None = None,
    ) -> dict:
        """根据反馈微调名字."""
        user_prompt = self._build_refine_prompt(original_request, history, feedback)
        raw = await self._client.chat(SYSTEM_PROMPT, user_prompt, api_key)
        names = self._parse_response(raw)
        return {"names": names}
