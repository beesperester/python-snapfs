class Config:

    def __init__(self) -> None:
        self.ignore = [
            "*.DS_Store",
            "*.git",
            "*.venv",
            "*.vscode",
            "*.pyc",
            "__pycache__"
        ]


config = Config()
