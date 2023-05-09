import copy
import json

domain = []  # 作用域栈
symbolTable = {}  # 符号表

def Ptype(node):
    '''
    type : basic_type
        | ARRAY LBRACKET period RBRACKET OF basic_type
        | RECORD multype END
    '''
    assert node['p_type'] == 'type'
    result = ''
    if node['info']["_type"] == "ARRAY":
        result += basic_type(node['child_nodes'][1])
    else:
        result += basic_type(node['info']["_type"])
    return result

def basic_type(node):
    '''
    basic_type : INTEGER
                | REAL
                | BOOLEAN
                | CHAR
    '''
    global headFile
    assert node['p_type'] == "basic_type"
    if node["info"]["_type"] == "INTEGER":
        return "int"
    if node["info"]["_type"] == "REAL":
        return "float"
    if node["info"]["_type"] == "BOOLEAN":
        return "bool"
    if node["info"]["_type"] == "CHAR":
        return "char"


def idlst(node):
    '''
    idlist : idlist COM ID | ID
    '''
    assert node['p_type'] == "idlist"
    result = node['info']['id_l']
    return result

def const_declarations(node):
    '''
    const_declarations : CONST const_declaration SEMICOLON
                        | empty
    '''
    result = ""
    if 'p_type' in node.keys():
        assert node['p_type'] == "const_declarations"
        result += const_declaration(node["child_nodes"][0])
        result += '\n'
    return result

def const_declaration(node):
    '''
    const_declaration : const_declaration SEMICOLON ID EQUAL const_value
                        | ID EQUAL const_value
    '''
    assert node['p_type'] == "const_declaration"
    result = ""
    for it in node['info']["values"]:
        result += 'const '
        if it["const_value"]['info']["_type"] == "NUM":
            if isinstance(it["const_value"]['info']["value"], int):
                result += 'int '
            if isinstance(it["const_value"]['info']["value"], float):
                result += 'float '
        if it["const_value"]['info']["_type"] == "LETTER":
            result += 'char '
        result += it["ID"] + ' = '
        result += const_value(it["const_value"])
        result += ';'
    return result

def const_value(node):
    '''
    const_value : NUM | QUO LETTER QUO
    '''
    assert node['p_type'] == "const_value"
    result = ''
    if node['info']["_type"] == "NUM":
        result += str(node['info']["value"])
    if node['info']["_type"] == "LETTER":
        result += '\'' + node['info']["value"] + '\''
    return result

def var_declarations(node):
    '''
    var_declarations : VAR var_declaration SEMICOLON
                    |
    '''
    result = ''
    if 'p_type' in node.keys():
        assert node['p_type'] == "var_declarations"
        result += var_declaration(node["child_nodes"][0])
        result += '\n'
    return result

def var_declaration(node):
    '''
    var_declaration : var_declaration SEMICOLON idlist COLON type
                    | idlist COLON type
    '''
    assert node['p_type'] == "var_declaration"
    result = ''
    for it in node['info']["values"]:
        if it['type']['info']["_type"] == "ARRAY":
            result += Ptype(it['type'])
            result += ' '
            range = period(it['type']["child_nodes"][0])
            idlist = idlst(it["id_l"])
            for id in idlist:
                result += id
                result += range
                result += ',' if id != idlist[-1] else ';'
        else:
            result += Ptype(it['type'])
            result += ' '
            idlist = idlst(it["id_l"])
            for id in idlist:
                result += id
                result += ',' if id != idlist[-1] else ';'
    return result
    

def period(node):
    '''
    period : period COM DIGITS POINTTO DIGITS
        | DIGITS POINTTO DIGITS
    '''
    assert node['p_type'] == "period"
    result = ''
    for period in node['info']["values"]:
        size = period["end"]-period["start"]+1
        result += '['+str(size)+']'
    return result