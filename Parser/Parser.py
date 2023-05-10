import ply.yacc as yacc
from Parser.Lexer import Lexer


class Parser:
    tokens = Lexer.tokens

    def __init__(self):
        self.input = None
        self.symbolList = {'curSymbol': {}, 'subFuncSymbol': {}, 'funcID': {}}
        self.isInSubFunc = False
        self.error = []
        self.warning = []
        self.symbolTable = None
        self.parser = None

    def p_programstruct(self, p):
        '''programstruct : program_head ';' program_body '.' '''
        p[0] = {
            'p_length': len(p),
            'p_type': 'programstruct',
            'child_nodes': [p[1], p[3]],
            'info': {}
        }
        self.symbolTable = {
            'constTable': p[3]['st']['ct'],
            'varTable': p[3]['st']['vt'],
            'subFuncTable': p[3]['st']['sft']
        }

    def p_program_head(self, p):
        '''program_head : PROGRAM ID '(' idlist ')'
                        | PROGRAM ID'''
        if len(p) == 6:
            p[0] = {
                'p_length': len(p),
                'p_type': 'program_head',
                'child_nodes': [p[4], ],
                'info': {'ID': p[2]}
            }

        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'program_head',
                'child_nodes': [],
                'info': {
                    'ID': p[2],
                }
            }

    def p_program_body(self, p):
        '''program_body : const_declarations var_declarations subprogram_declarations compound_statement'''
        p[0] = {
            'p_length': len(p),
            'p_type': 'program_body',
            'child_nodes': [p[1], p[2], p[3], p[4]],
            'info': {}
        }
        p[0]['st'] = {
            'ct': p[1]['st'],
            'vt': p[2]['st'],
            'sft': p[3]['st']
        }

    def p_idlist(self, p):
        '''idlist : ID
                  | idlist ',' ID'''
        if len(p) == 4:
            p[0] = {
                'p_length': len(p),
                'p_type': 'idlist',
                'info': {
                    'id_l': p[1]['info']['id_l'] + [p[3]]
                }
            }
            self.isRepeatedDefine(p[3], p.slice[3].lineno, p.slice[3].lexpos)
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'idlist',
                'child_nodes': [],
                'info': {
                    'id_l': [p[1]]
                }
            }
            self.isRepeatedDefine(p[1], p.slice[1].lineno, p.slice[1].lexpos)

    def p_const_declarations(self, p):
        '''const_declarations : empty
                              | CONST const_declaration ';' '''
        if len(p) == 4:
            p[0] = {
                'p_length': len(p),
                'p_type': 'const_declarations',
                'child_nodes': [p[2], ],
                'info': {}
            }
            p[0]['st'] = p[2]['st']
        else:
            p[0] = {'st': []}

    def p_const_declaration(self, p):
        '''const_declaration : ID RELOP const_value
                             | const_declaration ';' ID RELOP const_value'''  # RELOP只能为'='
        if len(p) == 6:
            p[0] = {
                'p_length': len(p),
                'p_type': 'const_declaration',
                'child_nodes': [p[1], p[5]],
                'info': {
                    'values': p[1]['info']['values'] + [{'ID': p[3], 'const_value': p[5]}]
                }
            }
            newST = {
                'id': p[3],
                'type': p[5]['info']['true_type'],
                'value': p[5]['info']['value']
            }
            p[0]['st'] = p[1]['st'] + [newST]
            self.isRepeatedDefine(p[3], p.slice[3].lineno, p.slice[3].lexpos)
            if self.isInSubFunc:
                self.symbolList['subFuncSymbol'][p[3]] = newST.copy()
                self.symbolList['subFuncSymbol'][p[3]]['isConst'] = True
            else:
                self.symbolList['curSymbol'][p[3]] = newST.copy()
                self.symbolList['curSymbol'][p[3]]['isConst'] = True
            if p[4] != '=':
                self.error.append({
                    'error': 'illegal syntax',
                    'value': p[2],
                    'line': p.slice[2].lineno,
                    'column': self.getColumn(self.input,  p.slice[2].lexpos)
                })
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'const_declaration',
                'child_nodes': [p[3], ],
                'info': {
                    'values': [{'ID': p[1], 'const_value': p[3]}]
                }
            }
            newST = {
                'id': p[1],
                'type': p[3]['info']['true_type'],
                'value': p[3]['info']['value']
            }
            p[0]['st'] = [newST]
            self.isRepeatedDefine(p[1], p.slice[1].lineno, p.slice[1].lexpos)
            if self.isInSubFunc:
                self.symbolList['subFuncSymbol'][p[1]] = newST.copy()
                self.symbolList['subFuncSymbol'][p[1]]['isConst'] = True
            else:
                self.symbolList['curSymbol'][p[1]] = newST.copy()
                self.symbolList['curSymbol'][p[1]]['isConst'] = True
            if p[2] != '=':
                self.error.append({
                    'error': 'illegal syntax',
                    'value': p[4],
                    'line': p.slice[4].lineno,
                    'column': self.getColumn(self.input,  p.slice[4].lexpos)
                })

    def p_const_value(self, p):
        '''const_value : ADDOP NUM  
                       | NUM
                       | LETTER'''  # ADDOP只能为'+'、'-'
        if len(p) == 3:
            p[0] = {
                'p_length': len(p),
                'p_type': 'const_value',
                'child_nodes': [],
                'info': {
                    '_type': 'NUM',
                    'true_type': 'INTEGER' if type(p[2]) == int else 'REAL',
                    'value': -p[2] if p[1] == '-' else p[2]
                }
            }
            if p[1].upper() == 'OR':
                self.error.append({
                    'error': 'illegal syntax',
                    'value': p[1],
                    'line': p.slice[1].lineno,
                    'column': self.getColumn(self.input,  p.slice[1].lexpos)
                })
        elif type(p[1]) != str:
            p[0] = {
                'p_length': len(p),
                'p_type': 'const_value',
                'child_nodes': [],
                'info': {
                    '_type': 'NUM',
                    'true_type': 'INTEGER' if type(p[1]) == int else 'REAL',
                    'value': p[1]
                }
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'const_value',
                'child_nodes': [],
                'info': {
                    '_type': 'LETTER',
                    'true_type': 'CHAR',
                    'value': p[1]
                }
            }

    def p_var_declarations(self, p):
        '''var_declarations : empty
                            | VAR var_declaration ';' '''
        if len(p) == 4:
            p[0] = {
                'p_length': len(p),
                'p_type': 'var_declarations',
                'child_nodes': [p[2], ],
                'info': {}
            }
            p[0]['st'] = p[2]['st']
        else:
            p[0] = {'st': []}

    def p_var_declaration(self, p):
        '''var_declaration : idlist ':' type
                           | var_declaration ';' idlist ':' type'''
        if len(p) == 6:
            p[0] = {
                'p_length': len(p),
                'p_type': 'var_declaration',
                'child_nodes': [p[1], p[3], p[5]],
                'info': {
                    'values': p[1]['info']['values'] + [{'id_l': p[3], 'type': p[5]}]
                }
            }
            p[0]['st'] = p[1]['st']
            for i in p[3]['info']['id_l']:
                newST = {
                    'id': i,
                    'type': p[5]['st']['type'],
                    'array': {
                        'isArray': p[5]['st']['array']['isArray'],
                        'dimension': p[5]['st']['array']['dimension'],
                        'size': p[5]['st']['array']['size'],
                        'start': p[5]['st']['array']['start'],
                    }
                }
                p[0]['st'] += [newST]
                if self.isInSubFunc:
                    self.symbolList['subFuncSymbol'][i] = newST.copy()
                    self.symbolList['subFuncSymbol'][i]['isConst'] = False
                else:
                    self.symbolList['curSymbol'][i] = newST.copy()
                    self.symbolList['curSymbol'][i]['isConst'] = False
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'var_declaration',
                'child_nodes': [p[1], p[3]],
                'info': {
                    'values': [{'id_l': p[1], 'type': p[3]}]
                }
            }
            p[0]['st'] = []
            for i in p[1]['info']['id_l']:
                newST = {
                    'id': i,
                    'type': p[3]['st']['type'],
                    'array': {
                        'isArray': p[3]['st']['array']['isArray'],
                        'dimension': p[3]['st']['array']['dimension'],
                        'size': p[3]['st']['array']['size'],
                        'start': p[3]['st']['array']['start'],
                    }
                }
                p[0]['st'] += [newST]
                if self.isInSubFunc:
                    self.symbolList['subFuncSymbol'][i] = newST.copy()
                    self.symbolList['subFuncSymbol'][i]['isConst'] = False
                else:
                    self.symbolList['curSymbol'][i] = newST.copy()
                    self.symbolList['curSymbol'][i]['isConst'] = False

    def p_type(self, p):
        '''type : basic_type
                | ARRAY '[' period ']' OF basic_type'''
        if len(p) == 2:
            p[0] = {
                'p_length': len(p),
                'p_type': 'type',
                'child_nodes': [p[1], ],
                'info': {
                    '_type': p[1]
                }
            }
            p[0]['st'] = {
                'type': p[1]['st'],
                'array': {
                    'isArray': False,
                    'dimension': 0,
                    'size': [],
                    'start': [],
                }
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'type',
                'child_nodes': [p[3], p[6]],
                'info': {
                    '_type': 'ARRAY',
                }
            }
            p[0]['st'] = {
                'type': p[6]['st'],
                'array': {
                    'isArray': True,
                    'dimension': p[3]['st']['dimension'],
                    'size': p[3]['st']['size'],
                    'start': p[3]['st']['start'],
                }
            }

    def p_basic_type(self, p):
        '''basic_type : INTEGER
                      | REAL
                      | BOOLEAN
                      | CHAR'''
        p[0] = {
            'p_length': len(p),
            'p_type': 'basic_type',
            'child_nodes': [],
            'info': {
                '_type': p[1].upper()
            }
        }
        p[0]['st'] = p[1].upper()

    def p_period(self, p):
        '''period : NUM DOUBLEDOT NUM
                  | period ',' NUM DOUBLEDOT NUM'''
        if len(p) == 4:
            # NUM只能为整数
            if type(p[1]) == float:
                self.error.append({
                    'error': 'The number representing array bounds should be integer',
                    'value': p[1],
                    'line': p.slice[1].lineno,
                    'column': self.getColumn(self.input,  p.slice[1].lexpos)
                })
            if type(p[3]) == float:
                self.error.append({
                    'error': 'The number representing array bounds should be integer',
                    'value': p[3],
                    'line': p.slice[3].lineno,
                    'column': self.getColumn(self.input,  p.slice[3].lexpos)
                })
            # 左边界不能大于右边界
            if p[1] > p[3]:
                self.error.append({
                    'error': 'The lower limit cannot be greater than the upper limit',
                    'value': [p[1], p[3]],
                    'line': p.slice[1].lineno,
                    'column': self.getColumn(self.input,  p.slice[1].lexpos)
                })
            p[0] = {
                'p_length': len(p),
                'p_type': 'period',
                'child_nodes': [],
                'info': {
                    'values': [{'start': p[1], 'end': p[3]}]
                }
            }
            p[0]['st'] = {
                'dimension': 1,
                'start': [p[1]],
                'size': [p[3] - p[1] + 1]
            }
        else:
            # NUM只能为整数
            if type(p[3]) == float:
                self.error.append({
                    'error': 'The number representing array bounds should be integer',
                    'value': p[3],
                    'line': p.slice[3].lineno,
                    'column': self.getColumn(self.input,  p.slice[3].lexpos)
                })
            if type(p[5]) == float:
                self.error.append({
                    'error': 'The number representing array bounds should be integer',
                    'value': p[5],
                    'line': p.slice[5].lineno,
                    'column': self.getColumn(self.input,  p.slice[5].lexpos)
                })
            # 左边界不能大于右边界
            if p[3] > p[5]:
                self.error.append({
                    'error': 'The lower limit cannot be greater than the upper limit',
                    'value': [p[3], p[5]],
                    'line': p.slice[3].lineno,
                    'column': self.getColumn(self.input,  p.slice[3].lexpos)
                })
            p[0] = {
                'p_length': len(p),
                'p_type': 'period',
                'child_nodes': [p[1], ],
                'info': {
                    'values': p[1]['info']['values'] + [{'start': p[3], 'end': p[5]}]
                }
            }
            p[0]['st'] = {
                'dimension': p[1]['st']['dimension'] + 1,
                'start': p[1]['st']['start'] + [p[3]],
                'size': p[1]['st']['size'] + [p[5] - p[3] + 1]
            }

    def p_subprogram_declarations(self, p):
        '''subprogram_declarations : empty
                                   | subprogram_declarations subprogram ';' '''
        self.isInSubFunc = False
        if len(p) == 4:
            p[0] = {
                'p_length': len(p),
                'p_type': 'subprogram_declarations',
                'child_nodes': [p[1], p[2]],
                'info': {
                    'subprograms': p[1]['info']['subprograms'] + [p[2]] if 'info' in p[1].keys() else [p[2]]
                }
            }
            p[0]['st'] = p[1]['st'] + [p[2]['st']]
        else:
            p[0] = {'st': []}

    def p_subprogram(self, p):
        '''subprogram : subprogram_head ';' subprogram_body'''
        p[0] = {
            'p_length': len(p),
            'p_type': 'subprogram',
            'child_nodes': [p[1], p[3]],
            'info': {
            }
        }
        p[0]['st'] = {
            'id': p[1]['st']['id'],
            'type': p[1]['st']['type'],
            'size': p[1]['st']['size'],
            'isReference': p[1]['st']['isReference'],
            'constTable': p[3]['st']['constTable'],
            'varTable': p[1]['st']['varTable'] + p[3]['st']['varTable']
        }

    def p_subprogram_head(self, p):
        '''subprogram_head : procedure ID formal_parameter
                           | function ID formal_parameter ':' basic_type'''
        if len(p) == 4:
            p[0] = {
                'p_length': len(p),
                'p_type': 'subprogram_head',
                'child_nodes': [p[3], ],
                'info': {
                    'ID': p[2],
                    '_type': 'PROCEDURE'
                }
            }
            p[0]['st'] = {
                'id': p[2],
                'type': None,
                'size': p[3]['st']['size'],
                'isReference': p[3]['st']['isReference'],
                'varTable': p[3]['st']['varTable']
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'subprogram_head',
                'child_nodes': [p[3], p[5]],
                'info': {
                    'ID': p[2],
                    '_type': 'FUNCTION'
                }
            }
            p[0]['st'] = {
                'id': p[2],
                'type': p[5]['st'],
                'size': p[3]['st']['size'],
                'isReference': p[3]['st']['isReference'],
                'varTable': p[3]['st']['varTable']
            }
        if p[2] in self.symbolList['funcID'].keys():
            self.error.append({
                'error': 'Define function_ID repeatedly',
                'value': p[2],
                'line': p.slice[2].lineno,
                'column': self.getColumn(self.input,  p.slice[2].lexpos)
            })
        self.symbolList['funcID'][p[2]] = p[0]['st'].copy()
        self.symbolList['subFuncSymbol'][p[2]] = p[0]['st'].copy()
        self.symbolList['subFuncSymbol'][p[2]]['isConst'] = False

    def p_procedure(self, p):
        '''procedure : PROCEDURE'''
        self.isInSubFunc = True
        self.symbolList['subFuncSymbol'].clear()

    def p_function(self, p):
        '''function : FUNCTION'''
        self.isInSubFunc = True
        self.symbolList['subFuncSymbol'].clear()

    def p_formal_parameter(self, p):
        '''formal_parameter : empty
                            | '(' parameter_list ')' '''
        if len(p) == 4:
            p[0] = {
                'p_length': len(p),
                'p_type': 'formal_parameter',
                'child_nodes': [p[2], ],
                'info': {}
            }
            p[0]['st'] = {
                'size': p[2]['st']['size'],
                'isReference': p[2]['st']['isReference'],
                'varTable': p[2]['st']['varTable']
            }
        else:
            p[0] = {'st': {
                'size': None,
                'isReference': None,
                'varTable': None
            }}

    def p_parameter_list(self, p):
        '''parameter_list : parameter
                          | parameter_list ';' parameter'''
        if len(p) == 4:
            p[0] = {
                'p_length': len(p),
                'p_type': 'parameter_list',
                'child_nodes': [p[1], p[3]],
                'info': {
                    'parameters': p[1]['info']['parameters'] + [p[3]]
                }
            }
            p[0]['st'] = {
                'size': p[1]['st']['size'] + p[3]['st']['size'],
                'isReference': p[1]['st']['isReference'] + p[3]['st']['isReference'],
                'varTable': p[1]['st']['varTable'] + p[3]['st']['varTable']
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'parameter_list',
                'child_nodes': [p[1], ],
                'info': {
                    'parameters': [p[1]]
                }
            }
            p[0]['st'] = {
                'size': p[1]['st']['size'],
                'isReference': p[1]['st']['isReference'],
                'varTable': p[1]['st']['varTable']
            }

    def p_parameter(self, p):
        '''parameter : var_parameter
                     | value_parameter'''
        p[0] = {
            'p_length': len(p),
            'p_type': 'parameter',
            'child_nodes': [p[1], ],
            'info': {
                'value': p[1]
            }
        }
        p[0]['st'] = p[1]['st']

    def p_var_parameter(self, p):
        '''var_parameter : VAR value_parameter'''
        p[0] = {
            'p_length': len(p),
            'p_type': 'var_parameter',
            'child_nodes': [p[2], ],
            'info': {}
        }
        p[0]['st'] = {
            'isReference': [True for i in range(len(p[2]['child_nodes'][0]['info']['id_l']))],
            'size': p[2]['st']['size'],
            'varTable': p[2]['st']['varTable']
        }

    def p_value_parameter(self, p):
        '''value_parameter : idlist ':' basic_type'''
        p[0] = {
            'p_length': len(p),
            'p_type': 'value_parameter',
            'child_nodes': [p[1], p[3]],
            'info': {
                'basic_type': p[3]
            }
        }
        p[0]['st'] = {
            'isReference': [False for i in range(len(p[1]['info']['id_l']))],
            'size': len(p[1]['info']['id_l']),
            'varTable': []
        }
        for i in p[1]['info']['id_l']:
            newST = {
                'id': i,
                'type': p[3]['st'],
                'array': {
                    'isArray': False,
                    'dimension': 0,
                    'size': [],
                    'start': []
                }
            }
            p[0]['st']['varTable'] += [newST]
            self.symbolList['subFuncSymbol'][i] = newST.copy()
            self.symbolList['subFuncSymbol'][i]['isConst'] = False

    def p_subprogram_body(self, p):
        '''subprogram_body : const_declarations var_declarations compound_statement'''
        p[0] = {
            'p_length': len(p),
            'p_type': 'subprogram_body',
            'child_nodes': [p[1], p[2], p[3]],
            'info': {}
        }
        p[0]['st'] = {
            'constTable': p[1]['st'],
            'varTable': p[2]['st']
        }

    def p_compound_statement(self, p):
        '''compound_statement : BEGIN statement_list END'''
        p[0] = {
            'p_length': len(p),
            'p_type': 'compound_statement',
            'child_nodes': [p[2], ],
            'info': {}
        }

    def p_statement_list(self, p):
        '''statement_list : statement
                          | statement_list ';' statement'''
        if len(p) == 2:
            p[0] = {
                'p_length': len(p),
                'p_type': 'statement_list',
                'child_nodes': [p[1], ],
                'info': {
                    'statements': [p[1]]
                }
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'statement_list',
                'child_nodes': [p[1], p[3]],
                'info': {
                    'statements': p[1]['info']['statements'] + [p[3]]
                }
            }

    def p_statement(self, p):
        '''statement : empty
                     | variable ASSIGNOP expression
                     | procedure_call
                     | compound_statement
                     | IF expression THEN statement else_part
                     | FOR ID ASSIGNOP expression TO expression DO statement
                     | READ '(' variable_list ')'
                     | WRITE '(' expression_list ')' '''
        if type(p[1]) == str:
            if p[1].upper() == 'IF':
                p[0] = {
                    'p_length': len(p),
                    'p_type': "statement",
                    'child_nodes': [p[2], p[4], p[5]],
                    'info': {
                        '_type': 'IF'
                    }
                }
            elif p[1].upper() == 'FOR':
                p[0] = {
                    'p_length': len(p),
                    'p_type': "statement",
                    'child_nodes': [p[4], p[6], p[8]],
                    'info': {
                        '_type': 'FOR',
                        'ID': p[2],
                        'ASSIGNOP': p[3]
                    }
                }
                if not self.findSymbol(p[2]):
                    self.error.append({
                        'error': 'Undefined identifier',
                        'value': p[2],
                        'line': p.slice[2].lineno,
                        'column': self.getColumn(self.input,  p.slice[2].lexpos)
                    })
                elif self.findSymbol(p[2])['isConst']:
                    self.error.append({
                        'error': 'Constant cannot be assigned',
                        'value': p[2],
                        'line': p.slice[2].lineno,
                        'column': self.getColumn(self.input,  p.slice[2].lexpos)
                    })
                elif p[4]['info']['exp_type'] != 'Undefined' and not self.isSafeAssign(p[4]['info']['exp_type'], self.findSymbol(p[2])['type']):
                    self.warning.append({
                        'warning': 'Unsafe assignment',
                        'value': p[4]['info']['exp_type'] + ' assign to ' + self.findSymbol(p[2])['type'],
                        'line': p.slice[2].lineno,
                        'column': self.getColumn(self.input,  p.slice[2].lexpos)
                    })
            elif p[1].upper() == 'READ':
                p[0] = {
                    'p_length': len(p),
                    'p_type': "statement",
                    'child_nodes': [p[3], ],
                    'info': {
                        '_type': 'READ'
                    }
                }
            elif p[1].upper() == 'WRITE':
                p[0] = {
                    'p_length': len(p),
                    'p_type': "statement",
                    'child_nodes': [p[3], ],
                    'info': {
                        '_type': 'WRITE'
                    }
                }
        elif p[1]['p_type'] == 'empty':
            p[0] = []
        elif p[1]['p_type'] == 'variable':
            p[0] = {
                'p_length': len(p),
                'p_type': 'statement',
                'child_nodes': [p[1], p[3]],
                'info': {
                    '_type': 'variable',
                    'ASSIGNOP': p[2]
                }
            }
            if self.findSymbol(p[1]['info']['ID']):
                if self.findSymbol(p[1]['info']['ID'])['isConst']:
                    self.error.append({
                        'error': 'Constant cannot be assigned',
                        'value': p[1]['info']['ID'],
                        'line': p.slice[2].lineno,
                        'column': self.getColumn(self.input, p.slice[2].lexpos)
                    })
                else:
                    var_type = p[1]['info']['var_type']
                    exp_type = p[3]['info']['exp_type']
                    if var_type is None:
                        self.error.append({
                            'error': 'Procedure has no return value',
                            'value': p[1]['info']['ID'],
                            'line': p.slice[2].lineno,
                            'column': self.getColumn(self.input, p.slice[2].lexpos)
                        })
                    elif exp_type and exp_type != 'Undefined' and not self.isSafeAssign(exp_type, var_type):
                        self.warning.append({
                            'warning': 'Unsafe assignment',
                            'value': exp_type + ' assign to ' + var_type,
                            'line': p.slice[2].lineno,
                            'column': self.getColumn(self.input,  p.slice[2].lexpos)
                        })
        elif p[1]['p_type'] == 'procedure_call':
            p[0] = {
                'p_length': len(p),
                'p_type': "statement",
                'child_nodes': [p[1], ],
                'info': {
                    '_type': 'procedure_call'
                }
            }
        elif p[1]['p_type'] == 'compound_statement':
            p[0] = {
                'p_length': len(p),
                'p_type': "statement",
                'child_nodes': [p[1], ],
                'info': {
                    '_type': 'compound_statement'
                }
            }


    def p_variable_list(self, p):
        '''variable_list : variable
                         | variable_list ',' variable'''
        if len(p) == 2:
            p[0] = {
                'p_length': len(p),
                'p_type': "variable_list",
                'child_nodes': [p[1], ],
                'info': {
                    'variables': [p[1]]
                }
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': "variable_list",
                'child_nodes': [p[1], p[3]],
                'info': {
                    'variables': p[1]['info']['variables'] + [p[3]]
                }
            }

    def p_variable(self, p):
        '''variable : ID id_varpart'''
        p[0] = {
            'p_length': len(p),
            'p_type': 'variable',
            'child_nodes': [p[2], ],
            'info': {
                'ID': p[1],
                'var_type': self.findSymbol(p[1])['type'] if self.findSymbol(p[1]) else 'UNDEFINED'
            }
        }
        if p[0]['info']['var_type'] == 'UNDEFINED':  # 判断id是否被定义
            self.error.append({
                'error': 'Undefined identifier',
                'value': p[1],
                'line': p.slice[1].lineno,
                'column': self.getColumn(self.input, p.slice[1].lexpos)
            })
        if p[2] is not None:
            if not self.findSymbol(p[1])['array']['isArray']:  # 判断若id有下标，id是否为array
                self.error.append({
                    'error': 'subscripted value is not an array',
                    'value': p[1],
                    'line': p.slice[1].lineno,
                    'column': self.getColumn(self.input, p.slice[1].lexpos)
                })
            elif len(p[2]['child_nodes'][0]['info']['exp_type']) != self.findSymbol(p[1])['array']['dimension']:  # 维度是否一致
                self.error.append({
                    'error': 'Dimension different',
                    'value': p[1],
                    'line': p.slice[1].lineno,
                    'column': self.getColumn(self.input, p.slice[1].lexpos)
                })
        elif 'array' in self.findSymbol(p[1]).keys() and self.findSymbol(p[1])['array']['isArray']:  # 维度是否一致
            self.error.append({
                'error': 'Dimension different',
                'value': p[1],
                'line': p.slice[1].lineno,
                'column': self.getColumn(self.input, p.slice[1].lexpos)
            })

    def p_id_varpart(self, p):
        '''id_varpart : empty
                      | '[' expression_list ']' '''
        if len(p) == 4:
            p[0] = {
                'p_length': len(p),
                'p_type': 'id_varpart',
                'child_nodes': [p[2], ],
                'info': {}
            }
        else:
            p[0] = None

    def p_procedure_call(self, p):
        '''procedure_call : ID
                          | ID '(' expression_list ')' '''
        if len(p) == 2:
            p[0] = {
                'p_length': len(p),
                'p_type': 'procedure_call',
                'child_nodes': [],
                'info': {
                    'ID': p[1]
                }
            }
            if p[1] not in self.symbolList['funcID'].keys():
                self.error.append({
                    'error': 'Undefined identifier',
                    'value': p[1],
                    'line': p.slice[1].lineno,
                    'column': self.getColumn(self.input,  p.slice[1].lexpos)
                })
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'procedure_call',
                'child_nodes': [p[3], ],
                'info': {
                    'ID': p[1]
                }
            }
            self.errorInProcedureCall(p)

    def p_else_part(self, p):
        '''else_part : empty
                     | ELSE statement'''
        if len(p) == 3:
            p[0] = {
                'p_length': len(p),
                'p_type': 'else_part',
                'child_nodes': [p[2], ],
                'info': {}
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'else_part',
                'child_nodes': [],
                'info': {}
            }

    def p_expression_list(self, p):
        '''expression_list : expression
                           | expression_list ',' expression'''
        if len(p) == 2:
            p[0] = {
                'p_length': len(p),
                'p_type': 'expression_list',
                'child_nodes': [p[1], ],
                'info': {
                    'exp_type': [p[1]['info']['exp_type']],
                    'expressions': [p[1]]
                }
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'expression_list',
                'child_nodes': [p[1], p[3]],
                'info': {
                    'exp_type': p[1]['info']['exp_type'] + [p[3]['info']['exp_type']],
                    'expressions': p[1]['info']['expressions'] + [p[3]]
                }
            }

    def p_expression(self, p):
        '''expression : simple_expression
                      | simple_expression RELOP simple_expression'''
        if len(p) == 2:
            p[0] = {
                'p_length': len(p),
                'p_type': 'expression',
                'child_nodes': [p[1], ],
                'info': {
                    'exp_type': p[1]['info']['exp_type']
                }
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'expression',
                'child_nodes': [p[1], p[3]],
                'info': {
                    'RELOP': p[2],
                    'exp_type': 'BOOLEAN'
                }
            }

    def p_simple_expression(self, p):
        '''simple_expression : term
                             | simple_expression ADDOP term'''
        if len(p) == 2:
            p[0] = {
                'p_length': len(p),
                'p_type': 'simple_expression',
                'child_nodes': [p[1], ],
                'info': {
                    'exp_type': p[1]['info']['exp_type']
                }
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'simple_expression',
                'child_nodes': [p[1], p[3]],
                'info': {
                    'ADDOP': p[2]
                }
            }
            self.getExpType(p)

    def p_term(self, p):
        '''term : factor
                | term MULOP factor'''
        if len(p) == 2:
            p[0] = {
                'p_length': len(p),
                'p_type': 'term',
                'child_nodes': [p[1], ],
                'info': {
                    'exp_type': p[1]['info']['exp_type']
                }
            }
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'term',
                'child_nodes': [p[1], p[3]],
                'info': {
                    'MULOP': p[2]
                }
            }
            self.getExpType(p)

    def p_factor(self, p):
        '''factor : NUM
                  | variable
                  | '(' expression ')'
                  | ID '(' expression_list ')' 
                  | NOT factor
                  | ADDOP factor'''  # ADDOP只能为'-'
        if type(p[1]) == int or type(p[1]) == float:
            p[0] = {
                'p_length': len(p),
                'p_type': 'factor',
                'child_nodes': [],
                'info': {
                    '_type': 'NUM',
                    'exp_type': 'INTEGER' if type(p[1]) == int else 'REAL',
                    'NUM': p[1]
                }
            }
        elif type(p[1]) == dict:
            p[0] = {
                'p_length': len(p),
                'p_type': 'factor',
                'child_nodes': [p[1], ],
                'info': {
                    '_type': 'variable',
                    'exp_type': p[1]['info']['var_type']
                }
            }
        elif p[1] == '(':
            p[0] = {
                'p_length': len(p),
                'p_type': 'factor',
                'child_nodes': [p[2], ],
                'info': {
                    '_type': 'expression',
                    'exp_type': p[2]['info']['exp_type'],
                }
            }
        elif p[1].upper() == 'NOT':
            p[0] = {
                'p_length': len(p),
                'p_type': 'factor',
                'child_nodes': [p[2], ],
                'info': {
                    '_type': 'NOT',
                    'exp_type': p[2]['info']['exp_type'],
                }
            }
        elif p[1] == '+' or p[1] == '-' or p[1].upper == 'OR':
            p[0] = {
                'p_length': len(p),
                'p_type': 'factor',
                'child_nodes': [p[2], ],
                'info': {
                    '_type': 'UMINUS' if p[1] == '-' else 'NORMAL',
                    'exp_type': p[2]['info']['exp_type'],
                }
            }
            if p[1].upper == 'OR':
                self.error.append({
                    'error': 'illegal syntax',
                    'value': p[1],
                    'line': p.slice[1].lineno,
                    'column': self.getColumn(self.input,  p.slice[1].lexpos)
                })
        else:
            p[0] = {
                'p_length': len(p),
                'p_type': 'factor',
                'child_nodes': [p[3], ],
                'info': {
                    '_type': 'procedure_id',
                    'exp_type': self.symbolList['funcID'][p[1]]['type'] if p[1] in self.symbolList['funcID'].keys() else 'Undefined',
                    'ID': p[1]
                }
            }
            if p[0]['info']['exp_type'] is None:
                self.error.append({
                    'error': 'Procedure has no return value',
                    'value': p[1],
                    'line': p.slice[1].lineno,
                    'column': self.getColumn(self.input, p.slice[1].lexpos)
                })
            self.errorInProcedureCall(p)

    def p_empty(self, p):
        'empty :'
        p[0] = {
            'p_length': len(p),
            'p_type': 'empty',
            'child_nodes': [],
            'info': {}
        }
        pass

    def p_error(self, p):
        if p:
            self.error.append({
                'error': 'illegal syntax',
                'value': p.value,
                'line': p.lineno,
                'column': self.getColumn(self.input,  p.lexpos)
            })

    def isRepeatedDefine(self, id, line, lexpos):
        if self.isInSubFunc:
            if id in self.symbolList['subFuncSymbol'].keys():
                self.error.append({
                    'error': 'Define ID repeatedly',
                    'value': id,
                    'line': line,
                    'column': self.getColumn(self.input,  lexpos)
                })
        else:
            if id in self.symbolList['curSymbol'].keys():
                self.error.append({
                    'error': 'Define ID repeatedly',
                    'value': id,
                    'line': line,
                    'column': self.getColumn(self.input,  lexpos)
                })

    def getExpType(self, p):
        if p[1]['info']['exp_type'] == 'UNDEFINED' or p[3]['info']['exp_type'] == 'UNDEFINED':
            p[0]['info']['exp_type'] = 'UNDEFINED'
        elif p[1]['info']['exp_type'] == "REAL" or p[3]['info']['exp_type'] == "REAL":
            p[0]['info']['exp_type'] = "REAL"
        elif p[1]['info']['exp_type'] == "INTEGER" or p[3]['info']['exp_type'] == "INTEGER":
            p[0]['info']['exp_type'] = "INTEGER"
        elif p[1]['info']['exp_type'] == "CHAR" or p[3]['info']['exp_type'] == "CHAR":
            p[0]['info']['exp_type'] = "CHAR"
        elif p[1]['info']['exp_type'] == "BOOLEAN" or p[3]['info']['exp_type'] == "BOOLEAN":
            p[0]['info']['exp_type'] = "BOOLEAN"

    def findSymbol(self, id):
        if self.isInSubFunc and id in self.symbolList['subFuncSymbol'].keys():
            return self.symbolList['subFuncSymbol'][id]
        elif id in self.symbolList['curSymbol'].keys():
            return self.symbolList['curSymbol'][id]
        else:
            return False

    def isSafeAssign(self, sour, des):
        if (
                (sour == 'INTEGER' and (des == 'INTEGER' or des == 'REAL')) or
                (sour == 'REAL' and des == 'REAL') or
                (sour == 'CHAR' and (des == 'CHAR' or des == 'INTEGER' or des == 'REAL')) or
                (sour == 'BOOLEAN' and (des == 'BOOLEAN' or des == 'INTEGER' or des == 'REAL' or des == 'CHAR'))
        ):
            return True
        return False

    def errorInProcedureCall(self, p):
        if p[1] not in self.symbolList['funcID'].keys():
            self.error.append({
                'error': 'Undefined identifier',
                'value': p[1],
                'line': p.slice[1].lineno,
                'column': self.getColumn(self.input,  p.slice[1].lexpos)
            })
        elif len(p[3]['info']['expressions']) != self.symbolList['funcID'][p[1]]['size']:
            self.error.append({
                'error': 'The number of parameters does not match in function call',
                'value': p[1],
                'line': p.slice[1].lineno,
                'column': self.getColumn(self.input,  p.slice[1].lexpos)
            })
        else:
            for i in range(len(p[3]['info']['expressions'])):
                var_type = p[3]['info']['exp_type'][i]
                para_type = self.symbolList['funcID'][p[1]]['varTable'][i]['type']
                if var_type != 'Undefined' and para_type != 'Undefined' and not self.isSafeAssign(var_type, para_type):
                    self.warning.append({
                        'warning': 'Unsafe assignment',
                        'value': str(i + 1) + 'th parameter: ' + var_type + ' assign to ' + para_type,
                        'line': p.slice[1].lineno,
                        'column': self.getColumn(self.input,  p.slice[1].lexpos)
                    })
                elif self.symbolList['funcID'][p[1]]['isReference'][i] and not (
                        p[3]['info']['expressions'][i]['child_nodes'][0]['p_length'] == 2 and
                        p[3]['info']['expressions'][i]['child_nodes'][0]['child_nodes'][0]['p_length'] == 2 and
                        p[3]['info']['expressions'][i]['child_nodes'][0]['child_nodes'][0]['child_nodes'][0]['info']['_type'] == 'variable'
                ):
                    self.error.append({
                        'error': 'Unable to call by reference',
                        'value': str(i + 1) + 'th parameter',
                        'line': p.slice[1].lineno,
                        'column': self.getColumn(self.input,  p.slice[1].lexpos)
                    })

    def getColumn(self, input, lexpos):
        last_cr = input.rfind('\n', 0, lexpos)
        if last_cr < 0:
            last_cr = -1
        column = lexpos - last_cr
        return column

    def run(self, input, **kwargs):
        self.input = input
        lexer = Lexer()
        lexer.build(input)
        self.parser = yacc.yacc(module=self, **kwargs)
        ast = self.parser.parse(input)
        return [ast, self.symbolTable, self.warning, lexer.error + self.error]

    
if __name__ == '__main__':
    data = open('../input.txt').read()
    m = Parser()
    import json as js
    fw=open("../input.out_const", "w+")
    ret=m.run(data)
    print(type(ret[1]))
    js.dump(ret,fw,indent=2)
