# HP 16C Emulator

This is a **work-in-progress emulator** of the **HP 16C** Programmer's Calculator, developed in **Python** and set up as a **Visual Studio 2022 project**. It aims to replicate all the features of the original calculator, including RPN stack, number base conversions, bitwise operations, word size selection, and memory registers.

## Features
- **RPN (Reverse Polish Notation) Stack**
- **Number Base Switching**: Decimal, Hexadecimal, Octal, and Binary
- **Bitwise Operations**: AND, OR, XOR, NOT, Shift Left/Right
- **Word Size Selection**: Supports 4-bit to 64-bit modes
- **Memory Registers**: Store and recall values
- **Error Handling**: Emulates original calculator behavior
- **Graphical Interface**: Uses a modern UI to replicate the HP 16C layout

## Installation & Setup
### Prerequisites
- **Windows 11** (Recommended, but should work on other versions)
- **Visual Studio 2022** with Python support
- **Python 3.10+**
- **pip** installed for dependencies

### Setup Instructions
1. **Clone the repository**:
   ```sh
   git clone https://github.com/globey-code/HP-16c.git
   cd HP-16C-Emulator
   ```
2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
3. **Open in Visual Studio**:
   - Open `HP 16C.sln` in Visual Studio 2022
   - Set `main.pyw` as the startup file
4. **Run the Emulator**:
   - Press `F5` to start the emulator inside Visual Studio

## Usage
- Use the on-screen buttons to operate the calculator, just like the original HP 16C.
- Keyboard shortcuts (if implemented) will be listed here.

## Building the Project (Creating an EXE)
To generate a standalone Windows executable:
```sh
pyinstaller --onefile --windowed main.pyw
```
This will create an `exe` file in the `dist` folder.

## Contributing
Contributions are welcome! Follow these steps:
1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature-name`)
3. **Commit your changes**
4. **Push to your branch** and open a Pull Request

## License
This project is licensed under the MIT License.

## Credits
Developed by [Globey-Code](https://github.com/globey-code).
