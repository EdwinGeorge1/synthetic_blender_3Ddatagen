from abc import ABC, abstractmethod

class PrimitiveWrapper(ABC):
    @abstractmethod
    def run(self, image_path: str, outdir: str):
        """
        Wrap `image_path` onto this primitive and export into `outdir`.
        Must prompt for dimensions exactly as before.
        """
        pass
from abc import ABC, abstractmethod

class PrimitiveWrapper(ABC):
    @abstractmethod
    def run(self, image_path: str, outdir: str):
        """
        Wrap `image_path` onto this primitive and export into `outdir`.
        Must prompt for dimensions exactly as before.
        """
        pass
