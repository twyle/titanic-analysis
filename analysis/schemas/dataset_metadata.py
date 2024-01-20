from __future__ import annotations
import logging
from pydantic import BaseModel, Field
from json import load, dump


class DatasetMetadata(BaseModel):
    source: str
    cols: list[str] = Field(default_factory=list)
    description: str
    path: str
    id: str

    @classmethod
    def from_metadata(cls, metadata_file: str) -> Self:
        """Create metadata from metadata file."""
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata: dict = load(f)
        except FileNotFoundError: #JSONDecodeError
            logging.error(f'There is no file such path "{metadata_file}".')
        else:
            return cls(**metadata)

    def save(self, path: str) -> str:
        """Save the metadata to disk."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                dump(self.model_dump(), f, indent=4)
        except FileNotFoundError:
            logging.error(f'There is no file such path "{path}".')
            return ''
        return path
