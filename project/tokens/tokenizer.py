import re

from project.constants import TokenizerMatcherConstant
from project.tokens import Token
from project.loggers import Logger


class Tokenizer:

    # the order of Pattern in the array of 'matchPatterns' is extremely important because some patterns won't work
    # if other patterns are invoked earlier than them especially 'I' pattern.
    # 'I' pattern must come before 'U' pattern, 'Url' pattern must come before 'L' pattern within current patterns.

    match_patterns = tuple(TokenizerMatcherConstant.get_all_matcher())
    token_type = ("S", "Q", "R", "I", "M", "U", "Url", "O", "C", "No", "Ha", "De", "Da", "Id", "L")

    @classmethod
    def get_tokens(cls, text: str) -> Token:
        logging = Logger.get_logger(__name__)

        token_string_list = []
        token_list = []
        token_string = ''
        text_length = len(text)

        while text_length != 0:
            for i in range(len(cls.match_patterns)):
                regex = re.compile(cls.match_patterns[i])
                match = regex.match(text)
                if match:
                    group = match.group(0)
                    # ignore space tokens
                    if cls.token_type[i] != 'S':
                        token_string_list.append(cls.token_type[i])
                        token_list.append(group.strip())
                        token_string += str(cls.token_type[i])

                    text = text[len(group):text_length].strip()
                    text_length = len(text)
                    break

                if i >= len(cls.match_patterns) - 1:
                    text_length = 0
                    token_string = "WARNING"
                    logging.warning("The written Policy/Rule/Step is not in an appropriate format" + text)

        tokens = Token(token_list, token_string_list, token_string)

        return tokens

