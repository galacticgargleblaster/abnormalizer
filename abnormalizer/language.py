from abc import abstractmethod, ABC
from typing import List, Tuple

from . import FormatSpec, logger, tabs_needed_to_pad_to_scope, printed_length, MAX_LINE_LENGTH
from .token import TokenLike, Token, distance_to_next_token_containing, find_range_of_tokens_within_scope
from pygments.token import Token as PT

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
    def minimum_global_scope_indentation(self, spec: FormatSpec) -> int:
        pass


class PreProcessorDirective(LanguageFeature):
    def formatted(self, spec: FormatSpec) -> str:
        self.tokens[1].value = self.tokens[1].value.lstrip()
        return f"#{' '*spec.define_depth_n_spaces}{' '.join([t.value for t in self.tokens[1:]])}"
      

class FunctionBase(GlobalScopeContributor):
    @staticmethod
    def _wrap_to_fit(line: str) -> str:
        if (printed_length(line) > MAX_LINE_LENGTH):
            pre, post = line.split('(', maxsplit=1)
            line = f"{pre}(\n\t{post}"
        return line
        
    @property
    def _split_index(self) -> int:
        """ token idx relative to 0 of function name (or first *).  future split location """
        identifier_idx = distance_to_next_token_containing(self.tokens, start=0, substring='(')
        idx = identifier_idx - 1
        while (self.tokens[idx - 1].value == '*'):
            idx -= 1
        return idx

    @property
    def _return_type(self) -> str:
        return f"{' '.join([t.value for t in self.tokens[:self._split_index]])}"

    def _prototype(self, spec: FormatSpec) -> str:
        n_tabs = tabs_needed_to_pad_to_scope(printed_length(self._return_type), spec.global_scope_n_chars)
        arg_start = distance_to_next_token_containing(self.tokens, 0, '(')
        ptr_and_identifier = "".join([t.value for t in self.tokens[self._split_index: self._split_index + arg_start - 1]])
        line = self._return_type + (TAB * n_tabs) + ptr_and_identifier + self._formatted_arguments(spec)
        return line

    def _formatted_arguments(self, spec: FormatSpec) -> str:
        open_p, close_p = find_range_of_tokens_within_scope(self.tokens, 0, '(')
        idx = open_p
        output = ""
        while idx <= close_p:
            if (self.tokens[idx].ttype == PT.Operator \
                and self.tokens[idx].value == '*' \
                    and self.tokens[idx - 1].value not in ['*', '(']):
                output += " "
            output += self.tokens[idx].value
            if (self.tokens[idx].ttype in [PT.Keyword, PT.Keyword.Type] and \
                (self.tokens[idx + 1].ttype in [PT.Keyword, PT.Keyword.Type] or \
                  self.tokens[idx + 1].ttype == PT.Name)):
                output += " "
            if output.endswith(','):
                output += " "
            idx += 1
        return output

    def minimum_global_scope_indentation(self, spec: FormatSpec) -> int:
        line = " ".join([t.value for t in self.tokens[:self._split_index]]) + " "
        return len(line)

class FunctionDefinition(LanguageFeature, FunctionBase):
    def formatted(self, spec: FormatSpec) -> str:
        prototype = (self._wrap_to_fit(self._prototype(spec)))
        return prototype[:-1] + "\n" + self._format_bracketed_area(spec) 

    def _format_bracketed_area(self, spec: FormatSpec):
        output = ""
        open_b, close_b = find_range_of_tokens_within_scope(self.tokens, 0, '{')
        idx = open_b
        depth = 0
        while (idx < close_b):
            val = self.tokens[idx].value
            output += f"{TAB * depth}{val}\n"
            if (val == '{'):
                depth += 1
            elif (val == '}'):
                depth -= 1
            idx += 1
        return output

class FunctionPrototype(LanguageFeature, FunctionBase):

    def formatted(self, spec: FormatSpec) -> str:
        return (self._wrap_to_fit(self._prototype(spec)))

class GlobalDeclaration(LanguageFeature, GlobalScopeContributor):
    def formatted(self, spec: FormatSpec) -> str:
        return self.value

    def minimum_global_scope_indentation(self, spec: FormatSpec) -> int:
        pass

class StructureBase(LanguageFeature, GlobalScopeContributor, ABC):
    SEPARATOR = ';'

    @abstractmethod
    def _mangle_names(self) -> None:
        """ 
        mangle noncompliant names such as foobar into t_foobar, e_foobar, g_foobar, ...
        """

    @property
    def user_defined_types(self) -> List[str]:
        types = []
        for idx, t in enumerate(self.tokens):
            if t.ttype == PT.Name and idx > 0 and self.tokens[idx - 1].value in ['typedef', 'struct', 'enum']:
                types.append(t.value)
        if 'typedef' in [t.value for t in self.tokens]:
            open_b, close_b = find_range_of_tokens_within_scope(self.tokens, self._identifier_idx, '{')
            types.append(self.tokens[close_b].value)
        return types

    @property
    def _identifier_idx(self):
        return distance_to_next_token_containing(self.tokens, start=0, substring='{') - 1

    @property
    def _members(self) -> List[List[Token]]:
        """ returns struct/enum members """
        members = []
        open_b, close_b = find_range_of_tokens_within_scope(self.tokens, self._identifier_idx, '{')
        idx = open_b + 1
        while (idx < close_b):
            dist = distance_to_next_token_containing(self.tokens, idx, self.SEPARATOR)
            if (dist and idx + dist >= close_b): 
                break
            if dist:
                members.append(self.tokens[idx:idx+dist + 1])
            else:
                members.append(self.tokens[idx:close_b - 1])
                return members
            idx += dist + 1
        return members
    
    def _formatted_body(self, spec: FormatSpec) -> str:
        result = ""
        for member in self._members:
            first, last = self._split_member(member, spec)
            line = f"{TAB}{' '.join([t.value for t in first])}"
            n_tabs = tabs_needed_to_pad_to_scope(printed_length(line), spec.global_scope_n_chars)
            line += f"{TAB * n_tabs}{''.join([t.value for t in last])}\n"
            result += line
        return result
    
    def _split_member(self, member: List[Token], spec: FormatSpec) -> Tuple[List[Token]]:
        """ spilts a member into parts pre- and post-indentation """
        idx = 0
        while (member[idx].ttype in [PT.Keyword, PT.Keyword.Type]\
                or member[idx].value in spec.user_defined_type_names):
            idx += 1
        return (member[:idx], member[idx:])
    
    def minimum_local_scope_indentation(self, spec: FormatSpec) -> int:
        min_indentation = 0
        for member in self._members:
            first, last = self._split_member(member, spec)
            partial_line = f"{TAB}{' '.join([t.value for t in first])} "
            min_indentation = max(min_indentation, printed_length(partial_line))
        return min_indentation

    def minimum_global_scope_indentation(self, spec: FormatSpec) -> int:
        idx = self._identifier_idx
        while (self.tokens[idx].value == '*'):
            idx -= 1
        line = " ".join([t.value for t in self.tokens[:idx]]) + " "
        return max(len(line), self.minimum_local_scope_indentation(spec))

    def formatted(self, spec: FormatSpec) -> str:
        idx = self._identifier_idx
        type_specifiers = ' '.join([t.value for t in self.tokens[:idx]])
        left_padding = len(type_specifiers + " ") 
        n_tabs = spec.tabs_needed_to_pad_to_global_scope(left_padding)
        identifier = self.tokens[idx].value
        
        output = f"""{type_specifiers}{n_tabs * TAB}{identifier}
{{
{self._formatted_body(spec)}}}"""
        return output 

class StructureDefinition(StructureBase):
    SEPARATOR = ';'
    def _mangle_names(self):
        val = self.tokens[self._identifier_idx - 1]
        if not val.startswith('s_'):
            self.tokens[self._identifier_idx].value = f"s_{val}"
            logger.warning("mangled")


    def formatted(self, spec: FormatSpec) -> str:
        return super().formatted(spec) + ';'

class EnumDefinition(StructureBase):
    SEPARATOR = ','
    def _mangle_names(self):
        pass
    
    def _formatted_body(self, spec: FormatSpec) -> str:
        result = ""
        for member in self._members:
            line = f"{TAB}{' '.join([t.value for t in member if t.value != ','])},\n"
            result += line
        return result
    
    def formatted(self, spec: FormatSpec) -> str:
        return super().formatted(spec) + ';'

class WithTypedef(StructureBase):
    def formatted(self, spec: FormatSpec) -> str:
        n_tabs = tabs_needed_to_pad_to_scope(len("}"), spec.global_scope_n_chars)
        line = f"{TAB * n_tabs}{self.tokens[-2].value};"
        return super().formatted(spec) + line

class TypedefStructureDefinition(WithTypedef):
    def _mangle_names(self):
        pass
    pass

class TypedefEnumDefinition(EnumDefinition, WithTypedef):
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
