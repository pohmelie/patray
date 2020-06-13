from importlib import resources

version = resources.read_text("patray", "version.txt").strip()
