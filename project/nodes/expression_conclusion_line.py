from datetime import datetime
import re

from project.loggers import Logger
from project.nodes import Node
from project.nodes.line_type import LineType
from project.fact_values import FactValue
from project.fact_values import FactValueType
from project.tokens import Tokenizer
from project.tokens import Token

logging: Logger = Logger.get_logger(__name__)


class ExprConclusionLine(Node):

    __equation: FactValue = None

    __dateFormatter = '%Y-%m-%d'

    def __init__(self, parent_text: str, tokens: Token):
        super().__init__(parent_text, tokens)

    def initialisation(self, parent_text: str, tokens: Token):
        logging.info("Generating Expression Conclusion Line with : " + str(parent_text))

        self._nodeName = parent_text
        temp_array = re.split("IS CALC", parent_text)
        self._variableName = temp_array[0].strip()
        index_of_c_in_tokens_string_list = tokens.get_tokens_string_list().index('C')
        self.set_value(tokens.get_tokens_string_list()[index_of_c_in_tokens_string_list].strip(),
                       tokens.get_tokens_list()[index_of_c_in_tokens_string_list].strip())
        self.__equation = self._value

    def get_equation(self) -> FactValue:
        return self.__equation

    def set_equation(self, equation):
        self.__equation = equation

    def get_line_type(self) -> LineType:
        return LineType.EXPR_CONCLUSION

    def self_evaluate(self, working_memory: dict) -> FactValue:
        # this node_line can evaluate all python syntax as a part of evaluation.
        # however, in order to complex computation/calculation, a person editing a rule
        # must be familiar with python syntax, and need to change 'pattern', otherwise limit the
        # calculation in handling int, double(long) and difference in years between two dates at the moment.
        # if difference in days or months is required then new 'keyword'
        # must be introduced such as 'Diff Years', 'Diff Days', or 'Diff Months'

        equation_in_string = self.__equation.get_value()
        pattern = re.compile(r'[-+/*()?:;,.""](\s*)')
        date_pattern = re.compile(r'([0-2]?[0-9]|3[0-1])/(0?[0-9]|1[0-2])/([0-9][0-9])?[0-9][0-9]|\
                                  ([0-9][0-9])?[0-9][0-9]/(0?[0-9]|1[0-2])/([0-2]?[0-9]|3[0-1])')

        # logic for this is as follows;
        #  1. replace all variables with actual values from 'workingMemory'
        #  2. find out if equation is about date (difference in years) calculation or not
        #  3. if it is about date then convert all relevant date-in-string to datetime then calculate
        #  3-1. if it is about int or double(long) then use plain Javascript

        script = equation_in_string
        temp_script = script

        if pattern.match(equation_in_string):
            temp_array = re.split(pattern, equation_in_string)
            temp_array_length = len(temp_array)
            temp_item = ''

            for i in range(temp_array_length):
                temp_item = temp_array[i].strip()
                if (len(temp_item) != 0) and (temp_item in dict(working_memory)) \
                        and (dict(working_memory)[temp_item] is not None):
                    temp_fact_value: FactValue = working_memory[temp_item]
                    if temp_fact_value.get_value_type() == FactValueType.DATE:
                        # below line is temporary solution.
                        # Within next iteration it needs to be that the nodes should take dateFormatter
                        # for its constructor to determine which date format it needs

                        temp_str = temp_fact_value.get_value().strftime("%d/%m/%Y")
                        temp_script = temp_script.replace(temp_item, temp_str)
                    else:
                        temp_script = temp_script.replace(temp_item, str(working_memory[temp_item].get_value()))

        date_matcher = date_pattern.finditer(temp_script)
        return_value = None
        if date_matcher:
            date_array = []
            for x in date_matcher:
                date_time = datetime.strptime(x.group(), '%d/%m/%Y')
                date_array.append(date_time)

            if len(date_array) > 0:
                result = (date_array[0] - date_array[1]).days/365.2
            else:
                result = eval(temp_script)

            check_tokens = Tokenizer.get_tokens(str(result)).get_tokens_string()

            if check_tokens == 'No':
                return_value = FactValue(result, FactValueType.INTEGER)
            elif check_tokens == 'De':
                return_value = FactValue(result, FactValueType.DOUBLE)
                # there is no function for outcome to be a date at the moment
                # E.g.The determination IS CALC(enrollment date + 5 days)
            else:
                return_value = FactValue(result, FactValueType.BOOLEAN)

        return return_value


