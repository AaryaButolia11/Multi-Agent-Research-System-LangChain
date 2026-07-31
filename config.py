"""
Central configuration: which models each role uses, and per-model pricing so the
metrics layer can turn token counts into real dollar figures.

Prices are USD per 1,000,000 tokens. Verify against https://groq.com/pricing —
they change. (Llama 3.3 70B Versatile was $0.59 in / $0.79 out as of mid-2026.)
"""

WRITER_MODEL = "llama-3.3-70b-versatile"
CRITIC_MODEL = "llama-3.3-70b-versatile"
JUDGE_MODEL = "llama-3.3-70b-versatile"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

WRITER_TEMPERATURE = 0.3
CRITIC_TEMPERATURE = 0.0
JUDGE_TEMPERATURE = 0.0

PRICING = {
    # model_name: {input $/1M, output $/1M}
    "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
    "openai/gpt-oss-120b": {"input": 0.15, "output": 0.60},
    "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
}