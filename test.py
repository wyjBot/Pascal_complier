from Parser.Parser import Parser
from Generate.program import code_generate

parser = Parser()
input = open('test/example.pas').read()
data = parser.run(input)
result = code_generate(data[0], data[1])
with open("test/example.ast","w+") as fw:
  fw.write(data[0])
with open("test/example.symTable","w+") as fw:
  fw.write(data[1])
with open("test/example.c","w+") as fw:
  fw.write(result)
