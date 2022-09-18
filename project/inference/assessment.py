from project.loggers import Logger
from project.nodes import Node
from project.nodes import NodeSet

logging: Logger = Logger.get_logger(__name__)

# the reason of having Assessment class is to allow a user to do multiple assessment within one or multiple conditions.


class Assessment:
    __goal_node: Node

    # the goal rule index in ruleList of ruleSet
    __goal_node_index: int

    # each instance of this object has a variable of ruleToBeAsked due to the following reasons
    # 1. a user will be allowed to do assessment on multiple investigation points at the same time
    # 2. a user will be allowed to do an assessment within another assessment.
    __node_to_be_asked: Node

    # this variable is to track next node to be asked within 'IterateLine' type node.
    # However, better way needs to be found.
    __aux_node_to_be_asked: Node

    def __init__(self, node_set: NodeSet, goal_node_name: str):
        self.__goal_node = node_set.get_node_dictionary()[goal_node_name]
        self.__goal_node_index = node_set.find_node_index(goal_node_name)
        self.__node_to_be_asked = None
        self.__aux_node_to_be_asked = None

    def set_assessment(self, node_set: NodeSet, goal_node_name: str):
        self.__goal_node = node_set.get_node_dictionary()[goal_node_name]
        self.__goal_node_index = node_set.find_node_index(goal_node_name)
        self.__node_to_be_asked = None

    def get_goal_node(self) -> Node:
        return self.__goal_node

    def get_goal_node_index(self) -> int:
        return self.__goal_node_index

    def set_node_to_be_asked(self, node_to_be_asked: Node):
        self.__node_to_be_asked = node_to_be_asked

    def get_node_to_be_asked(self) -> Node:
        return self.__node_to_be_asked

    def set_aux_node_to_be_asked(self, aux_node_to_be_asked: Node):
        self.__aux_node_to_be_asked = aux_node_to_be_asked

    def get_aux_node_to_be_asked(self) -> Node:
        return self.__aux_node_to_be_asked

