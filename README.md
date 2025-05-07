# C-Slang ~  
C-Slang is a **minimalist, Lua-C hybrid programming language** created for fun and experimentation. It combines the simplicity of Lua with the structure of C, designed to feel familiar yet quirky.

> ⚠️ This is a toy language. It’s not production-ready, but it’s a cool little project to mess around with.

---

## 🚀 Features

- C-style syntax with a sprinkle of Lua vibes
- Basic types: `int`, `float`, `bool`, `char`, `string`
- Functions, loops (`while`, `for`), conditionals (`if`, `elif`, `else`)
- `print(...)` and `read(...)` for I/O
- Basic expressions and arithmetic
- Single-line and multi-line comments
- WIP EBNF grammar with future plans for arrays and structs

---

## 🔧 Transpiler to C

I wrote a **basic transpiler** that converts `.csl` files into C code.

### How to Use

1. **Clone the repo:**
   ```bash
   git clone https://github.com/0ASLAN-dev0/C-Slang.git
   cd C-Slang
````

2. **Install the transpiler:**

   ```bash
   pip install .
   ```

3. **Transpile a `.csl` file:**

   ```bash
   transpilercsl path/to/your_file.csl
   ```

This will output a `.c` file in the same directory.

---

## 😅 Known Issues

* The transpiler is **incomplete**
* Some language features aren't supported yet.
* Error handling is minimal to non-existent.
* Parsing could be way more robust.

Basically: it kinda works... Mostly.

---

## ❤️ Contributions Welcome

I would **greatly appreciate** any contributions to this project!
Bug fixes, improvements, refactoring, or even better — **a real compiler** — would be amazing.

If you're into building languages, parsers, or compilers, feel free to fork and build something better out of this.

---

## 📜 License

[MIT](LICENSE) — do whatever you want (with credits of course).

---

Made with ❤️ by [0ASLAN-dev0](https://github.com/0ASLAN-dev0)
