import json

from flask import session

import project
from project import create_app
from project.domain.create_file import CreateFile
from project.domain.models import Rule, History
from project.domain.update_rule_description import UpdateRuleDescription
from project.fact_values import FactValue
from project.fact_values.fact_value_type import FactValueType
from project.inference import InferenceEngine, Assessment
from project.nodes import HistoryRecord, LineType
from project.repository import RuleRepository
from project.rule_parser import RuleSetReader, RuleSetScanner
from project.rule_parser.rule_set_parser import RuleSetParser

app = create_app()

rule_prefix_url = 'service/rule/'
inference_prefix_url = 'service/inference/'


@app.route(rule_prefix_url + 'searchRuleByName')
def search_rule_by_name(rule_name: str):  # put application's code here
    return RuleRepository.find_rule_by_rule_name(rule_name)


@app.route(rule_prefix_url + 'findRuleTextByName')
def find_rule_text_by_name(rule_name: str):
    temp_rule = RuleRepository.find_rule_text_by_rule_name(rule_name)
    if temp_rule is not None:
        rule_file = temp_rule.get_the_latest_file()
        return json.loads("{\"ruleText\":\"" + rule_file.decode('ascii') + "\"}")

    return None


@app.route(rule_prefix_url + 'findTheLatestRuleFileByName')
def get_the_latest_rule_file_by_name(rule_name):
    return RuleRepository.find_rule_text_by_rule_name(rule_name).get_the_latest_file()


@app.route(rule_prefix_url + 'findTheLatestRuleHistoryByName')
def get_the_latest_rule_history_by_name(rule_name):
    temp_rule = RuleRepository.find_rule_by_rule_name(rule_name)
    if temp_rule is not None:
        return temp_rule.get_the_latest_history()
    return None


@app.route(rule_prefix_url + 'findAllRules')
def get_all_rules():
    return RuleRepository.find_all_rules()


@app.route(rule_prefix_url + 'updateRule', method=['POST'])
def update_rule(update_rule: UpdateRuleDescription):
    old_rule_name = update_rule.get_old_rule_name()
    new_rule_name = update_rule.get_new_rule_name()
    new_rule_category = update_rule.get_new_category()
    RuleRepository.update_rule_name_and_category(old_rule_name, new_rule_name, new_rule_category)
    rule_from_database = RuleRepository.find_rule_by_rule_name(new_rule_name)

    if rule_from_database is not None:
        return json.loads(
            '{"newRuleName":' + rule_from_database.name + ", \"newCategory\": \"" + rule_from_database.category + "\"}")

    return None


@app.route(rule_prefix_url + 'createNewRule', method=['POST'])
def create_new_rule(new_rule: Rule):
    new_rule_name = new_rule.name
    new_rule_category = new_rule.category
    RuleRepository.create_new_rule(new_rule_name, new_rule_category)

    rule_from_database = RuleRepository.find_rule_by_rule_name(new_rule_name)
    if rule_from_database is not None:
        return json.loads(
            "{\"ruleName\":\"" + rule_from_database.name + "\", \"category\":\"" + rule_from_database.category + "\"}")

    return None


@app.route(rule_prefix_url + 'createFile', method=['POST'])
def create_file(create_file: CreateFile):
    rule_name = create_file.get_rule_name()
    rule_text = create_file.get_rule_text()
    rule_text_byte_array = bytearray(rule_text, 'utf-8')

    rule_id = RuleRepository.find_id_by_name(rule_name)
    RuleRepository.create_rule_file(rule_id, rule_text_byte_array)

    rule_file_from_database = RuleRepository.find_rule_text_by_rule_name(rule_name).get_the_latest_file()

    if rule_file_from_database is not None:
        return json.loads("{\"ruleText\":\"" + rule_file_from_database.files + "\"}")

    return None


@app.route(rule_prefix_url + 'updateHistory', method=['POST'])
def update_history(request_rule: CreateFile):
    inference_engine: InferenceEngine = session.get('inferenceEngine')
    working_memory: dict = inference_engine.get_assessment_state().get_working_memory()

    rule_name = request_rule.get_rule_name()
    rule_history: History = get_the_latest_rule_history_by_name(rule_name)
    parent_temp_history: json = json.loads("{}")

    if rule_history is not None:
        target_history: json = rule_history.history
        record_list = list()

        filtered_list = list()

        # this is for the case of rules in workingMemory.
        # Hence, the rules should be checked if it is in history list or not.
        # if it is in the history list then history record should be fetched and update record according to
        # the workingMemory,
        # and if is not in the history list then create a new record, and insert the new record into the history list.
        for each_rule_key in working_memory.keys():
            for history_key in target_history:
                if history_key == each_rule_key:
                    filtered_list.append({history_key: target_history[history_key]})

            record = HistoryRecord()
            record.set_name(each_rule_key)

            if len(filtered_list) > 0:
                record.set_false_count(int(filtered_list[0].get('false')))
                record.set_true_count(int(filtered_list[0].get('true')))

            fact_value: FactValue = working_memory[each_rule_key]

            if fact_value.get_value_type() == FactValueType.BOOLEAN:
                record.set_type(str(fact_value.get_value_type()).lower())
                if fact_value.get_value() is True:
                    record.increment_true_count()
                else:
                    record.increment_false_count()
            else:
                record.set_type(str(fact_value.get_value_type()).lower())
                record.increment_true_count()

            record_list.append(record)

        # this is for the case of rules that are not Boolean type and is in history list but not currently being asked.
        # Hence, the record for the rule should be incremented for 'FALSE' due to it is equivalent to 'FALSE' case
        # for propositional rules.

        for key, history_item in target_history.items():
            if key not in working_memory.keys():
                if str(history_item['type']).lower() != 'boolean':
                    record = HistoryRecord()
                    record.set_name(key)
                    record.set_false_count(int(history_item['false']))
                    record.set_true_count(int(history_item['true']))
                    record.increment_false_count()
                    record_list.append(record)

                else:
                    record = HistoryRecord()
                    record.set_name(key)
                    record.set_false_count(int(history_item['false']))
                    record.set_true_count(int(history_item['true']))
                    record_list.append(record)

        for each_record in record_list:
            temp_history = json.loads("{}")
            temp_history["true"] = str(each_record.get_true_count())
            temp_history["false"] = str(each_record.get_false_count())
            temp_history["type"] = each_record.get_type()

            parent_temp_history[each_record.get_name()] = temp_history
    else:  # case of the rule file has never been used so that there is a no record history.
        for work_item in working_memory.keys():
            fact_value: FactValue = working_memory.get(work_item)
            temp_history: json = json.loads("{}")

            if fact_value.get_value_type() == FactValueType.BOOLEAN:
                if fact_value.get_value() is True:
                    temp_history["true"] = "1"
                    temp_history["false"] = "0"
                else:
                    temp_history["true"] = "0"
                    temp_history["false"] = "1"
            else:
                temp_history["true"] = "1"
                temp_history["false"] = "0"

            temp_history["type"] = str(working_memory.get(work_item).get_value_type())
            parent_temp_history[work_item] = temp_history

    RuleRepository.create_rule_history(RuleRepository.find_id_by_name(rule_name), parent_temp_history)

    return json.loads("\"update\":\"done\"")


@app.route(inference_prefix_url + 'viewSummary')
def view_summary():
    inference_engine: InferenceEngine = session.get('inferenceEngine')
    temp_summary_list = list()
    temp_assessment_state = inference_engine.get_assessment_state()
    temp_working_memory = temp_assessment_state.get_working_memory()
    for summary_item in temp_assessment_state.get_summary_list():
        summary_json = json.loads("{}")
        summary_json['nodeText'] = summary_item
        summary_json['nodeValue'] = str(temp_working_memory.get(summary_item).get_value())
        temp_summary_list.append(summary_json)

    # following lines are to transfer all possible left over value from editing answers process from workingMemory
    # to summary list in GUI

    for each_key in temp_working_memory.keys():
        if each_key not in inference_engine.get_assessment_state().get_summary_list():
            summary_json = json.loads("{}")
            summary_json['nodeText'] = each_key
            summary_json['nodeValue'] = str(temp_working_memory.get(each_key).get_value())
            temp_summary_list.append(summary_json)

    return temp_summary_list


# TODO: this API still needs further work
@app.route(inference_prefix_url + 'editAnswer', method=['POST'])
def edit_answer(question: json):
    inference_engine: InferenceEngine = session.get('inferenceEngine')
    assessment: Assessment = session.get('assessment')

    question_name = question['question']
    inference_engine.edit_answer(question_name)
    object_node: json = json.loads("{}")
    questions_and_answers: json = json.loads("\"workingMemory\":[]")
    temp_working_memory = inference_engine.get_assessment_state().get_working_memory()
    for each_key in temp_working_memory.keys():
        sub_object_node = json.loads("{}")
        sub_object_node['questionText'] = each_key
        sub_object_node['answer'] = str(temp_working_memory.get(each_key))
        sub_object_node['answerValueType'] = str(temp_working_memory.get(each_key).get_value_type())
        questions_and_answers['workingMemory'].append(sub_object_node)

    if temp_working_memory.get(assessment.get_goal_node().get_node_name()) is None \
            or inference_engine.get_assessment_state().all_mandatory_node_determined() is False:
        object_node['hasMoreQuestion'] = 'true'
    else:
        goal_node_name = assessment.get_goal_node().get_node_name()
        object_node['hasMoreQuestion'] = 'false'
        object_node['goalRuleName'] = goal_node_name
        object_node['goalRuleValue'] = str(temp_working_memory.get(goal_node_name).get_value())
        object_node['goalRuleType'] = \
            str(inference_engine.find_type_of_element_to_be_asked(assessment.get_goal_node()).get(
                goal_node_name)).lower()

    return object_node


@app.route(inference_prefix_url + 'feedAnswer', method=['POST'])
def feed_answer(answers: json):
    inference_engine: InferenceEngine = session.get('inferenceEngine')
    assessment: Assessment = session.get('assessment')

    first_key_and_value = list(answers.items())[0]

    question_name: str = first_key_and_value[0]
    answer_entry: json = first_key_and_value[1]

    from project.fact_values import FactValueType
    fact_value_type: FactValueType = FactValueType[str(answer_entry['type']).upper()]

    if assessment.get_node_to_be_asked().get_line_type() == LineType.ITERATE:
        inference_engine.feed_answer_to_node(assessment.get_aux_node_to_be_asked(), question_name,
                                             str(answer_entry['answer']), fact_value_type,
                                             assessment)
    else:
        inference_engine.feed_answer_to_node(assessment.get_node_to_be_asked(), question_name,
                                             str(answer_entry['answer']), fact_value_type,
                                             assessment)

    object_node = json.loads("{}")
    if inference_engine.get_assessment_state().get_working_memory().get(
            assessment.get_goal_node().get_node_name() is None) \
            or inference_engine.get_assessment_state().all_mandatory_node_determined() is not True:
        object_node['hasMoreQuestion'] = 'true'
    else:
        goal_node_name: str = assessment.get_goal_node().get_node_name()
        object_node['hasMoreQuestion'] = 'false'
        object_node['goalRuleName'] = goal_node_name
        object_node['goalRuleValue'] = str(
            inference_engine.get_assessment_state().get_working_memory().get(goal_node_name).get_value())
        object_node['goalRuleType'] = str(
            inference_engine.find_type_of_element_to_be_asked(assessment.get_goal_node()).get(goal_node_name)).lower()

    return object_node


@app.route(inference_prefix_url + 'getNextQuestion')
def get_next_question(rule_name: str):
    inference_engine: InferenceEngine = session.get('inferenceEngine')
    if inference_engine is None or inference_engine.get_node_set().get_node_set_name() != rule_name:
        set_inference_engine(rule_name)

    inference_engine: InferenceEngine = session.get('inferenceEngine')
    assessment: Assessment = session.get('assessment')
    next_question_node = inference_engine.get_next_question(assessment)
    if assessment.get_node_to_be_asked().get_line_type() == LineType.ITERATE:
        assessment.set_aux_node_to_be_asked(next_question_node)

    question_fact_value_type_dict: dict = inference_engine.find_type_of_element_to_be_asked(next_question_node)
    questionnaire: list = inference_engine.get_questions_from_node_to_be_asked(next_question_node)
    questionnaire_list = list()
    for question in questionnaire:
        object_node = json.loads("{}")
        object_node['questionText'] = question
        object_node['questionValueType'] = str(question_fact_value_type_dict.get(question)).lower()

        questionnaire_list.append(object_node)

    return questionnaire_list


@app.route(inference_prefix_url + 'setInferenceEngine')
def set_inference_engine(rule_name: str):
    inference_engine = InferenceEngine()
    rule_text: str = str(get_the_latest_rule_file_by_name(rule_name).files, 'utf-8')
    rule_set_reader = RuleSetReader()
    rule_set_parser = RuleSetParser()
    rule_set_reader.set_file_with_text(rule_text)
    rule_set_scanner = RuleSetScanner(rule_set_reader, rule_set_parser)
    rule_set_scanner.scan_rule_set()
    rule_set_scanner.establish_node_set()

    inference_engine.set_node_set(rule_set_parser.get_node_set())
    inference_engine.get_node_set().set_node_set_name(rule_name)

    assessment = Assessment()
    assessment.set_assessment(rule_set_parser.get_node_set(),
                              rule_set_parser.get_node_set().get_sorted_node_list()[0].get_node_name())
    inference_engine.set_assessment(assessment)
    session['inferenceEngine'] = inference_engine
    session['assessment'] = assessment
    object_node = json.loads("{}")
    object_node['InferenceEngine'] = 'created'

    return object_node


@app.route(inference_prefix_url + "setMachineLearningInferenceEngine")
def set_machine_learning_inference_engine(rule_name):
    inference_engine = InferenceEngine()
    rule_text: str = str(get_the_latest_rule_file_by_name(rule_name).files, 'utf-8')
    rule_set_reader = RuleSetReader()
    rule_set_parser = RuleSetParser()

    rule_set_reader.set_file_with_text(rule_text)
    rule_set_scanner = RuleSetScanner(rule_set_reader, rule_set_parser)
    rule_set_scanner.scan_rule_set()

    rule_history: History = get_the_latest_rule_history_by_name(rule_name)
    history_dict = dict()
    if rule_history is not None:
        history_dict = rule_history.get_history_dict()
    else:
        history_dict = None

    rule_set_scanner.establish_node_set(history_dict)
    inference_engine.set_node_set(rule_set_parser.get_node_set())
    inference_engine.get_node_set().set_node_set_name(rule_name)

    assessment = Assessment()
    assessment.set_assessment(rule_set_parser.get_node_set(),
                              rule_set_parser.get_node_set().get_sorted_node_list()[0].get_node_name())
    inference_engine.set_assessment(assessment)
    session['inferenceEngine'] = inference_engine
    session['assessment'] = assessment

    object_node = json.loads("{}")
    object_node['InferenceEngine'] = 'created'

    return object_node


if __name__ == '__main__':
    app.run()
