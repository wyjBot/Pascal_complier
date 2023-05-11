from Generate.expression import *
def compound_statement(node):
    '''
    compound_statement -> begin statement_list end
    compound_statement -> statement_list
    '''
    assert node['p_type'] == "compound_statement"
    result = ""
    result += statement_list(node["child_nodes"][0])
    return result

def statement_list(node):
    '''
    statement_list -> statement_list ; statement | statement
    statement_list -> statement_list statement | statement
    '''
    assert node['p_type'] == "statement_list", "type:{}".format(node['p_type'])
    result = ""
    assert len(node['info']["statements"]) > 0
    if len(node['info']["statements"]) == 1:
        result += statement(node['info']["statements"][0])
    elif len(node['info']["statements"]) > 1:
        tmp_node = copy.deepcopy(node)
        state = tmp_node['info']["statements"].pop()
        result += statement_list(tmp_node)
        # result += " "
        result += statement(state)
    return result

def statement(node):
    '''
    Pascal:                                                     C:
    statement ->                                                statement ->
    variable assignop expression                                variable = expression
    | procedure_call                                            | procedure_call
    | compound_statement                                        | compound_statement
    | if expression then statement else_part                    | if(expression){statement}else_part
    | for id assignop expression to expression do statement     | for(id=expression;id<expression;id++){statement}
    | read ( variable_list )                                    | scanf("format_string",var1,var2)
    | write ( expression_list )                                 | printf("format_string",var1,var2)
    | while expression do statement                             | while(expression){statement}
    | ε                                                         | ε
    '''
    global domain
    if len(node) == 0:
        return ""
    assert node['info']["_type"] in ["variable", "procedure_call", "compound_statement",
                                "IF", "FOR", "READ", "WRITE", "WHILE"], "_type:{}".format(node['info']["_type"])
    format_tamap = {"INTEGER": "%d",
                        "REAL": "%f", "BOOLEAN": "%d", "CHAR": "%c"}
    type = node['info']["_type"]
    result = ""
    if type == "variable":
        result += variable(node["child_nodes"][0])[0]
        if result == domain[-1]:
            # in function
            result = "return "
        else:
            result += " = "
        result += expression(node["child_nodes"][1])
    elif type == "procedure_call":
        result += procedure_call(node["child_nodes"][0])
    elif type == "compound_statement":
        result += compound_statement(node["child_nodes"][0])
    elif type == "IF":
        result += "if("
        result += expression(node["child_nodes"][0])
        result += ")"
        result += "{"
        result += statement(node["child_nodes"][1])
        result += "}"
        result += else_part(node["child_nodes"][2])
    elif type == "FOR":
        result += "for("
        result += node['info']["ID"]
        result += " = "
        result += expression(node["child_nodes"][0])
        result += ";"
        result += node['info']["ID"]
        result += " < "
        result += expression(node["child_nodes"][1])
        result += ";"
        result += node['info']["ID"]
        result += "++"
        result += "){"
        result += statement(node["child_nodes"][2])
        result += "}"
    elif type == "READ":
        var, __type = variable_list(node["child_nodes"][0])
        var = var.split(",")
        assert len(var) == len(__type)
        assert len(var) > 0
        format_string = ""
        var_string = ""
        for i in range(len(var)):
            format_string += "{}".format(format_tamap[__type[i]])
            var_string += "&{},".format(var[i])
        var_string = var_string[0: -1]
        result += "scanf(\"{}\",{})".format(format_string, var_string)
    elif type == "WRITE":
        var = expression_list(
            node["child_nodes"][0], return_list=True)
        __type = node["child_nodes"][0]["info"]["exp_type"]
        assert len(var) == len(__type), len(var)
        assert len(var) > 0
        format_string = ""
        var_string = ""
        for i in range(len(var)):
            format_string += "{}\\n".format(format_tamap[__type[i]])
            var_string += "{},".format(var[i])
        var_string = var_string[0: -1]
        result += "printf(\"{}\",{})".format(format_string, var_string)
    if type in ["variable", "procedure_call", "READ", "WRITE"]:
        result += ";"
    return result

def procedure_call(node):
    """
    procedure_call -> id | id ( expression_list )
    """
    assert node['p_type'] == "procedure_call"
    result = ""
    result += node['info']["ID"]+'('
    if node['p_length'] == 5:
        result += "{}".format(expression_list(
            node["child_nodes"][0], for_procedure_call=True, procedure_id=node['info']["ID"]))
    result += ')'
    return result

def else_part(node):
    """
    else_part -> else statement | ε
    """
    assert node['p_type'] == "else_part"
    result = ""
    if node['p_length'] == 3:
        result += "else{"
        result += statement(node["child_nodes"][0])
        result += "}"
    return result
