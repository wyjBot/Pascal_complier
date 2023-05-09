from Generate.subProgram import *

def program_struct(ast):
    global domain
    '''
    programstruct : program_head ; program_body .
    '''
    node = ast
    result = ""
    domain += ["global"]
    if node is not None:
        assert node['p_type'] == "programstruct"
        result += program_head(node["child_nodes"][0])
        result += program_body(node["child_nodes"][1])
    else:
        result += '/* Error, Parser gives no AST. */'
    domain.pop()
    return result

def program_head(node):
    '''
    program_head : PROGRAM ID LPAREN idlist RPAREN
    '''
    assert node['p_type'] == "program_head"
    result = ""
    result+="#include<stdbool.h>\n"
    result+="#include<stdio.h>\n"
    return result

def program_body(node):
    '''
    program_body : const_declarations var_declarations subprogram_declarations compound_statement
    '''
    global domain
    assert node['p_type'] == "program_body"
    result = ""
    result += const_declarations(node["child_nodes"][0])
    result += var_declarations(node["child_nodes"][1])
    result += subprogram_declarations(node["child_nodes"][2])
    result += "int main(int argc,char* argv[])"
    domain += ["main"]
    result += '{'
    result += compound_statement(node["child_nodes"][3])
    result += '}'
    return result



# def pre_ast(node):
#     if not 'child_nodes' in node: return
#     if node['p_type'] == 'subprograms':
#         for i in node['info']['subprograms']:
#
#     for x in node['child_nodes']:
#         if not x:continue
#         if not 'p_type' in x: continue
#         node[x['p_type']]=x
#         pre_ast(x)
#     if not 'const_declarations' in node:
#         node['const_declarations']=None
#     del node['child_nodes']


def code_generate(_ast, _symbolTable):
    global domain,symbolTable
    # pre_ast(_ast) # print(_ast)
    symbolTable.clear()
    symbolTable.update(_symbolTable)  # 符号表
    result=program_struct(_ast)  # 从programstruct节点开始生成目标代码
    import Generate.optimize
    return Generate.optimize.code_format(result)  # 代码格式化

if __name__=="__main__":
    fr=open("./test/input.txt")
    data=json.load(fr)
    result=code_generate(data[0],data[1])
    print(result)
