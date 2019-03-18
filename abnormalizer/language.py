from abc import abstractmethod, ABC
from typing import List

from . import FormatSpec
from .token import TokenLike, Token, distance_to_next_token_containing


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


class GlobalScopeContributor(ABC):
    @abstractmethod
    def minimum_global_scope_indentation(self) -> int:
        pass


class PreProcessorDirective(LanguageFeature):
    def formatted(self, spec: FormatSpec) -> str:
        self.tokens[1].value = self.tokens[1].value.lstrip()
        return f"#{' '*spec.define_depth_n_spaces}{' '.join([t.value for t in self.tokens[1:]])}"
      

class FunctionBase(GlobalScopeContributor):
    def minimum_global_scope_indentation(self) -> int:
        identifier_idx = distance_to_next_token_containing(self.tokens, start=0, substring='(')
        idx = identifier_idx - 1
        while (self.tokens[idx].value == '*'):
            idx -= 1
        line = " ".join(self.tokens[:idx]) + " "
        return len(line)

class FunctionDefinition(LanguageFeature, FunctionBase):
    def formatted(self, spec: FormatSpec) -> str:
        return self.value

class FunctionPrototype(LanguageFeature, FunctionBase):
    def formatted(self, spec: FormatSpec) -> str:
        return self.value

class GlobalDeclaration(LanguageFeature, GlobalScopeContributor):
    def formatted(self, spec: FormatSpec) -> str:
        return self.value

    def minimum_global_scope_indentation(self) -> int:
        pass

class StructureLike(LanguageFeature, GlobalScopeContributor):
    @property
    def _identifier_idx(self):
        return distance_to_next_token_containing(self.tokens, start=0, substring='{')
    
    def minimum_local_scope_indentation(self) -> int:
        min_indentation = 0
        idx = self._identifier_idx + 2
        while (self.tokens[idx].value != '}'):
            name_idx = idx + distance_to_next_token_containing(self.tokens, idx, ';')
            last_type_specifier_idx = name_idx - 1
            while self.tokens[last_type_specifier_idx].value == '*':
                last_type_specifier_idx -= 1
            line = " ".join(t.value for t in self.tokens[idx: last_type_specifier_idx + 1]) + " "
            min_indentation = max(min_indentation, len(line))
            idx = name_idx + 1
        return min_indentation

    def minimum_global_scope_indentation(self) -> int:
        idx = self._identifier_idx - 1
        while (self.tokens[idx].value == '*'):
            idx -= 1
        line = " ".join([t.value for t in self.tokens[:idx]]) + " "
        return len(line)


    def formatted(self, spec: FormatSpec) -> str:
        output = ' '.join([t.value for t in self.tokens[:self._identifier_idx]])
        left_padding = len(output + " ") 
        n_tabs = int((spec.global_scope_n_chars - left_padding) / 4)
        output += n_tabs * '\t'
        output += f"{self.tokens[self._identifier_idx].value}\n"
        return output 
