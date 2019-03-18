from abc import abstractmethod, ABC
from typing import List

from . import FormatSpec, logger
from .token import TokenLike, Token, distance_to_next_token_containing, find_range_of_tokens_within_scope

TAB = '\t'

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
        line = " ".join([t.value for t in self.tokens[:idx]]) + " "
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

class StructureBase(LanguageFeature, GlobalScopeContributor, ABC):

    @abstractmethod
    def _mangle_names(self) -> None:
        """ 
        mangle noncompliant names such as foobar into t_foobar, e_foobar, g_foobar, ...
        """

    @property
    def _identifier_idx(self):
        return distance_to_next_token_containing(self.tokens, start=0, substring='{') - 1
    
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
        idx = self._identifier_idx
        while (self.tokens[idx].value == '*'):
            idx -= 1
        line = " ".join([t.value for t in self.tokens[:idx]]) + " "
        return len(line)


    def formatted(self, spec: FormatSpec) -> str:
        idx = self._identifier_idx
        type_specifiers = ' '.join([t.value for t in self.tokens[:idx]])
        left_padding = len(type_specifiers + " ") 
        n_tabs = spec.tabs_needed_to_pad_to_global_scope(left_padding)
        identifier = self.tokens[idx].value
        
        open_b, close_b = find_range_of_tokens_within_scope(self.tokens, idx, '{')

        import ipdb; ipdb.set_trace()

        output = f"""{type_specifiers}{n_tabs * TAB}{identifier}
        {{
        {TAB}{open_b}
        }};
        """
        return output 

class StructureDefinition(StructureBase):
    def _mangle_names(self):
        val = self.tokens[self._identifier_idx - 1]
        if not val.startswith('s_'):
            self.tokens[self._identifier_idx].value = f"s_{val}"
            logger.warning("mangled")
        

class EnumDefinition(StructureBase):
    def _mangle_names(self):
        pass

class TypedefStructureDefinition(StructureBase):
    def _mangle_names(self):
        pass
    pass

class TypedefEnumDefinition(StructureBase):
    def _mangle_names(self):
        pass
    pass


class StructureLike(object):
    def __new__(cls, tokens: List[Token]):
        if any([t.value == 'typedef' for t in tokens]):
            if any([t.value == 'struct' for t in tokens]):
                return TypedefStructureDefinition(tokens)
            elif any ([t.value == 'enum' for t in tokens]):
                return TypedefEnumDefinition(tokens)
        elif any([t.value == 'struct' for t in tokens]):
            return StructureDefinition(tokens)
        elif any ([t.value == 'enum' for t in tokens]):
            return EnumDefinition(tokens)
        else:
            raise NotImplementedError(f"formatting not implemented for:\n{[t.value for t in tokens]}")
