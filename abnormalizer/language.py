from abc import abstractmethod
from typing import List

from . import TokenLike, Token


class LanguageFeature(TokenLike):
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
    
    @abstractmethod
    def formatted(self):
        pass

    @property
    def value(self):
        return "".join([t.value for t in self.tokens])

    def remove_whitespace(self):
        [t.strip() for t in self.tokens]
        self.tokens = [t for t in self.tokens if t.value]

class PreProcessorDirective(LanguageFeature):
    def formatted(self, indent_spaces: int) -> str:
        self.tokens[1].value = self.tokens[1].value.lstrip()
        return f"#{' '*indent_spaces}{' '.join([t.value for t in self.tokens[1:]])}"
    

class FunctionDefinition(LanguageFeature):
    pass

class FunctionPrototype(LanguageFeature):
    pass

class GlobalDeclaration(LanguageFeature):
    pass

class StructureLike(LanguageFeature):
    def formatted(self, global_scope_n_tabs):
        return self.value