from Parser.Parser import Parser
from Generate.program import code_generate

parser = Parser()
input = open('input.txt').read()
data = parser.run(input)
result = code_generate(data[0], data[1])
print(result)
