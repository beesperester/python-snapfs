class Config:

    def __init__(self) -> None:
        self.ignore = [
            ".snapfs",
            "*",
            "^*.c4d",
            "^*.png"
        ]


config = Config()
