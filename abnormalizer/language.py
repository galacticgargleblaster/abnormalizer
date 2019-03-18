from abc import abstractmethod, ABC
from typing import List

from . import TokenLike, Token, FormatSpec


class LanguageFeature(TokenLike, ABC):
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
    
    @abstractmethod
    def formatted(self, spec: FormatSpec) -> str:
        pass

    @property
    def value(self):
        return "".join([t.value for t in self.tokens])

    def remove_whitespace(self):
        [t.strip() for t in self.tokens]
        self.tokens = [t for t in self.tokens if t.value]

class PreProcessorDirective(LanguageFeature):
    def formatted(self, spec: FormatSpec) -> str:
        self.tokens[1].value = self.tokens[1].value.lstrip()
        return f"#{' '*spec.define_depth_n_spaces}{' '.join([t.value for t in self.tokens[1:]])}"
    

class FunctionDefinition(LanguageFeature):
    def formatted(self, spec: FormatSpec) -> str:
        pass
    pass

class FunctionPrototype(LanguageFeature):
    def formatted(self, spec: FormatSpec) -> str:
        pass
    pass

class GlobalDeclaration(LanguageFeature):
    def formatted(self, spec: FormatSpec) -> str:
        pass
    pass

class StructureLike(LanguageFeature):
    def formatted(self, global_scope_n_tabs):
        return self.value