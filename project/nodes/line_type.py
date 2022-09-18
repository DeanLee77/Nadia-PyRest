from enum import Enum


class LineType(Enum):
    META = "META"
    VALUE_CONCLUSION = "VALUE_CONCLUSION"
    EXPR_CONCLUSION = "EXPR_CONCLUSION"
    COMPARISON = "COMPARISON"
    ITERATE = "ITERATE"
    WARNING = "WARNING"

    @staticmethod
    def get_all_values():
        return list(map(lambda c: c.value, LineType))
