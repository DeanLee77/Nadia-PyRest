from enum import Enum


class TokenizerMatcherConstant(Enum):

    SPACE_MATCHER = r"^\s+"
    QUOTED_MATCHER = r"^([\"\“])(.*)([\"\”])(\.)*"
    RULE_SET_MATCHER = r"^(RULE SET:)"
    ITERATE_MATCHER = r"^(ITERATE:(\s*)LIST OF)(.)"
    MIXED_MATCHER = r"^([A-Z][a-z-'’,\.\s]+)+"
    UPPER_MATCHER = r"^([:'’,\.A-Z_\s]+(?![a-z]))"
    URL_MATCHER = r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?"
    OPERATOR_MATCHER = r"^([<>=]+)"
    CALCULATION_MATCHER = r"^(\()([\s|\d+(?!/.)|\w|\W]*)(\))"
    NUMBER_MATCHER = r"^(\d+)(?!\w|\-|\/|\.|\d)+"
    HASH_MATCHER = r"^([-]?)([0-9a-f]{10,}$)(?!\\-)*"
    DECIMAL_NUMBER_MATCHER = r"^([\d]+\.\d+)(?!\d)"
    DATE_MATCHER = r"^([0-2]?[0-9]|3[0-1])/(0?[0-9]|1[0-2])/([0-9][0-9])?[0-9][0-9]|^([0-9][0-9])?[0-9][0-9]/(0?[" \
                   r"0-9]|1[0-2])/([0-2]?[0-9]|3[0-1]) "
    GUID_MATCHER = r"^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}"
    LOWER_MATCHER = r"^([a-z\-'’,\.\s]+(?!\d))"

    @staticmethod
    def get_all_matcher() -> list:
        return list(map(lambda x: x.value, TokenizerMatcherConstant))

    @staticmethod
    def get_all_enums() -> list:
        return list(map(lambda c: c, TokenizerMatcherConstant))
