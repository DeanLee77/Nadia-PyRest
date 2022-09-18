from abc import ABCMeta
import abc
from typing import Optional

from project.fact_values import FactValue
from project.fact_values import FactValueType
from project.nodes.line_type import LineType
from project.tokens.token import Token
from project.tokens.token_string_dictionary import TokenStringDictionary
import re

from project.fact_values import FactValue


class Node(metaclass=ABCMeta):
    __staticNodeId: int = 0
    _nodeId: int = None
    _nodeName: str = None
    _nodeLine: int = None
    _variableName: str = None
    _value: FactValue = None
    _tokens: Token = None

    def __init__(self, parent_text, tokens):
        self._nodeId = Node.__staticNodeId
        Node.__staticNodeId += 1
        self._tokens = tokens

        self.initialisation(parent_text, tokens)

    @abc.abstractmethod
    def initialisation(self, parent_text: str, tokens: Token): pass

    @abc.abstractmethod
    def get_line_type(self) -> LineType: pass

    @abc.abstractmethod
    def self_evaluate(self, working_memory: dict) -> FactValue: pass

    def set_node_line(self, node_line: int):
        self._nodeLine = node_line

    def get_node_line(self) -> int:
        return self._nodeLine

    def get_node_id(self):
        return self._nodeId

    def get_node_name(self) -> str:
        return self._nodeName

    def get_tokens(self) -> Token:
        return self._tokens

    def get_variable_name(self) -> str:
        return self._variableName

    def set_node_variable(self, new_variable_name: str):
        self._variableName = new_variable_name

    def get_fact_value(self) -> FactValue:
        return self._value

    def set_value(self, last_token_string: any, last_token: any = None):
        if last_token is None:
            self._value = last_token_string
        else:
            if re.match(r"Q", last_token_string, re.IGNORECASE):
                self._value = FactValue(last_token, FactValueType.DEFI_STRING)
            elif not re.match(r"[CLMU]", last_token_string, re.IGNORECASE):
                self._value = FactValue(last_token, TokenStringDictionary.find_fact_value_type(last_token_string))
            else:
                if Node.is_boolean(last_token):
                    if re.match(r"false", last_token, re.IGNORECASE):
                        self._value = FactValue(False, FactValueType.BOOLEAN)
                    elif re.match(r"true", last_token, re.IGNORECASE):
                        self._value = FactValue(True, FactValueType.BOOLEAN)
                elif re.match(r"(^[\'\"])(.*)([\'\"]$)", last_token, re.IGNORECASE):
                    self._value = FactValue(last_token, FactValueType.DEFI_STRING)
                else:
                    self._value = FactValue(last_token, TokenStringDictionary.find_fact_value_type(last_token_string))

    @staticmethod
    def is_boolean(in_string) -> bool:
        if re.match(r"false+", in_string, re.IGNORECASE)\
                or re.match(r"true+", in_string, re.IGNORECASE):
            return True
        else:
            return False

    @staticmethod
    def is_integer(in_string) -> bool:
        return "No" == in_string

    @staticmethod
    def is_double(in_string) -> bool:
        return "De" == in_string

    @staticmethod
    def is_date(in_string) -> bool:
        return "Da" == in_string

    @staticmethod
    def is_url(in_string) -> bool:
        return "Url" == in_string

    @staticmethod
    def is_hash(in_string) -> bool:
        return "Ha" == in_string

    @staticmethod
    def is_guid(in_string) -> bool:
        return "Id" == in_string

    @staticmethod
    def reset():
        Node.__staticNodeId = 0

    @staticmethod
    def get_static_node_id() -> int:
        return Node.__staticNodeId

