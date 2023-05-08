import ply.lex as lex


class Lexer:
    # 保留字
    keywords = {
        'program': 'PROGRAM',
        'var': 'VAR',
        'procedure': 'PROCEDURE',
        'begin': 'BEGIN',
        'end': 'END',
        'if': 'IF',
        'then': 'THEN',
        'else': 'ELSE',
        'const': 'CONST',
        'array': 'ARRAY',
        'of': 'OF',
        'integer': 'INTEGER',
        'real': 'REAL',
        'boolean': 'BOOLEAN',
        'char': 'CHAR',
        'function': 'FUNCTION',
        'for': 'FOR',
        'to': 'TO',
        'do': 'DO',
        'read': 'READ',
        'write': 'WRITE',
        'not': 'NOT'
    }

    # Token类型列表的声明
    tokens = [
                 'ID',  # 标识符
                 'NUM',  # 常数
                 'LETTER',  # 字母a~z、A~Z
                 'RELOP',  # 关系运算符=、<>、<、<=、>、>=
                 'ADDOP',  # 运算符+、-和or
                 'MULOP',  # 运算符*、/、div、mod和and
                 'ASSIGNOP',  # 赋值号:=
                 'DOUBLEDOT',  # ..
             ] + list(keywords.values())

    t_ignore = ' \t'  # 忽略字符

    literals = ',;:\'().'  # 字面字符

    def __init__(self):
        self.error = []
        self.data = None
        self.lexer = None

    def t_ID(self, t):
        '[a-zA-Z][0-9a-zA-Z]*'
        t.type = self.keywords.get(t.value.lower(), 'ID')
        if t.value.lower() == 'div' or t.value.lower() == 'mod' or t.value.lower() == 'and':
            t.type = 'MULOP'
        if t.value.lower() == 'or':
            t.type = 'ADDOP'
        return t

    def t_NUM(self, t):
        '[0-9]+(.[0-9]+)?'
        try:
            t.value = int(t.value)
        except ValueError:
            t.value = float(t.value)
        return t

    def t_LETTER(self, t):
        '\'[a~zA~Z]\''
        t.value = t.value[1]
        return t

    def t_RELOP(self, t):
        '=|<>|<=|>=|<|>'
        return t

    def t_ADDOP(self, t):
        '\+|-'
        return t

    def t_MULOP(self, t):
        '\*|/'
        return t

    def t_ASSIGNOP(self, t):
        ':='
        return t

    def t_DOUBLEDOT(self, t):
        '\.\.'
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_COMMENT(self, t):
        r'{(.|\n|\t)*}'
        t.lexer.lineno += t.value.count('\n')

    def t_error(self, t):
        def getColumn(input, token):
            last_cr = input.rfind('\n', 0, token.lexpos)
            if last_cr < 0:
                last_cr = -1
            column = token.lexpos - last_cr
            return column
        self.error.append({
            'error': 'Lex error',
            'value': t.value[0],
            'line': t.lineno,
            'column': getColumn(self.data, t)
        })
        t.lexer.skip(1)

    def build(self, data, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        self.data = data

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)




# if __name__ == '__main__':
#     data = open('input.txt').read()
#     m = MyLexer()
#     m.build()
#     m.test(data)