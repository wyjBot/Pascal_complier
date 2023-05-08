from var import *
def expression_list(node, array_id="", for_array: bool = False, index_depth=0, return_list=False, for_procedure_call: bool = False, procedure_id: str = "", ardepth=0):
    global symbolTable,domain
    """
    expression_list -> expression_list , expression | expression
    """
    assert node['p_type'] == "expression_list"
    assert len(node["expressions"]) > 0
    result = ""
    result_list = []  # for printf format string
    if for_array == True:
        assert return_list == False
        if len(node["expressions"]) == 1:
            if isinstance(array_id, str):
                func_variable_list = []
                if domain[-1] == "main":
                    func_variable_list += symbolTable["variables"]
                else:
                    func_variable_list += symbolTable["variables"]
                    func_variable_list += get_subFunc(
                        domain[-1])["table"]["variables"]
                array_info = {}
                # print("\narray_id:", array_id)
                for v in func_variable_list:
                    # print(v)
                    if v["token"] == array_id:
                        array_info = v
                assert array_info != {}
            elif isinstance(array_id, list):  # for record
                search_area = symbolTable["variables"]
                for i in search_area:
                    if i["token"] == array_id[0]:
                        search_area = i["recordTable"]["variables"]
                        break

                for i in range(1, len(array_id)):
                    target = array_id[i]  # for b c in a.b.c
                    for j in search_area:
                        if target in j["token"]["ids"]:
                            if j["recordTable"] == None:
                                array_info = j
                                break
                            else:
                                search_area = j["recordTable"]["variables"]
                                break
            index = expression(node["expressions"][0])
            start_index = array_info["start"][-1-index_depth]
            if index.isdigit():
                index = str(int(index)-start_index)
            else:
                if start_index != 0:
                    index += "-{}".format(str(start_index))
            result += "[{}]".format(index)
        elif len(node["expressions"]) > 1:
            tmp_node = copy.deepcopy(node)
            expressionData = tmp_node["expressions"].pop()
            last_expression = copy.deepcopy(node)
            last_expression["expressions"].clear()
            last_expression["expressions"].append(expression)
            tmp = "{}{}".format(
                expression_list(
                    tmp_node, for_array=for_array, array_id=array_id, index_depth=index_depth+1),
                expression_list(last_expression, for_array=for_array, array_id=array_id, index_depth=index_depth))
            result += tmp
    else:
        if len(node["expressions"]) == 1:
            tmp = expression(node["expressions"][0])
            if return_list == True:
                result_list.append(tmp)
            else:
                if for_procedure_call == True:
                    is_ref_list = get_subFunc(procedure_id)[
                        "table"]["references"]
                    # print(is_ref_list)

                    if node["__type"] is not None and is_ref_list is not None:
                        if len(node["__type"])-1-ardepth < len(is_ref_list) and is_ref_list[len(node["__type"])-1-ardepth] == True:
                            result += "&"

                result += tmp

        elif len(node["expressions"]) > 1:
            tmp_node = copy.deepcopy(node)
            expressionData = tmp_node["expressions"].pop()
            if return_list == True:
                result_list.extend(expression_list(
                    tmp_node, for_array=for_array, return_list=return_list))
                result_list.append(expression(expression))
            else:
                result += expression_list(tmp_node,
                                                    for_array=for_array, for_procedure_call=for_procedure_call, procedure_id=procedure_id, ardepth=ardepth+1)
                result += ","
                if for_procedure_call == True:
                    is_ref_list = get_subFunc(procedure_id)[
                        "table"]["references"]
                    # print(is_ref_list)
                    if node["__type"] is not None and is_ref_list is not None:
                        if len(node["__type"])-1-ardepth < len(is_ref_list) and is_ref_list[len(node["__type"])-1-ardepth] == True:
                            result += "&"
                result += expression(expressionData)
    if return_list == True:
        return result_list
    return result

def expression(node):
    """
    expression -> simple_expression relop simple_expression | simple_expression | simple_expression equal simple_expression
    """
    assert node['p_type'] == "expression"
    assert node['p_length'] in [2, 4]
    result = ""
    if node['p_length'] == 2:
        assert node["simple_expression"], "key missing: simple_expression"
        result += simple_expression(node["simple_expression"])
    elif node['p_length'] == 4:
        assert node["simple_expression_1"], "key missing: simple_expression_1"
        assert node["RELOP"], "key missing: RELOP"
        assert node["simple_expression_2"], "key missing: simple_expression_2"
        result += simple_expression(
            node["simple_expression_1"]) + ' '
        if node["RELOP"] == "=":
            result += "=="
        elif node["RELOP"] == "<>":
            result += "!="
        else:
            result += node["RELOP"]
        result += ' ' + \
            simple_expression(node["simple_expression_2"])
    return result

def simple_expression(node):
    """
    simple_expression -> simple_expression addop term | term
    """
    assert node['p_type'] == "simple_expression"
    assert node['p_length'] in [2, 4]
    result = ""
    if node['p_length'] == 2:
        assert node["term"], "key missing: term"
        result += term(node["term"])
    elif node['p_length'] == 4:
        assert node["simple_expression"], "key missing: simple_expression"
        assert node["ADDOP"], "key missing: ADDOP"
        assert node["term"], "key missing: term"
        result += simple_expression(node["simple_expression"]) + ' '
        if node["ADDOP"].lower() == "or":
            result += "||"
        else:
            result += node["ADDOP"]
        result += ' ' + term(node["term"])
    return result

def term(node):
    """
    term -> term mulop factor | factor
    """
    assert node['p_type'] == "term"
    assert node['p_length'] in [2, 4]
    result = ""
    if node['p_length'] == 2:
        assert node["factor"], "key missing: factor"
        result += factor(node["factor"])
    elif node['p_length'] == 4:
        assert node["term"], "key missing: term"
        assert node["MULOP"], "key missing: MULOP"
        assert node["factor"], "key missing: factor"
        result += term(node["term"]) + ' '
        if node["MULOP"].lower() == "mod":
            result += "%"
        elif node["MULOP"].lower() in ["/", "div"]:
            result += "/"
        elif node["MULOP"].lower() == "and":
            result += "&&"
        else:
            result += node["MULOP"]
        result += ' ' + factor(node["factor"])
    return result

def factor(node):
    """
    factor -> num | digits | variable | id ( expression_list ) | ( expression ) | not factor | uminus factor | addop factor
    """
    assert node['p_type'] == "factor"
    assert node["_type"] in ["NUM", "variable", "procedure_id",
                                "expression", "NOT", "UMINUS", "NORMAL"]
    result = ""
    type = node["_type"]
    if type == "NUM":
        result += str(node["NUM"])
    elif type == "variable":
        result += variable(node["variable"])[0]
    elif type == "procedure_id":
        result += "{}({})".format(node["ID"],
                                    expression_list(node["expression_list"], procedure_id=node["ID"], for_procedure_call=True))
    elif type == "expression":
        result += "("
        result += expression(node["expression"])
        result += ")"
    elif type == "NOT":
        result += "!"
        result += factor(node["factor"])
    elif type == "UMINUS":
        result += "-"
        result += factor(node["factor"])
    elif type == "NORMAL":
        result += factor(node["factor"])

    return result

#varible generate
def variable_list(node):
    """
    variable_list -> variable_list , variable | variable
    """
    assert node['p_type'] == "variable_list", "type:{}".format(node['p_type'])
    result = ""
    typelist = []
    assert len(node["variables"]) > 0
    if len(node["variables"]) == 1:
        var, __type = variable(node["variables"][0])
        result += var
        typelist.append(__type)
    elif len(node["variables"]) > 1:
        tmp_node = copy.deepcopy(node)
        variableData = tmp_node["variables"].pop()
        var, __type = variable_list(tmp_node)
        typelist.extend(__type)
        result += var
        result += ","
        var, __type = variable(variableData)
        result += var
        typelist.append(__type)
    return result, typelist

def variable(node, reference_judge=True):
    global domain
    """
    variable -> id id_varpart
    """
    assert node['p_type'] == "variable"
    result = ""
    if isinstance(node["ID"], list):
        result += '.'.join(node["ID"])
    if isinstance(node["ID"], str):
        if domain[-1] != "main":
            subFunc_table = get_subFunc(domain[-1])["table"]
            # for i, j in enumerate(subFunc_table["variables"]):
            # print(domain[-1])
            if subFunc_table["references"] != None:
                arnum = len(subFunc_table["references"])
                for i in range(arnum):
                    if subFunc_table["variables"][i]["token"] == node["ID"]:
                        if subFunc_table["references"][i] == True:
                            result += "*"
                            pass
                        break
        result += node["ID"]

    result += id_varpart(node["id_varpart"], array_id=node["ID"])
    return result, node["__type"]

def id_varpart(node, array_id=""):
    """
    id_varpart -> [ expression_list ] | ε       #[1,2,3]
    id_varpart -> expression_list | ε           #[1][2][3]
    """
    result = ""
    if node is None:
        return result
    else:
        assert node['p_type'] == "id_varpart"
        result += expression_list(
            node["expression_list"], for_array=True, array_id=array_id)
        return result


def get_subFunc(subfunctoken=""):
    global symbolTable
    # print(subfunctoken)
    for i in symbolTable["subFunc"]:
        if i["token"] == subfunctoken:
            return i
    exit("\"{}\" doesn't exist in symbol table".format(subfunctoken))
