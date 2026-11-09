"""第3回 宿題（発展 a）: 演習の学習支援エージェントを Google ADK で組み立て直す。

指示（INSTRUCTIONS）とツール（search_glossary・get_lecture_summary・演習で作った make_quiz）は app/ のものをそのまま使い、
エージェントを組み立てる部分だけを ADK で書く。app/ のファイルは変えない。

動かし方（リポジトリの直下で）:
    PYTHONPATH=. uv run --with google-adk adk run adk_agent/glossary_agent
"""

from google.adk.agents import Agent

from app import tools
from app.agent import INSTRUCTIONS
from app.config import MODEL

root_agent = Agent(
    model=MODEL,  # 演習と同じ既定モデル（gemini-3.5-flash-lite）。AIE_MODEL で切り替わる点も同じ
    name="glossary_agent",
    description="AIE2026 講座の用語集と各回の要点を引いて答える学習支援エージェント",
    instruction=INSTRUCTIONS,
    # Pydantic AI の agent.tool_plain(...) に当たる。関数を並べるだけで、
    # docstring と型ヒントがツールの説明文と引数スキーマになる点は同じ
    tools=[tools.search_glossary, tools.get_lecture_summary, tools.make_quiz],
)
