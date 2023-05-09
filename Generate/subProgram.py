from Generate.statement import *
def subprogram_declarations(node):
    '''
    subprogram_declarations : subprogram_declarations subprogram SEMICOLON
                            |
    '''
    result = ''
    if node is not None:
        assert node['p_type'] == "subprogram_declarations"
        for it in node['info']["subprograms"]:
            result += subprogram(it)
            result += '\n'
    return result

def subprogram(node):
    '''
    subprogram : subprogram_head SEMICOLON subprogram_body
    '''
    assert node['p_type'] == "subprogram"
    result = ''
    result += subprogram_head(node["child_nodes"][0])
    result += subprogram_body(node["child_nodes"][1])
    domain.pop()
    return result

def subprogram_head(node):
    '''
    subprogram_head :  seen_PROCEDURE ID formal_parameter
                    | FUNCTION seen_FUNCTION ID formal_parameter COLON basic_type
    '''
    global domain
    assert node['p_type'] == "subprogram_head"
    result = ''
    if node['info']["_type"] == 'PROCEDURE':
        result += 'void '
    else:
        result += basic_type(node["child_nodes"][1]) + ' '
    result += node['info']["ID"]
    domain += [node['info']["ID"]]
    result += formal_parameter(node["child_nodes"][0])
    return result

def formal_parameter(node):
    '''
    formal_parameter : LPAREN parameter_list RPAREN
                    |
    '''
    result = ''
    result += '('
    if 'p_type' in node.keys():
        assert node['p_type'] == "formal_parameter"
        result += parameter_list(node["child_nodes"][0])
    result += ')'
    return result

def parameter_list(node):
    '''
    parameter_list : parameter_list SEMICOLON parameter
                | parameter
    '''
    assert node['p_type'] == "parameter_list"
    result = ''
    for it in node['info']["parameters"]:
        result += parameter(it)
        result += ','if it != node['info']["parameters"][-1] else ''
    return result

def parameter(node):
    '''
    parameter : var_parameter
            | value_parameter
    '''
    assert node['p_type'] == "parameter"
    result = ''
    if node['info']["value"]['p_type'] == "value_parameter":
        result += value_parameter(node['info']["value"])
    else:
        result += var_parameter(node['info']["value"])
    return result

def var_parameter(node):
    '''
    var_parameter : VAR value_parameter
    '''
    assert node['p_type'] == "var_parameter"
    result = ''
    type = basic_type(node["child_nodes"][0]['info']["basic_type"])
    idlist = idlst(node["child_nodes"][0]["child_nodes"][0])
    for id in idlist:
        result += type + '* '
        result += id
        result += ',' if id != idlist[-1] else ''
    return result

def value_parameter(node):
    '''
    value_parameter : idlist COLON basic_type
    '''
    assert node['p_type'] == "value_parameter"
    result = ''
    type = basic_type(node["child_nodes"][1])
    idlist = idlst(node["child_nodes"][0])
    for id in idlist:
        result += type + ' '
        result += id
        result += ',' if id != idlist[-1] else ''
    return result

def subprogram_body(node):
    '''
    subprogram_body : const_declarations var_declarations compound_statement
    '''
    assert node['p_type'] == "subprogram_body"
    result = ""
    result += '{'
    result += const_declarations(node["child_nodes"][0])
    result += var_declarations(node["child_nodes"][1])
    result += compound_statement(node["child_nodes"][2])
    result += '}'
    return result
