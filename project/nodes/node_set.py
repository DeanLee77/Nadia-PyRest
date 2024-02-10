import json
from project.loggers import Logger
from project.nodes.node import Node
from . import DependencyMatrix

logging: Logger = Logger.get_logger(__name__)


class NodeSet:
    __nodeSetName: str
    __inputDictionary: dict
    __factDictionary: dict
    __nodeDictionary: dict
    __nodeIdDictionary: dict
    __sortedNodeList: []
    __defaultGoalNode: Node
    __dependencyMatrix: DependencyMatrix

    def __init__(self):
        self.__nodeSetName = ''
        self.__inputDictionary = dict()
        self.__factDictionary = dict()
        self.__nodeDictionary = dict()
        self.__nodeIdDictionary = dict()
        self.__sortedNodeList = []
        self.__defaultGoalNode = None
        self.__dependencyMatrix: DependencyMatrix = DependencyMatrix([[]])
        logging.info("NodeSet is generated")

    def __repr__(self):
        return json.dumps(self.__dict__)

    def get_dependency_matrix(self) -> DependencyMatrix:
        return self.__dependencyMatrix

    def set_dependency_matrix(self, dependency_matrix):
        if isinstance(dependency_matrix, list):
            self.__dependencyMatrix = DependencyMatrix(dependency_matrix)
        elif isinstance(dependency_matrix, DependencyMatrix):
            self.__dependencyMatrix = dependency_matrix

    def get_node_set_name(self) -> str:
        return self.__nodeSetName

    def set_node_set_name(self, node_set_name):
        if len(node_set_name) == 0:
            logging.error("node_set_name is None")
        self.__nodeSetName = node_set_name

    def set_node_id_dictionary(self, node_id_dictionary):
        if len(node_id_dictionary) == 0:
            logging.debug("node_id_dictionary has no items")
        self.__nodeIdDictionary = node_id_dictionary

    def get_node_id_dictionary(self) -> dict:
        return self.__nodeIdDictionary

    def set_node_dictionary(self, node_dictionary):
        if len(node_dictionary) == 0:
            logging.debug("node_dictionary has no items")
        self.__nodeDictionary = node_dictionary

    def get_node_dictionary(self) -> dict:
        return self.__nodeDictionary

    def set_sorted_node_list(self, sorted_node_list):
        if len(sorted_node_list) == 0:
            logging.error("sorted_node_list has no items")
        self.__sortedNodeList = sorted_node_list

    def get_sorted_node_list(self) -> list:
        return self.__sortedNodeList

    def get_input_dictionary(self) -> dict:
        return self.__inputDictionary

    def set_fact_dictionary(self, fact_dictionary):
        if len(fact_dictionary) == 0:
            logging.info("fact_dictionary has no items")
        self.__factDictionary = fact_dictionary

    def get_fact_dictionary(self) -> dict:
        return self.__factDictionary

    def get_node(self, node_index) -> Node:
        return self.__sortedNodeList[node_index]

    def get_node(self, node_name) -> Node:
        return self.__nodeDictionary[node_name]

    def get_node_by_node_id(self, node_id) -> Node:
        return self.get_node(self.get_node_id_dictionary()[node_id])

    def find_node_index(self, node_name) -> int:
        for node_index in range(len(self.get_sorted_node_list())):
            if self.get_sorted_node_list()[node_index].get_node_name() == node_name:
                return node_index

    def set_default_goal_node(self, name):
        self.__defaultGoalNode = self.get_node_dictionary().get(name)

    def get_default_goal_node(self) -> Node:
        return self.__defaultGoalNode

    def transfer_fact_dictionary_to_working_memory(self, working_memory) -> dict:
        if len(working_memory) == 0:
            logging.info("working_memory has no items")
        for key in self.__factDictionary:
            working_memory[key] = self.__factDictionary[key]

        return working_memory
