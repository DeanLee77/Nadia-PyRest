import json
from project.loggers import Logger
from project.nodes.node import Node
from project.tokens import Token
from project.nodes.line_type import LineType
from project.fact_values import FactValue, FactValueType
from datetime import datetime

logging: Logger = Logger.get_logger(__name__)


class ComparisonLine(Node):
    __operatorString = None
    __lhs = None
    __rhs = None

    def __init__(self, child_text: str, tokens: Token):
        super().__init__(child_text, tokens)
        self._lineType = LineType.COMPARISON
    
    def __repr__(self):
        return json.dumps(self.__dict__)

    def initialisation(self, child_text: str, tokens: Token):
        logging.info("Generating Comparison Line with : " + str(child_text))

        self._nodeName = child_text
        # In 'eval' engine '=' operator means assigning a value,
        # hence if the operator is '=' then it needs to be replaced with '=='.
        operator_index = tokens.get_tokens_string_list().index("O")
        if tokens.get_tokens_list()[operator_index] == "=":
            self.__operatorString = "=="
            self._variableName = child_text.split("=")[0].strip()
        else:
            self.__operatorString = tokens.get_tokens_list()[operator_index]
            self._variableName = child_text.split(self.__operatorString)[0].strip()

        self.__lhs = self._variableName
        tokens_string_list_size = len(tokens.get_tokens_string_list())
        last_token = tokens.get_tokens_list()[tokens_string_list_size - 1]
        last_token_string = tokens.get_tokens_string_list()[tokens_string_list_size - 1]
        self.set_value(last_token_string, last_token)
        self.__rhs = self._value

    def get_rule_name(self):
        return self._nodeName

    def get_lhs(self):
        return self.__lhs

    def get_rhs(self):
        return self.__rhs

    def get_operator(self):
        return self.__operatorString

    def get_line_type(self):
        return LineType.COMPARISON

    def self_evaluate(self, working_memory):
        # Negation type can only be used for this line type
        working_memory_lhs_value: FactValue = None
        script = ""
        if self._variableName in working_memory:
            working_memory_lhs_value = working_memory[self._variableName]

        rhs_value_in_string = self.__rhs.get_value()
        if rhs_value_in_string in working_memory:
            working_memory_rhs_value = working_memory[rhs_value_in_string]
        else:
            working_memory_rhs_value = self.get_rhs()

        # There will NOT be the case of that workingMemoryRhsValue is null because the nodes must be in following format;
        # - A = 12231 (int or double)
        # - A = Adam sandler (String)
        # - A = 11/11/1977 (Date)
        # - A = 123123dfae1421412aer(Hash)
        # - A = 1241414-12421312-142421312(UUID)
        # - A = true(Boolean)
        # - A = www.aiBrain.com(URL)
        # - A = B(another variable)

        # if it is about date comparison then string of 'script' needs rewriting
        if ((working_memory_lhs_value is not None)
            and (working_memory_lhs_value.get_value_type() == FactValueType.DATE)) \
                or \
                ((working_memory_rhs_value is not None)
                 and (working_memory_rhs_value.get_value_type() == FactValueType.DATE)):
            working_memory_lhs_value_str = str(working_memory_lhs_value.get_value()).split(" ")[0]
            working_memory_rhs_value_str = str(working_memory_rhs_value.get_value()).split(" ")[0]
            if self.__operatorString == ">":
                return_value = \
                    datetime.strptime(working_memory_lhs_value_str, "%Y-%m-%d") \
                    > datetime.strptime(working_memory_rhs_value_str, "%Y-%m-%d")
            elif self.__operatorString == ">=":
                return_value = \
                    datetime.strptime(working_memory_lhs_value_str, "%Y-%m-%d") \
                    >= datetime.strptime(working_memory_rhs_value_str, "%Y-%m-%d")
            elif self.__operatorString == "<":
                return_value = \
                    datetime.strptime(working_memory_lhs_value_str, "%Y-%m-%d") \
                    < datetime.strptime(working_memory_rhs_value_str, "%Y-%m-%d")
            elif self.__operatorString == "<=":
                return_value = \
                    datetime.strptime(working_memory_lhs_value_str, "%Y-%m-%d") \
                    <= datetime.strptime(working_memory_rhs_value_str, "%Y-%m-%d")
            elif self.__operatorString == "==":
                return_value = \
                    datetime.strptime(working_memory_lhs_value_str, "%Y-%m-%d") \
                    == datetime.strptime(working_memory_rhs_value_str, "%Y-%m-%d")
            script = str(return_value)
        elif (working_memory_lhs_value is not None) and \
             ((working_memory_lhs_value.get_value_type() == FactValueType.DECIMAL)
                or (working_memory_lhs_value.get_value_type() == FactValueType.DOUBLE)\
                or (working_memory_lhs_value.get_value_type() == FactValueType.INTEGER)
                or (working_memory_lhs_value.get_value_type() == FactValueType.NUMBER)):

            script = str(working_memory_lhs_value.get_value()) \
                     + str(self.__operatorString) \
                     + str(working_memory_rhs_value.get_value())
        elif working_memory_lhs_value is not None and working_memory_lhs_value.get_value_type() == FactValueType.LIST:
            for fact_value_in_list in working_memory_lhs_value.get_value():
                script = 'False'
                if fact_value_in_list.get_value() == working_memory_rhs_value.get_value():
                    script = 'True'
                    break
        else:
            working_memory_rhs_value_str = ""
            if working_memory_rhs_value.get_value_type() == FactValueType.DEFI_STRING:
                working_memory_rhs_value_str = str(eval(working_memory_rhs_value.get_value()))
            else:
                working_memory_rhs_value_str = str(working_memory_rhs_value.get_value())
            if (working_memory_rhs_value is not None) and (working_memory_lhs_value is not None):
                script = "'" + str(working_memory_lhs_value.get_value()) \
                         + "'" + self.__operatorString \
                         + "'" + working_memory_rhs_value_str + "'"

        if (working_memory_rhs_value is not None) and (working_memory_lhs_value is not None):
            return FactValue(eval(script))
