from Generate.var import *
def expression_list(node, array_id="", for_array: bool = False, index_depth=0, return_list=False, for_procedure_call: bool = False, procedure_id: str = "", ardepth=0):
    global symbolTable,domain
    """
    expression_list -> expression_list , expression | expression
    """
    assert node['p_type'] == "expression_list"
    assert len(node['info']["expressions"]) > 0
    result = ""
    result_list = []  # for printf format string
    if for_array == True:
        assert return_list == False
        if len(node['info']["expressions"]) == 1:
            if isinstance(array_id, str):
                func_variable_list = []
                if domain[-1] == "main":
                    func_variable_list += symbolTable["varTable"]
                else:
                    func_variable_list += symbolTable["varTable"]
                    func_variable_list += get_subFunc(
                        domain[-1])["table"]["variables"]
                array_info = {}
                # print("\narray_id:", array_id)
                for v in func_variable_list:
                    # print(v)
                    if v["id"] == array_id:
                        array_info = v
                assert array_info != {}
            index = expression(node['info']["expressions"][0])
            start_index = array_info['array']["start"][-1-index_depth]
            if index.isdigit():
                index = str(int(index)-start_index)
            else:
                if start_index != 0:
                    index += "-{}".format(str(start_index))
            result += "[{}]".format(index)
        elif len(node['info']["expressions"]) > 1:
            tmp_node = copy.deepcopy(node)
            expressionData = tmp_node['info']["expressions"].pop()
            last_expression = copy.deepcopy(node)
            last_expression['info']["expressions"].clear()
            last_expression['info']["expressions"].append(expressionData)
            tmp = "{}{}".format(
                expression_list(
                    tmp_node, for_array=for_array, array_id=array_id, index_depth=index_depth+1),
                expression_list(last_expression, for_array=for_array, array_id=array_id, index_depth=index_depth))
            result += tmp
    else:
        if len(node['info']["expressions"]) == 1:
            tmp = expression(node['info']["expressions"][0])
            if return_list == True:
                result_list.append(tmp)
            else:
                if for_procedure_call == True:
                    is_ref_list = get_subFunc(procedure_id)["isReference"]
                    # print(is_ref_list)

                    if node['info']["exp_type"] is not None and is_ref_list is not None:
                        if len(node['info']["exp_type"])-1-ardepth < len(is_ref_list) and is_ref_list[len(node['info']["exp_type"])-1-ardepth] == True:
                            result += "&"

                result += tmp

        elif len(node['info']["expressions"]) > 1:
            tmp_node = copy.deepcopy(node)
            expressionData = tmp_node['info']["expressions"].pop()
            if return_list == True:
                result_list.extend(expression_list(
                    tmp_node, for_array=for_array, return_list=return_list))
                result_list.append(expression(expressionData))
            else:
                result += expression_list(tmp_node,
                                                    for_array=for_array, for_procedure_call=for_procedure_call, procedure_id=procedure_id, ardepth=ardepth+1)
                result += ","
                if for_procedure_call == True:
                    is_ref_list = get_subFunc(procedure_id)["isReference"]
                    # print(is_ref_list)
                    if node['info']["exp_type"] is not None and is_ref_list is not None:
                        if len(node['info']["exp_type"])-1-ardepth < len(is_ref_list) and is_ref_list[len(node['info']["exp_type"])-1-ardepth] == True:
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
        assert node["child_nodes"][0], "key missing: simple_expression"
        result += simple_expression(node["child_nodes"][0])
    elif node['p_length'] == 4:
        assert node["child_nodes"][0], "key missing: simple_expression_1"
        assert node['info']["RELOP"], "key missing: RELOP"
        assert node["child_nodes"][1], "key missing: simple_expression_2"
        result += simple_expression(
            node["child_nodes"][0]) + ' '
        if node['info']["RELOP"] == "=":
            result += "=="
        elif node['info']["RELOP"] == "<>":
            result += "!="
        else:
            result += node['info']["RELOP"]
        result += ' ' + \
            simple_expression(node["child_nodes"][1])
    return result

def simple_expression(node):
    """
    simple_expression -> simple_expression addop term | term
    """
    assert node['p_type'] == "simple_expression"
    assert node['p_length'] in [2, 4]
    result = ""
    if node['p_length'] == 2:
        assert node["child_nodes"][0], "key missing: term"
        result += term(node["child_nodes"][0])
    elif node['p_length'] == 4:
        assert node["child_nodes"][0], "key missing: simple_expression"
        assert node['info']["ADDOP"], "key missing: ADDOP"
        assert node["child_nodes"][1], "key missing: term"
        result += simple_expression(node["child_nodes"][0]) + ' '
        if node['info']["ADDOP"].lower() == "or":
            result += "||"
        else:
            result += node['info']["ADDOP"]
        result += ' ' + term(node["child_nodes"][1])
    return result

def term(node):
    """
    term -> term mulop factor | factor
    """
    assert node['p_type'] == "term"
    assert node['p_length'] in [2, 4]
    result = ""
    if node['p_length'] == 2:
        assert ["child_nodes"][0], "key missing: factor"
        result += factor(node["child_nodes"][0])
    elif node['p_length'] == 4:
        assert node["child_nodes"][0], "key missing: term"
        assert node['info']["MULOP"], "key missing: MULOP"
        assert node["child_nodes"][1], "key missing: factor"
        result += term(node["child_nodes"][0]) + ' '
        if node['info']["MULOP"].lower() == "mod":
            result += "%"
        elif node['info']["MULOP"].lower() in ["/", "div"]:
            result += "/"
        elif node['info']["MULOP"].lower() == "and":
            result += "&&"
        else:
            result += node['info']["MULOP"]
        result += ' ' + factor(node["child_nodes"][1])
    return result

def factor(node):
    """
    factor -> num | digits | variable | id ( expression_list ) | ( expression ) | not factor | uminus factor | addop factor
    """
    assert node['p_type'] == "factor"
    assert node['info']["_type"] in ["NUM", "variable", "procedure_id",
                                "expression", "NOT", "UMINUS", "NORMAL"]
    result = ""
    type = node['info']["_type"]
    if type == "NUM":
        result += str(node['info']["NUM"])
    elif type == "variable":
        result += variable(node["child_nodes"][0])[0]
    elif type == "procedure_id":
        result += "{}({})".format(node['info']["ID"],
                                    expression_list(node["child_nodes"][0], procedure_id=node['info']["ID"], for_procedure_call=True))
    elif type == "expression":
        result += "("
        result += expression(node["child_nodes"][0])
        result += ")"
    elif type == "NOT":
        result += "!"
        result += factor(["child_nodes"][0])
    elif type == "UMINUS":
        result += "-"
        result += factor(node["child_nodes"][0])
    elif type == "NORMAL":
        result += factor(node["child_nodes"][0])

    return result

#varible generate
def variable_list(node):
    """
    variable_list -> variable_list , variable | variable
    """
    assert node['p_type'] == "variable_list", "type:{}".format(node['p_type'])
    result = ""
    typelist = []
    assert len(node['info']["variables"]) > 0
    if len(node['info']["variables"]) == 1:
        var, __type = variable(node['info']["variables"][0])
        result += var
        typelist.append(__type)
    elif len(node['info']["variables"]) > 1:
        tmp_node = copy.deepcopy(node)
        variableData = tmp_node['info']["variables"].pop()
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
    if isinstance(node['info']["ID"], list):
        result += '.'.join(node['info']["ID"])
    if isinstance(node['info']["ID"], str):
        if domain[-1] != "main":
            subFunc_table = get_subFunc(domain[-1])
            # for i, j in enumerate(subFunc_table["variables"]):
            # print(domain[-1])
            if subFunc_table["isReference"] != None:
                arnum = len(subFunc_table["isReference"])
                for i in range(arnum):
                    if subFunc_table["varTable"][i]["id"] == node['info']["ID"]:
                        if subFunc_table["isReference"][i] == True:
                            result += "*"
                            pass
                        break
        result += node['info']["ID"]

    result += id_varpart(node["child_nodes"][0], array_id=node['info']["ID"])
    return result, node['info']["var_type"]

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
            node["child_nodes"][0], for_array=True, array_id=array_id)
        return result


def get_subFunc(subfuncId=""):
    global symbolTable
    # print(subfunctoken)
    for i in symbolTable["subFuncTable"]:
        if i["id"] == subfuncId:
            return i
    exit("\"{}\" doesn't exist in symbol table".format(subfuncId))
