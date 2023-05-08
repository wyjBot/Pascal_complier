from expression import *
def compound_statement(node):
    '''
    compound_statement -> begin statement_list end
    compound_statement -> statement_list
    '''
    assert node['p_type'] == "compound_statement"
    result = ""
    result += statement_list(node["statement_list"])
    return result

def statement_list(node):
    '''
    statement_list -> statement_list ; statement | statement
    statement_list -> statement_list statement | statement
    '''
    assert node['p_type'] == "statement_list", "type:{}".format(node['p_type'])
    result = ""
    assert len(node["statements"]) > 0
    if len(node["statements"]) == 1:
        result += statement(node["statements"][0])
    elif len(node["statements"]) > 1:
        tmp_node = copy.deepcopy(node)
        state = tmp_node["statements"].pop()
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
    if(node == None):
        return ""
    assert node["_type"] in ["variable", "procedure_call", "compound_statement",
                                "IF", "FOR", "READ", "WRITE", "WHILE"], "_type:{}".format(node["_type"])
    format_tamap = {"INTEGER": "%d",
                        "REAL": "%f", "BOOLEAN": "%d", "CHAR": "%c"}
    type = node["_type"]
    result = ""
    if type == "variable":
        result += variable(node["variable"])[0]
        if result == domain[-1]:
            # in function
            result = "return "
        else:
            result += " = "
        result += expression(node["expression"])
    elif type == "procedure_call":
        result += procedure_call(node["procedure_call"])
    elif type == "compound_statement":
        result += compound_statement(node["compound_statement"])
    elif type == "IF":
        result += "if("
        result += expression(node["expression"])
        result += ")"
        result += "{"
        result += statement(node["statement"])
        result += "}"
        result += else_part(node["else_part"])
    elif type == "FOR":
        result += "for("
        result += node["ID"]
        result += " = "
        result += expression(node["expression"])
        result += ";"
        result += node["ID"]
        result += " < "
        result += expression(node["to_expression"])
        result += ";"
        result += node["ID"]
        result += "++"
        result += "){"
        result += statement(node["statement"])
        result += "}"
    elif type == "READ":
        var, __type = variable_list(node["variable_list"])
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
            node["expression_list"], return_list=True)
        __type = node["expression_list"]["__type"]
        assert len(var) == len(__type), len(var)
        assert len(var) > 0
        format_string = ""
        var_string = ""
        for i in range(len(var)):
            format_string += "{}: {}\\n".format(var[i],
                                                format_tamap[__type[i]])
            var_string += "{},".format(var[i])
        var_string = var_string[0: -1]
        result += "printf(\"{}\",{})".format(format_string, var_string)
    elif type == "WHILE":
        result = "while({}){{{}}}".format(expression(node["expression"]),
                                            statement(node["statement"]))
    if type in ["variable", "procedure_call", "READ", "WRITE"]:
        result += ";"
    return result

def procedure_call(node):
    """
    procedure_call -> id | id ( expression_list )
    """
    assert node['p_type'] == "procedure_call"
    result = ""
    result += node["ID"]+'('
    if node['p_length'] == 5:
        result += "{}".format(expression_list(
            node["expression_list"], for_procedure_call=True, procedure_id=node["ID"]))
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
        result += statement(node["statement"])
        result += "}"
    return result
