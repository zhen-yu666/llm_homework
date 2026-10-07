"""全局配置：路径、模型、切分与检索参数。

本配置使用阿里云 DashScope 的 OpenAI 兼容接口，调用通义千问 LLM 和
text-embedding-v3 嵌入模型。需要提供 DASHSCOPE_API_KEY：可以设置 shell
环境变量，也可以在项目根目录创建 .env（参考 .env.example，由 python-dotenv 加载）。
"""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 项目根目录（先定义，便于加载根目录下的 .env）
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 加载项目根目录 .env；shell 中已存在的环境变量优先（override 默认 False）
load_dotenv(PROJECT_ROOT / ".env")


def _configure_chinese_font() -> None:
    """选择系统已安装的中文字体，避免缺少 SimHei 时图表中文变方框。"""
    from matplotlib import font_manager

    preferred = [
        "SimHei",             # Windows / 已安装该字体的环境
        "Noto Sans CJK SC",   # Ubuntu: sudo apt install fonts-noto-cjk
        "WenQuanYi Zen Hei",  # Ubuntu: sudo apt install fonts-wqy-zenhei
        "WenQuanYi Micro Hei",
        "Source Han Sans SC",
        "Microsoft YaHei",
        "DejaVu Sans",        # 兜底：无中文字体时至少不报错
    ]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    chosen = [name for name in preferred if name in installed]
    if chosen:
        rest = [f for f in plt.rcParams["font.sans-serif"] if f not in chosen]
        plt.rcParams["font.sans-serif"] = chosen + rest
    plt.rcParams["axes.unicode_minus"] = False


_configure_chinese_font()

# 随机种子
SEED = 42

# 路径
DATA_DIR = PROJECT_ROOT / "data"
CORPUS_DIR = DATA_DIR / "corpus"
EVAL_DIR = DATA_DIR / "eval"
QA_SET_PATH = EVAL_DIR / "qa_set.jsonl"
RESULTS_DIR = PROJECT_ROOT / "results"
INDEX_DIR = PROJECT_ROOT / "index_store"

RESULTS_DIR.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)

# ============================================================
# LLM 配置：通义千问（DashScope OpenAI 兼容模式）
# ============================================================
LLM_PROVIDER = "openai"  # 固定为 openai，表示使用 OpenAI 兼容接口

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
OPENAI_API_KEY = DASHSCOPE_API_KEY  # 兼容旧变量名
OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
)
# 可选：qwen-turbo / qwen-plus / qwen-max / qwen2.5-7b-instruct 等
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "qwen-plus")

# ============================================================
# Embedding 配置：通义千问 text-embedding-v3
# ============================================================
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", DASHSCOPE_API_KEY)
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", OPENAI_BASE_URL)
# DashScope 的 embedding 接口单次最多 25 条文本，设置小一点的 chunk_size 避免超限
EMBEDDING_CHUNK_SIZE = int(os.getenv("EMBEDDING_CHUNK_SIZE", "10"))

# 切分默认参数
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64

# 检索默认参数
DEFAULT_TOP_K = 5
RRF_K = 60


def get_llm(temperature: float = 0.0):
    """返回统一的 LLM 实例：通义千问。"""
    from langchain_openai import ChatOpenAI

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "未检测到 DASHSCOPE_API_KEY，请先设置环境变量：\n"
            '  PowerShell: $env:DASHSCOPE_API_KEY="sk-你的Key"'
        )

    return ChatOpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        model=OPENAI_MODEL,
        temperature=temperature,
    )


def get_embeddings():
    """返回统一的 Embedding 实例：通义千问 text-embedding-v3。"""
    from langchain_openai import OpenAIEmbeddings

    if not EMBEDDING_API_KEY:
        raise RuntimeError(
            "未检测到 DASHSCOPE_API_KEY，请先设置环境变量：\n"
            '  PowerShell: $env:DASHSCOPE_API_KEY="sk-你的Key"'
        )

    # 兼容不同版本的 langchain-openai 参数命名
    try:
        return OpenAIEmbeddings(
            api_key=EMBEDDING_API_KEY,
            base_url=EMBEDDING_BASE_URL,
            model=EMBEDDING_MODEL,
            chunk_size=EMBEDDING_CHUNK_SIZE,
            check_embedding_ctx_length=False,
        )
    except TypeError:
        return OpenAIEmbeddings(
            openai_api_key=EMBEDDING_API_KEY,
            openai_api_base=EMBEDDING_BASE_URL,
            model=EMBEDDING_MODEL,
            chunk_size=EMBEDDING_CHUNK_SIZE,
            check_embedding_ctx_length=False,
        )