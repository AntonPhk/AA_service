from abc import ABC, abstractmethod


class DatabaseInterface(ABC):
    @abstractmethod
    async def get_by_id(self, *args, **kwargs): ...

    @abstractmethod
    async def create(self, *args, **kwargs): ...

    @abstractmethod
    async def update(self, *args, **kwargs): ...

    @abstractmethod
    async def delete(self, *args, **kwargs): ...
