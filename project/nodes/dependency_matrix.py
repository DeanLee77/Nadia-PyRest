from project.nodes.dependency_type import DependencyType


class DependencyMatrix:
    # order of dependency type
    # 1. MANDATORY
    # 2. OPTIONAL
    # 3. POSSIBLE
    # 4. AND
    # 5. OR
    # 6. NOT
    # 7. KNOWN
    # int value will be '1' if any one of them is true case otherwise '0'
    # for instance, if a rule is in 'MANDATORY AND NOT' dependency then
    # dependency type value is '1001010'
    #
    # if there is no dependency then value is 0000000

    __dependencyTwoDimensionList: [[]] = None
    __dependencyListSize: int = None

    def __init__(self, dependency_two_dimension_list):
        self.__dependencyTwoDimensionList = dependency_two_dimension_list
        self.__dependencyListSize = len(dependency_two_dimension_list)

    def get_dependency_two_dimension_list(self) -> list:
        return self.__dependencyTwoDimensionList

    def get_dependency_type(self, parent_rule_id, child_rule_id) -> int:
        return self.__dependencyTwoDimensionList[parent_rule_id][child_rule_id]

    def get_to_child_dependency_list(self, node_id) -> list:

        to_child_dependency_list = []
        target_node_dependency_list = self.__dependencyTwoDimensionList[node_id]

        for child_index in range(len(target_node_dependency_list)):
            if (target_node_dependency_list[child_index] != -1) and (child_index != node_id):
                to_child_dependency_list.append(child_index)

        return to_child_dependency_list

    def get_or_to_child_dependency_list(self, node_id) -> list:
        or_to_child_dependency_list = []
        target_node_dependency_list = self.__dependencyTwoDimensionList[node_id]
        or_dependency = DependencyType.get_or()

        for child_index in range(len(target_node_dependency_list)):
            if (target_node_dependency_list[child_index] != -1) \
                    and (child_index != node_id) \
                    and ((target_node_dependency_list[child_index] & or_dependency) == or_dependency):
                or_to_child_dependency_list.append(child_index)

        return or_to_child_dependency_list

    def get_and_to_child_dependency_list(self, node_id) -> list:
        and_to_child_dependency_list = []
        target_node_dependency_list = self.__dependencyTwoDimensionList[node_id]
        and_dependency = DependencyType.get_and()

        for child_index in range(len(target_node_dependency_list)):
            if (target_node_dependency_list[child_index] != -1) \
                    and (child_index != node_id) \
                    and ((target_node_dependency_list[child_index] & and_dependency) == and_dependency):
                and_to_child_dependency_list.append(child_index)

        return and_to_child_dependency_list

    def get_mandatory_to_child_dependency_list(self, node_id) -> list:
        mandatory_child_dependency_list = []
        target_node_dependency_list = self.__dependencyTwoDimensionList[node_id]
        mandatory_dependency = DependencyType.get_mandatory()

        for child_index in range(len(target_node_dependency_list)):
            if (target_node_dependency_list[child_index] != -1) \
                    and (child_index != node_id) \
                    and ((target_node_dependency_list[child_index] & mandatory_dependency) == mandatory_dependency):
                mandatory_child_dependency_list.append(child_index)

        return mandatory_child_dependency_list

    def get_from_parent_dependency_list(self, node_id) -> list:

        from_parent_dependency_list = []

        for parent_index in range(len(self.__dependencyTwoDimensionList)):
            if (parent_index != node_id) and (self.__dependencyTwoDimensionList[parent_index][node_id] != -1):
                from_parent_dependency_list.append(parent_index)

        return from_parent_dependency_list

    def has_mandatory_child_node(self, node_id) -> bool:

        return len(self.get_mandatory_to_child_dependency_list(node_id)) > 0
