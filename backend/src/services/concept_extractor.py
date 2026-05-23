"""Concept extraction service using LLM.

Extracts concepts, domains, emotions, and insights from highlights.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Optional

from src.services.llm_provider import LLMProvider, LLMResponse
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ExtractedConcepts:
    """Result of concept extraction from a highlight.

    Attributes:
        concepts: List of extracted concept names.
        domain: Subject domain classification.
        emotion: Emotional tone (agreement,质疑,反对,兴奋).
        user_focus: What the user focused on.
        author_viewpoint: Author's main argument in the highlight.
    """

    concepts: list[str]
    domain: Optional[str]
    emotion: str
    user_focus: Optional[str] = None
    author_viewpoint: Optional[str] = None


class ConceptExtractor:
    """Extracts concepts and metadata from text highlights using LLM.

    Analyzes reading highlights to identify:
    - Core concepts and themes
    - Subject domain
    - Emotional tone
    - User's focus areas
    - Author's viewpoint

    This is a key component for building the knowledge graph.
    """

    # Valid subject domains
    VALID_DOMAINS = {
        "管理学", "心理学", "哲学", "经济学", "物理学",
        "历史", "文学", "社会学", "AI", "计算机科学",
        "教育学", "政治学", "法学", "医学", "艺术",
        "宗教", "自然辩证法", "思维科学", "方法论",
    }

    # Valid emotions
    VALID_EMOTIONS = {
        "agreement",      # 共鸣
        "questioning",    # 质疑
        "objection",      # 反对
        "excitement",     # 兴奋
        "neutral",        # 中性
    }

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        temperature: float = 0.3,
    ) -> None:
        """Initialize concept extractor.

        Args:
            llm_provider: LLM provider for API calls.
            temperature: LLM temperature for extraction (lower = more focused).
        """
        self.llm_provider = llm_provider or LLMProvider()
        self.temperature = temperature
        self.logger = get_logger(self.__class__.__name__)

    def _build_extraction_prompt(self, highlight: str) -> str:
        """Build prompt for concept extraction.

        Args:
            highlight: The highlight text to analyze.

        Returns:
            Formatted prompt string.
        """
        return f"""分析以下阅读高亮内容，提取关键信息。

高亮内容：
"""{highlight}"""

请以JSON格式返回以下信息：
{{
    "concepts": ["概念1", "概念2", ...],  // 提取的核心概念（3-8个）
    "domain": "学科领域",                    // 学科分类
    "emotion": "情绪倾向",                  // agreement/questioning/objection/excitement/neutral
    "user_focus": "用户关注点",             // 用户标记这段的原因
    "author_viewpoint": "作者观点"          // 作者在这一段的主要观点
}}

要求：
- concepts应该反映该段落的核心理念，使用名词或短语
- domain应该对应一个学科领域，如：管理学、心理学、哲学、AI等
- emotion应该准确反映阅读者对该内容的情绪反应
- 只返回一个有效的JSON对象，不要有其他内容
"""

    def _parse_extraction_response(self, response: str) -> ExtractedConcepts:
        """Parse LLM response into ExtractedConcepts.

        Args:
            response: Raw LLM response text.

        Returns:
            Parsed ExtractedConcepts.

        Raises:
            ValueError: If response cannot be parsed.
        """
        # Try to extract JSON from response
        json_str = self._extract_json(response)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse JSON: %s", str(e))
            raise ValueError(f"Invalid JSON response: {e}") from e

        # Extract and validate concepts
        concepts = self._validate_concepts(data.get("concepts", []))
        if not concepts:
            self.logger.warning("No valid concepts found in response")
            concepts = []

        # Extract and validate domain
        domain = self._validate_domain(data.get("domain"))

        # Extract and validate emotion
        emotion = self._validate_emotion(data.get("emotion", "neutral"))

        return ExtractedConcepts(
            concepts=concepts,
            domain=domain,
            emotion=emotion,
            user_focus=data.get("user_focus"),
            author_viewpoint=data.get("author_viewpoint"),
        )

    def _extract_json(self, text: str) -> str:
        """Extract JSON from response text (handles markdown code blocks).

        Args:
            text: Response text that may contain JSON.

        Returns:
            Extracted JSON string.
        """
        # Try direct parse first
        text = text.strip()

        # Remove markdown code block markers
        if text.startswith("```"):
            # Find the JSON content
            lines = text.split("\n")
            # Skip first line (```json or ```)
            if len(lines) > 1:
                text = "\n".join(lines[1:])
            # Remove closing ```
            if text.endswith("```"):
                text = text[:-3]

        # Try to find JSON object in text
        json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if json_match:
            return json_match.group(0)

        return text

    def _validate_concepts(self, concepts: Any) -> list[str]:
        """Validate and clean concept list.

        Args:
            concepts: Raw concepts from LLM response.

        Returns:
            Cleaned and deduplicated concept list.
        """
        if not isinstance(concepts, list):
            return []

        cleaned = []
        seen = set()

        for concept in concepts:
            if not concept or not isinstance(concept, str):
                continue

            # Clean the concept
            concept = concept.strip()
            if not concept:
                continue

            # Normalize to lowercase for deduplication
            normalized = concept.lower()
            if normalized not in seen:
                seen.add(normalized)
                cleaned.append(concept)

        return cleaned

    def _validate_domain(self, domain: Any) -> Optional[str]:
        """Validate domain against known domains.

        Args:
            domain: Raw domain from LLM response.

        Returns:
            Validated domain or None.
        """
        if not domain or not isinstance(domain, str):
            return None

        domain = domain.strip()
        if not domain:
            return None

        # Check if it's a known domain (with partial matching)
        for valid_domain in self.VALID_DOMAINS:
            if valid_domain in domain or domain in valid_domain:
                return valid_domain

        # Return as-is if not matched (could be a new domain)
        return domain

    def _validate_emotion(self, emotion: Any) -> str:
        """Validate and normalize emotion.

        Args:
            emotion: Raw emotion from LLM response.

        Returns:
            Normalized emotion string.
        """
        if not emotion or not isinstance(emotion, str):
            return "neutral"

        emotion = emotion.strip().lower()

        # Map Chinese emotions to English
        emotion_map = {
            "共鸣": "agreement",
            "同意": "agreement",
            "质疑": "questioning",
            "怀疑": "questioning",
            "反对": "objection",
            "否定": "objection",
            "兴奋": "excitement",
            "惊喜": "excitement",
            "中性": "neutral",
        }

        # Check mapped emotions
        if emotion in emotion_map:
            return emotion_map[emotion]

        # Check direct match
        if emotion in self.VALID_EMOTIONS:
            return emotion

        return "neutral"

    def extract(self, highlight: str) -> ExtractedConcepts:
        """Extract concepts from a highlight.

        Args:
            highlight: The highlight text to analyze.

        Returns:
            ExtractedConcepts with all metadata.

        Raises:
            Exception: If LLM call fails.
        """
        self.logger.debug("Extracting concepts from highlight: %s...", highlight[:50])

        # Build prompt
        prompt = self._build_extraction_prompt(highlight)

        # Call LLM
        messages = [{"role": "user", "content": prompt}]
        response = self.llm_provider.chat_completion(
            messages=messages,
            temperature=self.temperature,
        )

        # Parse response
        if not response.content:
            self.logger.warning("Empty response from LLM")
            return ExtractedConcepts(
                concepts=[],
                domain=None,
                emotion="neutral",
            )

        result = self._parse_extraction_response(response.content)

        self.logger.info(
            "Extracted %d concepts from highlight",
            len(result.concepts),
        )

        return result

    def extract_batch(
        self,
        highlights: list[str],
    ) -> list[ExtractedConcepts]:
        """Extract concepts from multiple highlights.

        Args:
            highlights: List of highlight texts.

        Returns:
            List of ExtractedConcepts for each highlight.
        """
        self.logger.info("Batch extracting concepts from %d highlights", len(highlights))

        results = []
        for i, highlight in enumerate(highlights):
            try:
                result = self.extract(highlight)
                results.append(result)
            except Exception as e:
                self.logger.error(
                    "Failed to extract concepts from highlight %d: %s",
                    i,
                    str(e),
                )
                # Add empty result for failed highlight
                results.append(
                    ExtractedConcepts(
                        concepts=[],
                        domain=None,
                        emotion="neutral",
                    )
                )

        return results
