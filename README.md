
Архитекутра компьютера - Лабораторная №3
======

Выполнил
---

Анисимов Максим Дмитриевич P3233

Вариант (упрощённый)
---

> Базовый вариант: alg | risc | neum | hw | instr | binary | stream | mem | pstr | prob1 | cache
>
> Вариант после упрощения: asm | risc | neum | hw | instr | struct | stream | mem | pstr | prob1 | cache

Синтаксис языка
---

Синтаксис в расширенной БНФ

* `[...]` - вхождение 0 или 1 раз
* `{...}` - вхождение 0 или несколько раз
* `{...}`- - вхождение 1 или несколько раз

Форма Бэкуса-Наура


```bash

program ::= { program_line }-

program_line ::= code_line [ comment ]

code_line ::=  data_label ":" 
        | insruction 
        | data

data ::= ".word" variable

variable ::= integer
       | string
       | label_name

instruction ::= op0 
       | op1 register 
       | op2 register "," register
       | op3 address
       | op4 register, address
       | op4 address, register

address ::= label_name | "(" label_name ")"

label_name ::= <any of "a-z A-Z"> { <any of "a-z A-Z 0-9 _ "> }

register ::= "r" <any of "0-3">

op0 ::= "nop" 
      | "hlt" 

op1 ::= "inc" 
      | "dec"

op2 ::= "add" 
      | "sub"
      | "mul"
      | "div"	
      | "mod"
      | "test"
      
op3 ::= "jg" 
      | "jng"
      | "jz" 
      | "jnz" 
      | "jmp"

op4 ::= "mov"

integer :: = [ "-" ] { <any of "0-9"> }-

positive_integer :: = { <any of "0-9"> }-

string ::= "\'" { <any of "a-z A-Z">}- "\'"

comment ::= ";" { <any symbol except "\n"> }

```
**Команды:**

1. op0 (Безадресные команды)

    * `nop` - нет операции
    * `hlt` - остановка работы программы


2. op1 (Адресные команды)

    * `inc { register }` - операция инкрементации значения в регистре
    * `dec { register }` - операция декрментации значения в регистре


3. op2 (Адресные команды)

    * `add { register register }` - сложение первого и второго регистра
    * `sub { register register }` - вычитание первого и второго регистра
    * `mul { register register }` - умножение первого и второго регистра
    * `div { register register }` - деление первого регистра на второй
    * `mod { register register }` - нахождение остатка деления первого регистра на второй
    * `test {register register}` - логическое умножение двух регистров


4. op3 (Команды ветвления)

    * `jg { label_name }` - переход по адресу label_name, если флаг N = 0 (Результат вычислений положительный)
    * `jng { label_name }` - переход по адресу label_name, если флаг N != 0 (Результат вычислений отрицательный)
    * `jz {label_name }` - переход по адресу label_name если флаг Z = 0 (Результат вычислений равен 0)
    * `jnz { label_name }` - переход на указанную метку если Z != 0 (Результат вычислений не равен 0)
    * `jmp { label_name }` - безусловный переход по адресу


5. op4 (Адресная команда)

    * `mov { register, address }` - загрузить значение из address в register
    * `mov { address, register }` - загрузить значение из register в address

**Семантика:**

* Глобальная видимость данных
* Есть поддержка литералов (Чисельных и строковых)
  * Пример объявления литерала: `.word 10000` или `.word 'Hello world!'`
* Строки хранятся в виде `Паскаль-подобных` (Сначала идёт длина строки, потом сама строка)
* Метка `_start` является началом программы
* Текст, написанный после `;` является комментарием
* Выполнение кода происходит последовательно. Возможен переход на другие участки кода при помощи команд ветвления. Поддержка подпрограмм отсутствует

Организация памяти
---

* Архитектура фон-Неймана
* Машинное слово - не определено

```bash

          registers    
+----------------------------+
| r0: general register       |
| r1: general register       |
| r2: general register       |
| r3: general register       |
| ip: counter                |
| ar: address register       |
| dr: data register          |
| ps: program state register |
+----------------------------+

            memory
+----------------------------+
| 00:  start address (n)     |
| 01:  input port            |
| 02:  output str port       |
| 03:  output int port       |   
| 04:       ...
|      variables space       |
|           ...              |
| n:   program start         |
|           ...              |
+----------------------------+

```

* В ячейке `00` лежит адрес начала программы
* В ячейках `01`, `02`, `03` хранятся порты ввода-вывода
* В ячейках с `03` по `n` хранятся переменные, используемые в программе:
    * Целочисельные
    * Строковые

**Адресация памяти:**

* Асболютная адресация
* Косвенная адресация

Система команд
---

**Особенности процессора:**

* Машинное слово - не определено. Инструкции хранятся как высокоуровневая структура
* Пользователь может оперировать только четырьмя регистрами общего назначения `r0 - r3`. Служебные регистры используются самим процессором
* Ввод-вывод осуществляется асинхронно. В качестве устройства для ввода-вывода используются 3 ячейки общей памяти: одна для ввода, две другие для вывода целочисельных и строковых данных
* Поток управления:
  * Поддерживаются условные и безусловные переходы. Если условие перехода не выполняется, то осуществляется инкрементация регистра `IP`

**Кодирование инструкций:**

* Машинный код сериализуется в список JSON
* Один элемент списка - однак инструкция
Пример:

```json

[
   {
     "index": 0,
     "opcode": "add",
     "arg_1": "r0",
     "is_indirect_1": false,
     "arg_2": "r1",
     "is_indirect_2": false
   }
]

```

где:

* `index` - адрес памяти
* `opcode` - код операции
* `arg_1` - первый аргумент
* `is_indirect_1` - косвенная ли адресация для arg_1
* `arg_2` - второй аргумент
* `is_indirect_2` - косвенная ли адресация для arg_2
  Типы данных в модуле isa, где:
* `Opcode` - перечсление кодов операции

Транслятор
---

Интерфейс командной строки: `python translator.py <source_file> <target_file>`
Реализовано в модуле: [translator.py](https://github.com/MyximAnisimov/CSA-lab3/blob/main/translator.py)
Этапы трансляции (функция `translate`):

1. Очистка исходного текста от лишних пробелов, комментариев и пустых строк (функция `clean_source`)
2. Выделение переменных программы (функция `translate_section_data`)
3. Выделение меток (функция `translate_section_text_stage_1`)
4. Выделение команд (функция `translate_section_text_stage_2`)
5. Трансляция переменных в бинарный код (функция `translate_variables`)
6. Трансляция команд в бинарный код (функция `translate_commands`)
7. Объединение результатов двух последних шагов и формирование машинного кода

Правила трансляции в машинный код:

* Одна переменная - одна строка
* Одна команда - одна строка
* Ошибку компиляции вызовет:
    * Любая незивестная команда
    * Использование меток или целых чисел во всех командах, кроме команды `mov`
    * Незивестная метка
    * Повторное задание метки
    * Некорректный тип данных в слове `.word`
    * Двойная косвенная адресация в командах с двумя переменными
    * Косвенная адресация с использованием регистров

Модель процессора
---

Интерфейс командной строки: `machine.py <machine_code_file> <input_file>`

Реализовано в модуле: [machine](https://github.com/MyximAnisimov/CSA-lab3/blob/main/machine.py)

**DataPath**


![Image alt](https://github.com/MyximAnisimov/CSA-lab3/tree/main/schemes/DataPath.svg)

Реализован в классе `DataPath`

`memory` - однопортовая память, чтение и запись выполняются поочерёдно

Регистры (соответствуют регистрам на схеме):

* `Registers` - регистры общего назначения
    * `r0`
    * `r1`
    * `r2`
    * `r3`

* Служебные регистры
    * `pc` - счетчик команд
    * `ps` - регистр состояния
    * `ar` - адресный регистр
    * `ir` - регистр команды
    * `dr` - регистр данных, нужен при косвенной адресации

Объекты:

* `input_buffer` - входной буфер данных
    * адрес в памяти = 1
  
* `output_symbol_buffer` - выходной буфер для символов
    * адрес в памяти = 2

* `output_numeric_buffer` - выходной буфер для чисел
    * адрес в памяти = 3

* `alu` - арифметико-логическое устройство
    * мультиплексоры реализованы в виде Enum (Selectors) в модуле isa
    * операции алу реализованы в виде Enum (ALUOpcode) в модуле isa

Сигналы (реализованы в виде методов класса `DataPath`):

* `signal_fill_memory` - заполнить память программой
* `signal_latch_<reg>` - защелкнуть регистр `<reg>`
* `signal_write` - записать в память по адресу в `ar`
* `signal_execute_operation_on_alu` - записать в память по адресу в `ar`

**Control Unit**

![Image alt](https://github.com/MyximAnisimov/CSA-lab3/tree/main/schemes/ControlUnit.png)

Реализован в классе `ControlUnit`

* Hardwired (реализовано полностью на Python)
* Метод decode_and_execute_instruction моделирует выполнение полного цикла инструкции

Особенности работы модели:

* Цикл симуляции осуществляется в функции `simulation`
* Шаг моделирования соответствует одной инструкции с выводом состояния в журнал (каждая запись в журнале соответсвует состоянию процессора после выполнения инструкции)
* Для журнала состояний процессора используется стандартный модуль `logging`

Тестирование
---

Реализованные программы:

[hello](https://github.com/MyximAnisimov/CSA-lab3/blob/main/examples/src/hello.asm) - напечатать hello world
[cat](https://github.com/MyximAnisimov/CSA-lab3/blob/main/examples/src/cat.asm) - печатать данные, поданные на вход симулятору через файл ввода (размер ввода потенциально бесконечен)
[hello_user_name](https://github.com/MyximAnisimov/CSA-lab3/blob/main/examples/src/hello_user_name.asm) - запросить у пользователя его имя, считать его, вывести на экран приветствие
[prob1](https://github.com/MyximAnisimov/CSA-lab3/blob/main/examples/src/prob2.asm) - вывести сумму чисел до 1000, кратных 3 или 5
Интеграционные тесты реализованы в integration_test:

Стратегия: golden tests, конфигурация в папке [golden](https://github.com/MyximAnisimov/CSA-lab3/tree/main/golden)

**CI при помощи Github Action**

```

name: Python CI

on:
  push:
    branches:
      - main
    paths:
      - ".github/workflows/*"
      - "**/*.py"
  pull_request:
    branches:
      - main
    paths:
      - ".github/workflows/*"
      - "**/*.py"

defaults:
  run:
    working-directory: ./

jobs:

  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12.3"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Run tests and collect coverage
        run: |
          poetry run coverage run -m pytest .
          poetry run coverage report -m
        env:
          CI: true

  mypy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12.3"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Check code formatting with Mypy
        run: poetry run mypy .

  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12.3"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Check code formatting with Ruff
        run: poetry run ruff format --check .

      - name: Run Ruff linters
        run: poetry run ruff check .
```
где:

* `poetry` - управление зависимостями
* `coverage` - формирование отчёта об уровне покрытия исходного кода
* `pytest` - утилита для запуска тестов
* `ruff` - линтер для проверки соответствия "хорошим практикам" программирования
* `mypy` - проверка строгой типизации, при наличии

**Пример использования:**

Пример использования и журнал работы процессора на продемонстрирован на примере `cat`

```text

C:\Users\user\CSA-lab3\examples\inputs\cat.txt
[12, 'H', 'e', 'l', 'l', 'o', ' ', 'W', 'o', 'r', 'l', 'd', '!']

C:\Users\user\CSA-lab3\examples\inputs\cat.asm
 in_addr:
   .word 1

 out_addr:
   .word 2

 _start:
   mov r0, (in_addr)
   mov r1, r0
  loop:
   dec r1
   jng exit
   inc r1
   mov r2, (in_addr)
   dec r1
   jg write
   hlt

 write:
   mov (out_addr), r2
   jmp loop

 exit:
     hlt

C:\Users\user\CSA-lab3> poetry run translator.py examples\src\cat.asm examples\machine_codes\cat.json
source LoC: 24 code instr: 15

C:\Users\user\CSA-lab3> type examples\machine_codes\cat.json    
[{"index": 0, "opcode": "jmp", "arg_1": "6", "is_indirect_1": false, "arg_2": null, "is_indirect_2": null},
 {"index": 4, "opcode": "nop", "arg_1": "1", "is_indirect_1": false, "arg_2": null, "is_indirect_2": null},
 {"index": 5, "opcode": "nop", "arg_1": "2", "is_indirect_1": false, "arg_2": null, "is_indirect_2": null},
 {"index": 6, "opcode": "mov", "arg_1": "r0", "is_indirect_1": false, "arg_2": "4", "is_indirect_2": true},
 {"index": 7, "opcode": "mov", "arg_1": "r1", "is_indirect_1": false, "arg_2": "r0", "is_indirect_2": false},
 {"index": 8, "opcode": "dec", "arg_1": "r1", "is_indirect_1": false, "arg_2": null, "is_indirect_2": null},
 {"index": 9, "opcode": "jng", "arg_1": "17", "is_indirect_1": false, "arg_2": null, "is_indirect_2": null},
 {"index": 10, "opcode": "inc", "arg_1": "r1", "is_indirect_1": false, "arg_2": null, "is_indirect_2": null},
 {"index": 11, "opcode": "mov", "arg_1": "r2", "is_indirect_1": false, "arg_2": "4", "is_indirect_2": true},
 {"index": 12, "opcode": "dec", "arg_1": "r1", "is_indirect_1": false, "arg_2": null, "is_indirect_2": null},
 {"index": 13, "opcode": "jg", "arg_1": "15", "is_indirect_1": false, "arg_2": null, "is_indirect_2": null},
 {"index": 14, "opcode": "hlt", "arg_1": null, "is_indirect_1": null, "arg_2": null, "is_indirect_2": null},
 {"index": 15, "opcode": "mov", "arg_1": "5", "is_indirect_1": true, "arg_2": "r2", "is_indirect_2": false},
 {"index": 16, "opcode": "jmp", "arg_1": "8", "is_indirect_1": false, "arg_2": null, "is_indirect_2": null},
 {"index": 17, "opcode": "hlt", "arg_1": null, "is_indirect_1": null, "arg_2": null, "is_indirect_2": null}]

C:\Users\user\CSA-lab3> poetry run machine.py examples\machine_codes\cat.json examples\inputs\cat.txt         
 DEBUG    machine.py     INSTR: jmp 6        | R0:        0 | R1:        0 | R2:        0 | R3:        0 | N: 0 | Z: 0 | PC:    6
 DEBUG    machine.py    input: 12
 DEBUG    machine.py     INSTR: mov r0, (4)  | R0:       12 | R1:        0 | R2:        0 | R3:        0 | N: 0 | Z: 0 | PC:    7     
 DEBUG    machine.py     INSTR: mov r1, r0   | R0:       12 | R1:       12 | R2:        0 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:       11 | R2:        0 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:       11 | R2:        0 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:       12 | R2:        0 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'H'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:       12 | R2:       72 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:       11 | R2:       72 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:       11 | R2:       72 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: '' << 'H'
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:       11 | R2:       72 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:       11 | R2:       72 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:       10 | R2:       72 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:       10 | R2:       72 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:       11 | R2:       72 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'e'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:       11 | R2:      101 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:       10 | R2:      101 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:       10 | R2:      101 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'H' << 'e'
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:       10 | R2:      101 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:       10 | R2:      101 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        9 | R2:      101 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        9 | R2:      101 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:       10 | R2:      101 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'l'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:       10 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        9 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        9 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'He' << 'l'
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        9 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        9 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        8 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        8 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:        9 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'l'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:        9 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        8 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        8 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'Hel' << 'l'
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        8 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        8 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        7 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        7 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:        8 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'o'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:        8 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        7 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        7 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'Hell' << 'o'
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        7 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        7 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        6 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        6 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:        7 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: ' '
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:        7 | R2:       32 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        6 | R2:       32 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        6 | R2:       32 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'Hello' << ' '
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        6 | R2:       32 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        6 | R2:       32 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        5 | R2:       32 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        5 | R2:       32 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:        6 | R2:       32 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'W'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:        6 | R2:       87 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        5 | R2:       87 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        5 | R2:       87 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'Hello ' << 'W'
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        5 | R2:       87 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        5 | R2:       87 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        4 | R2:       87 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        4 | R2:       87 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:        5 | R2:       87 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'o'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:        5 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        4 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        4 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'Hello W' << 'o'        
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        4 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        4 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        3 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        3 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:        4 | R2:      111 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'r'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:        4 | R2:      114 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        3 | R2:      114 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        3 | R2:      114 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'Hello Wo' << 'r'       
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        3 | R2:      114 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        3 | R2:      114 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        2 | R2:      114 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        2 | R2:      114 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:        3 | R2:      114 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'l'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:        3 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        2 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        2 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'Hello Wor' << 'l'      
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        2 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        2 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        1 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        1 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:        2 | R2:      108 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: 'd'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:        2 | R2:      100 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        1 | R2:      100 | R3:        0 | N: 0 | Z: 0 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        1 | R2:      100 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'Hello Worl' << 'd'     
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        1 | R2:      100 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        1 | R2:      100 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        0 | R2:      100 | R3:        0 | N: 0 | Z: 1 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:        0 | R2:      100 | R3:        0 | N: 0 | Z: 0 | PC:   10     
 DEBUG    machine.py     INSTR: inc r1       | R0:       12 | R1:        1 | R2:      100 | R3:        0 | N: 0 | Z: 0 | PC:   11     
 DEBUG    machine.py    input: '!'
 DEBUG    machine.py     INSTR: mov r2, (4)  | R0:       12 | R1:        1 | R2:       33 | R3:        0 | N: 0 | Z: 0 | PC:   12     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:        0 | R2:       33 | R3:        0 | N: 0 | Z: 1 | PC:   13     
 DEBUG    machine.py     INSTR: jg 15        | R0:       12 | R1:        0 | R2:       33 | R3:        0 | N: 0 | Z: 0 | PC:   15     
 DEBUG    machine.py    output_str_buffer: 'Hello World' << '!'    
 DEBUG    machine.py     INSTR: mov (5), r2  | R0:       12 | R1:        0 | R2:       33 | R3:        0 | N: 0 | Z: 0 | PC:   16     
 DEBUG    machine.py     INSTR: jmp 8        | R0:       12 | R1:        0 | R2:       33 | R3:        0 | N: 0 | Z: 0 | PC:    8     
 DEBUG    machine.py     INSTR: dec r1       | R0:       12 | R1:       -1 | R2:       33 | R3:        0 | N: 1 | Z: 0 | PC:    9     
 DEBUG    machine.py     INSTR: jng 17       | R0:       12 | R1:       -1 | R2:       33 | R3:        0 | N: 0 | Z: 0 | PC:   17     
 INFO    machine.py    output_str_buffer: 'Hello World!'
 INFO    machine.py    output_int_buffer: []
Hello World!
[]
instr_counter:  101

```

**Пример проверки исходного кода:**

```bash

C:\Users\user\CSA-lab3> poetry run pytest . -v
====================== test session starts =======================
platform win32 -- Python 3.12.3, pytest-7.4.4, pluggy-1.5.0 -- C:\U
sers\user\AppData\Local\pypoetry\Cache\virtualenvs\csa-lab3-LX7E7N-U-py3.12\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\user\CSA-lab3
configfile: pytest.ini
plugins: golden-0.2.2
collected 5 items                                                 

integration_test.py::test_translator_and_machine[golden/cat.yml] PASSED [ 20%]
integration_test.py::test_translator_and_machine[golden/hello.yml] PASSED [ 40%]
integration_test.py::test_translator_and_machine[golden/hello_user_name.yml] PASSED [ 60%]
integration_test.py::test_translator_and_machine[golden/prob1.yml] PASSED [ 80%]
integration_test.py::test_translator_and_machine[golden/test.yml] PASSED [100%]

======================= 5 passed in 0.49s ========================

```

```bash

| ФИО                        | алг             | LoC | code байт | code инстр. | инстр. | такт. | вариант                                                                   |
| Анисимов Максим Дмитриевич | hello           | 43  | -         | 43          | 114    | -     | asm | risc | neum | hw | instr | struct | stream | mem | pstr | prob1     |
| Анисимов Максим Дмитриевич | cat             | 24  | -         | 15          | 101    | -     | asm | risc | neum | hw | instr | struct | stream | mem | pstr | prob1     |
| Анисимов Максим Дмитриевич | hello_user_name | 120 | -         | 106         | 339    | -     | asm | risc | neum | hw | instr | struct | stream | mem | pstr | prob1     |
| Анисимов Максим Дмитриевич | prob1           | 56  | -         | 37          | 500    | -     | asm | risc | neum | hw | instr | struct | stream | mem | pstr | prob1     |
| Анисимов Максим Дмитриевич | test            | 46  | -         | 46          | 130    | -     | asm | risc | neum | hw | instr | struct | stream | mem | pstr | prob1     |

```
