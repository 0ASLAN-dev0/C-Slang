#!/usr/bin/env python

import re
import os
import sys
import keyboard

# Token definitions
TOKEN_REGEX = [
    ("KEYWORD", r"\b(func|int|float|bool|nbool|char|string|local|print|read|return|if|elif|else|while|for|break|continue|null|true|false)\b"),
    ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("NUMBER", r"\d+(\.\d+)?"),
    ("STRING", r'"[^"\\]*(\\.[^"\\]*)*"'),
    ("CHAR", r"'[^'\\]*(\\.[^'\\]*)*'"),
    ("OPERATOR", r"\+=|\-=|\*=|/=|%=|\+|\-|\*|\/|==|!=|<=|>=|=|<|>"),
    ("SEMICOLON", r";"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("COMMA", r","),
    ("MLCOMMENT", r"##(?:.|\n)*?##"),
    ("COMMENT", r"#.*"),
    ("WHITESPACE", r"\s+"),
]

class Tokenizer:
    def __init__(self, code: str):
        self.code = code
        self.tokens = []

    def tokenize(self):
        code = self.code
        while code:
            for token_type, pattern in TOKEN_REGEX:
                regex = re.compile(pattern)
                match = regex.match(code)
                if match:
                    value = match.group(0)
                    if token_type != "WHITESPACE":
                        self.tokens.append((token_type, value))
                    code = code[len(value):]
                    break
            else:
                raise SyntaxError(f"Unexpected token: {code[0]}")
        return self.tokens

class CSlangTranspiler:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.output = ['#include <stdio.h>']
        self.variables = {}
        self.functions = {}
        self.indentation_level = 0

    def current(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def previous(self):
        return self.tokens[self.i - 1] if self.i > 0 else (None, None)

    def advance(self):
        self.i += 1
        return self.previous()

    def peek(self, offset=1):
        # Correctly call self.current() to get the current token and then lookahead by 'offset'
        lookahead_index = self.i + offset
        if lookahead_index < len(self.tokens):
            return self.tokens[lookahead_index]
        return None

    def match(self, expected_type, expected_value=None):
        token_type, token_value = self.current()
        if token_type == expected_type and (expected_value is None or token_value == expected_value):
            return self.advance()[1]
        return None

    def check(self, expected_type, expected_value=None):
        token_type, token_value = self.current()
        return token_type == expected_type and (expected_value is None or token_value == expected_value)

    def consume(self, expected_type, error_message):
        if self.check(expected_type):
            return self.advance()
        raise SyntaxError(f"[Line {self.i}] {error_message}")

    def indent(self):
        return "\t" * self.indentation_level

    def parse(self):
        while self.i < len(self.tokens):
            self.parse_statement()

        return "\n".join(self.output)

    def parse_statement(self):
        token_type, token_value = self.current()

        if token_type in ("COMMENT", "MLCOMMENT"):
            self.parse_comment()
            return

        if token_type == "KEYWORD" and token_value in ("int", "float", "bool", "nbool", "char", "string"):
            self.parse_variable_declaration()
        elif token_type == "KEYWORD" and token_value == "print":
            self.parse_print_statement()
        elif token_type == "KEYWORD" and token_value == "read":
            self.parse_read_statement()
        elif token_type == "KEYWORD" and token_value == "func":
            self.parse_function_definition()
        elif token_type == "IDENTIFIER":
           # Look ahead to see if it's an assignment-like operator
           operator = self.peek(1)
           
           if operator:
               operator_type, operator_value = operator  # Unpack token (type, value)
               
               # Check if it's an assignment operator
               if operator_type == "OPERATOR" and operator_value in ("=", "+=", "-=", "*=", "/=", "%="):
                   return self.parse_assignment(operator_value)  # Pass actual operator string
           
           return self.parse_function_call_or_variable()  # Handle function call or variable reference


        elif token_type == "KEYWORD" and token_value in ("if", "elif", "else"):
            self.parse_conditional()
        elif token_type == "KEYWORD" and token_value in ("while", "for"):
            self.parse_loop()
        elif token_type == "KEYWORD" and token_value in ("break", "continue"):
            self.parse_break_continue()
        elif token_type == "KEYWORD" and token_value == "return":
            self.parse_return_statement()
        else:
            self.advance()

    def parse_return_statement(self):
        self.match("KEYWORD", "return")
        if self.current() != ("SEMICOLON", ";"):
            expr = self.parse_expression()
            self.output.append(f"{self.indent()}return {expr};")
        else:
            self.output.append(f"{self.indent()}return;")
        self.match("SEMICOLON")



    def parse_variable_declaration(self):
        var_type = self.match("KEYWORD")
        var_name = self.match("IDENTIFIER")
        c_type = self.map_type(var_type)
        self.variables[var_name] = var_type

        code_line = f"{self.indent()}{c_type} {var_name}"
        if self.match("OPERATOR", "="):
            expr = self.parse_expression()
            code_line += f" = {expr}"
        code_line += ";"
        self.match("SEMICOLON")
        self.output.append(code_line)

    def parse_print_statement(self):
        self.match("KEYWORD", "print")
        self.match("LPAREN")

        format_parts = []
        values = []

        while not self.check("RPAREN"):
            token_type, token_value = self.current()
            if token_type == "STRING":
                format_parts.append(token_value[1:-1].replace("%", "%%").replace('"', '\\"'))
                self.advance()
            elif token_type == "IDENTIFIER":
                var_type = self.variables.get(token_value, "int")  # Default to int if type not found
                fmt = self.format_specifier(var_type)
                format_parts.append(fmt)
                values.append(token_value)
                self.advance()
            elif token_type == "OPERATOR" and token_value == "+":
                self.advance()
            else:
                self.advance()

        self.match("RPAREN")
        self.match("SEMICOLON")

        format_string = ' '.join(format_parts)
        args = ', '.join(values)
        if args:
            self.output.append(f'{self.indent()}printf("{format_string}\\n", {args});')
        else:
            self.output.append(f'{self.indent()}printf("{format_string}\\n");')

    def parse_read_statement(self):
       self.match("KEYWORD", "read")
       self.match("LPAREN")
       prompt = self.match("STRING")
       self.match("COMMA")
       var_name = self.match("IDENTIFIER")
       self.match("RPAREN")
       self.match("SEMICOLON")

       var_type = self.variables.get(var_name, "int")  # Default to int if type not found
       scanf_specifier = self.scanf_specifier(var_type)

       self.output.append(f'{self.indent()}printf({prompt});')
       self.output.append(f'{self.indent()}scanf("{scanf_specifier}", &{var_name});')

    def scanf_specifier(self, var_type):
       if var_type == "string":
           return "%s"
       elif var_type == "float":
           return "%f"
       elif var_type == "bool":
           return "%d"  # For booleans, we use %d
       elif var_type == "int":
           return "%d"
       else:
           return "%s"  # Default to string if unknown type


    def format_specifier(self, var_type):
        if var_type == "string":
            return "%s"
        elif var_type == "float":
            return "%f"
        elif var_type == "bool":
            return "%d"  # For booleans, we use %d (1 for true, 0 for false)
        elif var_type == "int":
            return "%d"
        else:
            return "%s"  # Default to string if unknown type

    def parse_function_definition(self):
        self.match("KEYWORD", "func")
        func_name = self.match("IDENTIFIER")
        self.match("LPAREN")

        params = []
        while not self.check("RPAREN"):
            param_type = self.match("KEYWORD")  # e.g., int, float
            param_name = self.match("IDENTIFIER")
            params.append(f"{param_type} {param_name}")
            if not self.check("RPAREN"):
                self.match("COMMA")
        self.match("RPAREN")
        self.match("LBRACE")

        self.functions[func_name] = params  # Store full param strings with type
        self.output.append(f"int {func_name}({', '.join(params)}) {{")
        self.indentation_level += 1

        while not self.check("RBRACE"):
            self.parse_statement()

        self.indentation_level -= 1
        self.match("RBRACE")
        self.output.append(f"{self.indent()}}}")





    def parse_function_call_or_variable(self):
        identifier = self.match("IDENTIFIER")

        # Check if the identifier is followed by an opening parenthesis (function call)
        if self.check("LPAREN"):
            self.match("LPAREN")
            args = []

            # Parse function arguments
            while not self.check("RPAREN"):
                arg = self.parse_expression(stop_tokens={"COMMA", "RPAREN"})
                args.append(arg)
                if self.check("COMMA"):
                    self.match("COMMA")

            self.match("RPAREN")
            return f"{identifier}({', '.join(args)})"
        else:
            # It's just a variable or an expression involving a variable
            return identifier

    def parse_conditional(self):
        keyword = self.match("KEYWORD")
        if keyword in ("if", "elif"):
            self.match("LPAREN")
            condition = self.parse_expression()
            self.match("RPAREN")
            self.match("LBRACE")
            c_keyword = "if" if keyword == "if" else "else if"
            self.output.append(f"{self.indent()}{c_keyword} ({condition}) {{")
            self.indentation_level += 1
            while not self.check("RBRACE"):
                self.parse_statement()
            self.indentation_level -= 1
            self.match("RBRACE")
            self.output.append(f"{self.indent()}}}")
            if self.check("KEYWORD") and self.current()[1] in ("elif", "else"):
                self.parse_conditional()
        elif keyword == "else":
            self.match("LBRACE")
            self.output.append(f"{self.indent()}else {{")
            self.indentation_level += 1
            while not self.check("RBRACE"):
                self.parse_statement()
            self.indentation_level -= 1
            self.match("RBRACE")
            self.output.append(f"{self.indent()}}}")

    def parse_loop(self):
        if self.match("KEYWORD", "while"):
            self.match("LPAREN")
            condition = self.parse_expression()
            self.match("RPAREN")
            self.match("LBRACE")
            self.output.append(f"{self.indent()}while ({condition}) {{")
            self.indentation_level += 1
            while not self.check("RBRACE"):
                self.parse_statement()
            self.indentation_level -= 1
            self.match("RBRACE")
            self.output.append(f"{self.indent()}}}")
    
        elif self.match("KEYWORD", "for"):
            self.match("LPAREN")
            init = self.parse_expression()
            self.match("SEMICOLON")
            cond = self.parse_expression()
            self.match("SEMICOLON")
            inc = self.parse_expression()
            self.match("RPAREN")
    
            if self.check("KEYWORD", "do"):
                self.advance()
    
            self.match("LBRACE")
            self.output.append(f"{self.indent()}for ({init}; {cond}; {inc}) {{")
            self.indentation_level += 1
            while not self.check("RBRACE"):
                self.parse_statement()
            self.indentation_level -= 1
            self.match("RBRACE")
            self.output.append(f"{self.indent()}}}")

    def parse_comment(self):
        if self.check("COMMENT"):
            comment = self.advance()[1]
            cleaned = comment.lstrip("#").strip()
            formatted_comment = f"{self.indent()}// {cleaned}"
            self.output.append(formatted_comment)

        elif self.check("MLCOMMENT"):
            comment = self.advance()[1]
            cleaned = comment.strip("#")
            lines = cleaned.strip().splitlines()

            start_comment = f"{self.indent()}/*"
            self.output.append(start_comment)

            for line in lines:
                stripped_line = line.strip()
                formatted_line = f"{self.indent()}  * {stripped_line}"
                self.output.append(formatted_line)

            end_comment = f"{self.indent()} */"
            self.output.append(end_comment)



    def parse_assignment(self, operator):
        # Handle all types of assignment operators
        if operator == "=":
            # Handle basic assignment (e.g., a = 5)
            left = self.match("IDENTIFIER")
            self.match("OPERATOR")  # '=' token
            right = self.parse_expression()  # Parse the expression on the right
            self.output.append(f"{self.indent()}{left} = {right};")  # Transpile assignment
        elif operator == "+=":
            # Handle compound assignment (e.g., a += 1)
            left = self.match("IDENTIFIER")
            self.match("OPERATOR")  # Check for the correct assignment operator token
            right = self.parse_expression()
            self.output.append(f"{self.indent()}{left} += {right};")
        elif operator == "-=":
            left = self.match("IDENTIFIER")
            self.match("OPERATOR")
            right = self.parse_expression()
            self.output.append(f"{self.indent()}{left} -= {right};")
        elif operator == "*=":
            left = self.match("IDENTIFIER")
            self.match("OPERATOR")
            right = self.parse_expression()
            self.output.append(f"{self.indent()}{left} *= {right};")
        elif operator == "/=":
            left = self.match("IDENTIFIER")
            self.match("OPERATOR")
            right = self.parse_expression()
            self.output.append(f"{self.indent()}{left} /= {right};")
        elif operator == "%=":
            left = self.match("IDENTIFIER")
            self.match("OPERATOR")
            right = self.parse_expression()
            self.output.append(f"{self.indent()}{left} %= {right};")
        else:
            # Raise an error for unsupported assignment operators
            raise Exception(f"Unsupported assignment operator: {operator}")




    def parse_break_continue(self):
        stmt = self.match("KEYWORD")
        self.match("SEMICOLON")
        self.output.append(f"{self.indent()}{stmt};")

    def parse_expression(self, stop_tokens={"SEMICOLON", "COMMA", "RPAREN"}):
        expr = []
        while self.current() is not None and self.current()[0] not in stop_tokens:
            token_type, token_value = self.current()

            if token_type == "IDENTIFIER":
                next_token_type, next_token_value = self.tokens[self.i + 1] if self.i + 1 < len(self.tokens) else (None, None)
                if next_token_type == "LPAREN":
                    expr.append(self.parse_function_call_or_variable())
                    continue
                else:
                    expr.append(token_value)
                    self.advance()
                    continue

            if token_value in {"+", "-", "*", "/", "%"}:
                next_index = self.i + 1
                if next_index < len(self.tokens):
                    _, next_token_value = self.tokens[next_index]
                    if next_token_value == "=":
                        expr.append(token_value + "=")
                        self.i += 2
                        continue

            expr.append(token_value)
            self.advance()

        return " ".join(expr)

    def map_type(self, cslang_type):
        type_map = {
            "int": "int",
            "float": "float",
            "bool": "bool",
            "nbool": "bool",
            "char": "char",
            "string": "char*",
        }
        return type_map.get(cslang_type, "int")

    def format_specifier(self, var_type):
        if var_type == "int":
            return "%d"
        elif var_type == "float":
            return "%f"
        elif var_type == "bool":
            return "%d"
        elif var_type == "char":
            return "%c"
        elif var_type == "string":
            return "%s"
        return "%d"

def transpile_cslang(file_path):
    """ Function to transpile the C-Slang file to C code """
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return

    # Read the contents of the C-Slang file
    with open(file_path, 'r') as file:
        cslang_code = file.read()

    # Tokenize the C-Slang code
    tokens = Tokenizer(cslang_code).tokenize()

    # Transpile to C code
    transpiled_code = CSlangTranspiler(tokens).parse()


    # print(transpiled_code)

    # Save the transpiled C code to a new .c file in the same directory
    output_file_path = os.path.splitext(file_path)[0] + ".c"
    with open(output_file_path, 'w') as output_file:
        output_file.write(transpiled_code)

    print(f"Transpiled C code has been saved to: {output_file_path}")

def main():
    # Check if the script is called with the file path as an argument
    if len(sys.argv) != 2:
        print("Usage: transpilecsl <path-to-csl-file>")
        sys.exit(1)

    # Get the file path from the command line argument
    file_path = sys.argv[1]

    transpile_cslang(file_path)

    # Optionally, check if ESC key is pressed to break the loop
    if keyboard.is_pressed('esc'):
        print("Exiting...")

if __name__ == "__main__":
    main()
