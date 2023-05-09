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
    assert node['p_type'] == 'p_type'
    result = ''
    if node["_type"] == "ARRAY":
        result += basic_type(node["basic_type"])
    elif node["_type"] == "RECORD":
        pass
    else:
        result += basic_type(node["_type"])
    return result



def multype(node):
    '''
    multype : multype idlist COLON type SEMICOLON
            | idlist COLON type SEMICOLON
    '''
    assert node['p_type'] == "multype"
    result = ''
    for it in node["values"]:
        if it['p_type']["_type"] == "ARRAY":
            result += Ptype(it['p_type'])
            result += ' '
            range = period(it['p_type']["period"])
            idlist = idlst(it["idlist"])
            for id in idlist:
                result += id
                result += range
                result += ',' if id != idlist[-1] else ';'
        elif it['p_type']["_type"] == "RECORD":
            result += 'struct ' + '{'
            result += multype(it['p_type']["multype"])
            result += '}'
            idlist = idlst(it["idlist"])
            for id in idlist:
                result += id
                result += ',' if id != idlist[-1] else ';'
        else:
            result += Ptype(it['p_type'])
            result += ' '
            idlist = idlst(it["idlist"])
            for id in idlist:
                result += id
                result += ',' if id != idlist[-1] else ';'
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
    if node["_type"] == "INTEGER":
        return "int"
    if node["_type"] == "REAL":
        return "float"
    if node["_type"] == "BOOLEAN":
        return "bool"
    if node["_type"] == "CHAR":
        return "char"


def idlst(node):
    '''
    idlist : idlist COM ID | ID
    '''
    assert node['p_type'] == "idlist"
    result = node['info']['ids']
    return result

def const_declarations(node):
    '''
    const_declarations : CONST const_declaration SEMICOLON
                        | empty
    '''
    result = ""
    if node is not None:
        assert node['p_type'] == "const_declarations"
        result += const_declaration(node["const_declaration"])
        result += '\n'
    return result

def const_declaration(node):
    '''
    const_declaration : const_declaration SEMICOLON ID EQUAL const_value
                        | ID EQUAL const_value
    '''
    assert node['p_type'] == "const_declaration"
    result = ""
    for it in node["values"]:
        result += 'const '
        if it["const_value"]["_type"] == "NUM":
            if isinstance(it["const_value"]["value"], int):
                result += 'int '
            if isinstance(it["const_value"]["value"], float):
                result += 'float '
        if it["const_value"]["_type"] == "LETTER":
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
    if node["_type"] == "NUM":
        result += str(node["value"])
    if node["_type"] == "LETTER":
        result += '\'' + node["value"] + '\''
    return result

def var_declarations(node):
    '''
    var_declarations : VAR var_declaration SEMICOLON
                    |
    '''
    result = ''
    if node is not None:
        assert node['p_type'] == "var_declarations"
        result += var_declaration(node["var_declaration"])
        result += '\n'
    return result

def var_declaration(node):
    '''
    var_declaration : var_declaration SEMICOLON idlist COLON type
                    | idlist COLON type
    '''
    assert node['p_type'] == "var_declaration"
    result = ''
    for it in node["values"]:
        if it['p_type']["_type"] == "ARRAY":
            result += Ptype(it['p_type'])
            result += ' '
            range = period(it['p_type']["period"])
            idlist = idlst(it["idlist"])
            for id in idlist:
                result += id
                result += range
                result += ',' if id != idlist[-1] else ';'
        elif it['p_type']["_type"] == "RECORD":
            result += 'struct ' + '{'
            result += multype(it['p_type']["multype"])
            result += '}'
            idlist = idlst(it["idlist"])
            for id in idlist:
                result += id
                result += ',' if id != idlist[-1] else ';'
        else:
            result += Ptype(it['p_type'])
            result += ' '
            idlist = idlst(it["idlist"])
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
    for period in node["values"]:
        size = period["end"]-period["start"]+1
        result += '['+str(size)+']'
    return result