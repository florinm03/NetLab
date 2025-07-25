from typing import IO, List


class Image:
    def __init__(self, name: str, labels: List[str]) -> None:
        self.name = name
        self.labels = labels
