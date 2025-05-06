# C-Slang

C-Slang is a simple, lightweight, and beginner-friendly programming language designed to be easy to learn and use. Inspired by C-style syntax, it provides essential features for writing clean and efficient code while maintaining simplicity and flexibility. C-Slang code is **transpiled** into C, allowing you to run your programs using a C compiler.

## Features
- **Basic Data Types**: Supports `int`, `float`, `bool`, `char`, `string`, and more advanced types like arrays and structs.
- **Control Flow**: Includes conditionals (`if`, `else`, `elif`) and loops (`while`, `for`) for controlling program execution.
- **Function Definitions and Calls**: Define functions with parameters, return types, and use them throughout your program.
- **Input/Output**: Built-in `read` for user input and `print` for output with automatic type conversion for non-string values.
- **Clean Syntax**: Easy-to-understand syntax inspired by popular C-style languages, with support for basic operations like arithmetic, logical comparisons, and unary operations.
- **Transpiling to C**: C-Slang code is transpiled into C code, which you can then compile and run using a C compiler.

## Example Code

C-Slang:

```cslang
func main() {
    int x = 10;
    int y = 5;
    if (x > y) {
        print("x is greater than y");
    } else {
        print("y is greater than or equal to x");
    }
}
````

### Output:

```
x is greater than y
```

After transpiling, the equivalent C code will look like this:

```c
#include <stdio.h>

void main() {
    int x = 10;
    int y = 5;
    if (x > y) {
        printf("x is greater than y\n");
    } else {
        printf("y is greater than or equal to x\n");
    }
}
```

## Installation

To use C-Slang, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/0ASLAN-dev0/C-Slang.git
   ```

2. Navigate to the project directory:

   ```bash
   cd C-Slang
   ```

3. **Transpile** your C-Slang code into C using the transpiler provided in the repository:

   ```bash
   python transpile.py
   ```

   This will prompt you to enter the path to your c-slang file. After you hit enter it will generate the equivalent C code from your C-Slang program.

4. **Compile** the generated C code using a C compiler (e.g., GCC):

   ```bash
   gcc -o your_program your_code.c
   ```

5. Run the program:

   ```bash
   ./your_program
   ```

## Syntax Overview

C-Slang follows a C-style syntax with the following key constructs:

### Variables:

```cslang
int x = 10;
float pi = 3.14;
bool isValid = true;
string name = "C-Slang";
```

### Functions:

```cslang
func add(int a, int b) {
    return a + b;
}

int result = add(3, 4);
print(result); # 7
```

### Conditionals:

```cslang
if (x > y) {
    print("x is greater than y");
} else {
    print("x is not greater than y");
}
```

### Loops:

```cslang
for (int i = 0; i < 5; i = i + 1) {
    print(i);
}
```

### Input/Output:

```cslang
string userInput = read("Enter something: ");
print("You entered: " + userInput);
```

### Comments:

* **Single-line comments**: Start with `#`
* **Multiline comments**: Use `##` for blocks of comments

```cslang
# This is a single-line comment
##
This is a multiline comment
##
```

## Contributing

I welcome contributions to C-Slang! If you'd like to contribute, please fork the repository and submit a pull request with your changes. Make sure to follow the code style and include tests for any new features or bug fixes.


I would also really appreciate if someone makes a dedicated compiler for this language, I will add that compiler to this repository and add the creator as contributer.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify or add additional sections, such as more examples or instructions, as needed for your repository!
