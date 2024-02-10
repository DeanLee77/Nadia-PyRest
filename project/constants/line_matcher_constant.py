from enum import Enum


class LineMatcherConstant(Enum):

    META_PATTERN_MATCHER = r"(^U)([MLU]*)([(No)(Da)ML(De)(Ha)(U(rl)?)(Id)]*$)"
    VALUE_CONCLUSION_MATCHER = r"(^[LM]+)(U)?([MLQ(No)(Da)(De)(Ha)(Url)(Id)]*$)(?!C)"
    EXPRESSION_CONCLUSION_MATCHER = r"(^[LM(Da)]+)(U)(C)"
    COMPARISON_MATCHER = r"(^[MLU(Da)]+)(O)([MLUQ(No)(Da)(De)(Ha)(Url)(Id)]*$)"
    ITERATE_MATCHER = r"(^[MLU(No)(Da)]+)(I)([MLU]+$)"
    WARNING_MATCHER = r"WARNING"

    @staticmethod
    def get_all_line_matchers() -> list:
        return list(map(lambda c: c.value, LineMatcherConstant))

    @staticmethod
    def get_all_line_enums() -> list:
        return list(map(lambda c: c, LineMatcherConstant))
