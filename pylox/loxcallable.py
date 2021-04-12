from abc import ABC, abstractmethod

class LoxCallable(ABC):
    @abstractmethod
    def arity(self):
        pass

    @abstractmethod
    def call(self, args):
        pass
