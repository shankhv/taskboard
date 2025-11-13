from typing import Optional

class Tag:
    def __init__(
        self,
        name: str,
        id: Optional[str] = None
    ):
        self.id = id
        self.name = name

    def to_dict(self):
        return {
            "_id": self.id,
            "name": self.name
        }