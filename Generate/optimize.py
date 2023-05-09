
def code_format(srcCode):
        ''' 格式美化：添加换行 缩进'''
        indent = 0
        in_small = 0
        add_indent = False
        in_quote = False
        lines = list(srcCode)
        for i in range(0, len(lines)-1):
            add_indent = False
            if lines[i] == '&' and lines[i+1] == '*':
                lines[i] = ''
                lines[i+1] = ''
            if lines[i:i+2] == '*' and lines[i+1] == '&':
                lines[i] = ''
                lines[i+1] = ''
            if lines[i] in [',', ';']:
                lines[i] += ' '
            if lines[i] == '\"' or lines[i] == '\'':
                in_quote = ~in_quote
            if lines[i] == '(':
                in_small += 1
            if lines[i] == ')':
                in_small -= 1
            if in_quote == False and in_small == 0:
                if lines[i] == '{':
                    lines[i] += '\n'
                    indent += 1
                    add_indent = True
                if lines[i] == '}\n':
                    add_indent = True
                if lines[i] == '; ':
                    lines[i] += '\n'
                    add_indent = True
                if lines[i] == '\n':
                    add_indent = True
                if lines[i+1] == '}':
                    lines[i+1] += '\n'
                    indent -= 1
                    add_indent = True
            if add_indent == True:
                for j in range(0, indent):
                    lines[i] += '\t'
        tgtCode = ''.join(lines)
        return tgtCode