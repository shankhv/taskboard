from typing import Optional

class Category:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        id: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            "_id": self.id,
            "name": self.name,
            "description": self.description
        }