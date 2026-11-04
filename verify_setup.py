import importlib
packages = ["langchain", "langchain_openai", "langchain_community",
            "llama_index", "chromadb", "mcp", "dotenv"]
for name in packages:
    try:
        mod = importlib.import_module(name)
        version = getattr(mod, "__version__", "installed")
        print(f"OK   {name}: {version}")
    except ImportError as e:
        print(f"FAIL {name}: {e}")