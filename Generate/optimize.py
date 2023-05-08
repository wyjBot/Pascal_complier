
# 代码格式化：添加换行、缩进
def code_format(targetCode):
        indent = 0
        in_quote = False
        in_small = 0
        add_indent = False
        code_list = list(targetCode)
        for i in range(0, len(code_list)-1):
            add_indent = False
            if code_list[i] == '&' and code_list[i+1] == '*':
                code_list[i] = ''
                code_list[i+1] = ''
            if code_list[i:i+2] == '*' and code_list[i+1] == '&':
                code_list[i] = ''
                code_list[i+1] = ''
            if code_list[i] in [',', ';']:
                code_list[i] += ' '
            if code_list[i] == '\"' or code_list[i] == '\'':
                in_quote = ~in_quote
            if code_list[i] == '(':
                in_small += 1
            if code_list[i] == ')':
                in_small -= 1
            if in_quote == False and in_small == 0:
                if code_list[i] == '{':
                    code_list[i] += '\n'
                    indent += 1
                    add_indent = True
                if code_list[i] == '}\n':
                    add_indent = True
                if code_list[i] == '; ':
                    code_list[i] += '\n'
                    add_indent = True
                if code_list[i] == '\n':
                    add_indent = True
                if code_list[i+1] == '}':
                    code_list[i+1] += '\n'
                    indent -= 1
                    add_indent = True
            if add_indent == True:
                for j in range(0, indent):
                    code_list[i] += '\t'
        targetCode = ''.join(code_list)
        return targetCode