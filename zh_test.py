import pytest

from Parser.Parser import Parser
from Generate.program import code_generate


class TestLex:
    def test_lex_one(self):

        input = open('test/lex_test/test0').read()

        result = open('test/lex_test/result_test0').read()
        assert runALl(input) == result

    def test_lex_two(self):
        input = open('test/lex_test/test1').read()

        result = ''''''

        assert runALl(input) == result

    def test_lex_three(self):
        input = open('test/lex_test/test2').read()

        result = ''''''
        assert runALl(input) == result

    def test_lex_four(self):
        input = open('test/lex_test/test3').read()

        result = ''''''
        assert runALl(input) == result

    def test_lex_five(self):
        input = open('test/lex_test/test4').read()

        result = ''''''
        assert runALl(input) == result

    def test_lex_six(self):
        input = open('test/lex_test/test5').read()

        result = ''''''
        assert runALl(input) == result

class TestPaser:
    def test_paser_one(self):
        input = open('test/paser_test/test0').read()

        result = ''''''
        assert runALl(input) == result

    def test_paser_two(self):
        input = open('test/paser_test/test1').read()

        result = ''''''
        assert runALl(input) == result

    def test_paser_three(self):
        input = open('test/paser_test/test2').read()

        result = ''''''
        assert runALl(input) == result

    def test_paser_four(self):
        input = open('test/paser_test/test3').read()

        result = ''''''
        assert runALl(input) == result

    def test_paser_five(self):
        input = open('test/paser_test/test4').read()

        result = ''''''
        assert runALl(input) == result

    def test_paser_six(self):
        input = open('test/paser_test/test5').read()

        result = ''''''
        assert runALl(input) == result

def runALl(input):
    parser = Parser()
    data = parser.run(input)
    result = code_generate(data[0], data[1])
    return result



