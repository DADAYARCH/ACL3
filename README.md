## Отчет

* Черных Роман Александрович, P33151
* `lisp | acc | neum | hw | instr | struct | stream | mem | cstr | prob2 | 8bit`
* Без усложнения


### Язык программирования

Форма Бэкуса-Наура:

```text
<program> ::= <statement> | <statement> <program>
<statement> ::= <function_definition> | <common_statement>

<function_definition> ::= "(" <function_name> "(" <function_arguments> ")" <function_body> ")"
<function_name> ::= <identifier>
<function_arguments> ::= "" | <function_argument> | <function_argument> <function_arguments>
<function_argument> ::= <identifier>
<function_body> ::= <argument>

<common_statement> ::= "(" <statement_name> <arguments> ")"
<statement_name> ::= <boolean_operation> | <math_operation> | <identifier>
<boolean_operation> ::= "=" | ">="
<math_operation> ::= "+" | "-" | "*" | "/"
<arguments> ::= "" | <argument> | <argument> <arguments>
<argument> ::= <literal> | <variable> | <common_statement> 

<literal> ::= <number> | <string>
<number> ::= [ "-" ] <unsigned_number>
<unsigned_number> ::= <digit> | <digit> <unsigned_number>
<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
<string> ::= '"' <string_letters> '"'
<string_letters> ::= "" | <string_letter> | <string_letter> <string_letters>
<string_letter> ::= <any symbol except: '"'>

<variable> ::= <identifier>
<identifier> ::= <identifier_letters>
<identifier_letters> ::= <identifier_letter> | <identifier_letter> <identifier_letters>
<identifier_letters> ::= "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" 
  | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" 
  | "V" | "W" | "X" | "Y" | "Z" | "a" | "b" | "c" | "d" | "e" | "f" | "g" 
  | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" 
  | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "_"
```

Код состоит из последовательности выражений, заключенных в скобки. Выражение состоит из названия и аргументов, следующих 
друг за другом через пробел. В качестве аргументов могут выступать также выражения, переменные или числовые (`123`) или 
строковые литералы (`"str"`). Пробельные символы и переносы строк игнорируются.

Любое выражение/переменная/литерал имеют возвращаемое значение (кроме объявления функции).

Объявление функции выглядит, как обычное выражение, включающее название-аргументы-тело. Тело функция - ровно одно 
выражение.

Типов данных два: 64-битное знаковое число, строка. Соответственно, каждое выражение возвращает значение одного из двух 
типов.

На уровне языка поддерживаются математические выражения `+` - сложение, `-` - вычитание, `*` - умножение, 
`/` - целочисленное деление, `mod` - остаток от деления.

Поддерживаются операторы сравнения `=` - равно, `>` - больше, `>=` - больше или равно. Возвращаемое значение 1 - истина, 
0 - ложь.

Переменные можно определить при помощи функции `set` (`(set <label> <val>)`). Возвращает установленное значение. 
Область видимости данных - глобальная.

Также поддерживается условная конструкция `if` (`(if <cond> <opt1> <opt2>)`). Истина определяется по значению `cond`, 
равно 0 - будет выполнен код `opt2`, иначе `opt1`.

Определены функции для работы с вводом выводом: `printi`, `printc`, `print`, `printline`, `readline`, `readchar`. 
Функции вывода возвращают количество выведенных символов, а функция чтения - прочитанную строку или числовой код
символа.

Поддерживается функция цикла `loop`, которая позволяет *бесконечно* зациклить выполнение определенного выражения без
возможности завершения.

Код выполняется последовательно сверху вниз. Внутри выражений код выполняется *справа налево*.


### Организация памяти

Память общая для данных и для инструкций.

Имеет примерно следующий вид:

```text
    +------------------------+
    |         Memory         |
    +------------------------+
    | 0:   jmp s             |
    | 1:   <func1 code>      |
    | ...                    |
    | f:   <func2 code>      |
    | ...                    |
    | s:   <main code>       |
    | ...                    |
    | m:   halt              |
    | m+1: <const1>          |
    | m+2: <const2>          |
    | ...                    |
    | v+0: <variable1>       |
    | v+1: <variable2>       |
    | ...                    |
    | b+0: <anon_buffer1>    |
    | b+1: <anon_buffer2>    |
    | ...                    |
    | ...                    |
    | n:   stack start       |
    +------------------------+
```

Машинное слово - 32 бита.

Первая инструкция - переход к основной программе (которая была странслирована из исходного кода, написанного программистом).
Далее хранятся друг за другом используемые программой функции. После всех функции расположены инструкции основной программы.
Последняя инструкция - `halt`.

Далее находятся данные.

Сначала располагаются константы (числовые - 1 слово, строковые - количество символов + 1 слов). Далее находятся
переменные (по 1 машинному слову). Далее выделены анонимные буферы для некоторых команд, которые представляют
несколько размеченных друг за другом слов (например, `read` выделяет буфер для чтения данных из ввода). Буферы всегда 
инициализируются 0. В конце памяти данных находится место для стека, он "растет" от конца памяти к началу.

Программист с регистрами и памятью напрямую не работает.

Строковые литералы всегда считаются константами и записываются в область констант. Числовые литералы считаются
константой, если не влазят в 20 бит (то есть больше 2^19-1 или меньше -2^19). Остальные числа будут загружены в 
регистры при помощи непосредственной адресации.

Порядок расположения констант, переменных, буферов определяется порядком встречи в коде.

Во время трансляции исходной программы если заявляется необходимость выделения константы/переменной/буфера, то в
машинном коде временно записывается символ (идентификатор) выделенной памяти. На конечном этапе трансляции происходит 
маппинг всех запрошенных констант/переменных/буферов на память, а все идентификаторы в машинном коде заменяются на
непосредственный адрес.

В стек ничего не отображается.

Поскольку архитектура процессора - аккумуляторная, то все переменные отображаются в память, а при необходимости
обращения в аккумулятор загружается их значение. При вызове функций первый аргумент (если есть) передается через 
аккумулятор, а последующие (если есть) передаются через стек.


### Система команд

Типов данных два: 32-битное знаковое число, строка. Внутри процессора число представляет собой свое значение, а строка -
указатель по абсолютному адресу на первый символ.

Регистры:

| Название | Разрядность | Описание                                                                    |
|----------|-------------|-----------------------------------------------------------------------------|
| `ac`     | 32          | аккумулятор                                                                 |
| `ip`     | 32          | указатель на адрес исполняемой инструкции                                   |
| `in`     | 32          | содержит текущую исполняемую инструкцию                                     |
| `ar`     | 32          | регистр адреса, используется для чтения/записи                              |
| `dr`     | 32          | регистр данных, используется для чтения/записи                              |
| `sp`     | 32          | указатель на вершину стека                                                  |
| `fl`     | 4           | регистр флагов, содержит флаги по результатам операции (NZVC)               |

Доступ к памяти данных осуществляется при помощи регистров `ar`, `dr`. Для чтения необходимо задать адрес ячейки для 
чтения. Для записи необходимо задать адрес и значение для записи.

Ввод/вывод отображается на память. Для вывода необходимо выполнить запись в ячейку памяти по определенному адресу. 
Для ввода необходимо выполнить чтение определенной (другой) ячейки памяти.

Имеется 5 типов адресации:
  * непосредственная
  * абсолютная
  * относительная (`ip`)
  * относительная (`sp`)
  * относительная косвенная (`sp`)

Инструкции делятся на 3 типа: без аргумента, адресные, по значению.
Инструкции без аргумента не требуют адресации. Адресные используют аргумент адреса с которым будет выполнено действие.
Инструкции по значению используют адресацию, для указания на адрес значения, с которым будет выполнено действие.

Набор инструкций:

| Инструкция    | Описание                                                            |
|---------------|---------------------------------------------------------------------|
| `noop`        | ничего не выполняется                                               |
| `halt`        | останов                                                             |
| `ld <val>`    | загрузка значения из памяти в аккумулятор                           |
| `st <addr>`   | запись значения аккумулятора в память                               |
| `call <addr>` | вызвать функцию по адресу (адрес возврата положить на стек)         |
| `ret`         | возвращение из функции (адрес возврата снять со стека)              |
| `push`        | положить значение аккумулятора на стек                              |
| `pop`         | снять значение со стека и записать в аккумулятор                    |
| `popn`        | снять значение со стека без записи                                  |
| `cmp <val>`   | установить флаги по результату операции вычитания из аккумулятора   |
| `jme <addr>`  | переход по адресу если равно (Z == 1)                               |
| `jmg <addr>`  | переход по адресу если значение больше (N == V and Z == 0)          |
| `jmge <addr>` | переход по адресу если значение больше или равно (N == V or Z == 1) |
| `jmp <addr>`  | безусловный переход по адресу                                       |
| `inc <addr>`  | инкремент значения по адресу                                        |
| `dec <addr>`  | декремент значения по адресу                                        |
| `mod <val>`   | деление по модулю аккумулятора и значения                           |
| `add <val>`   | сложить значение с аккумулятором                                    |
| `sub <val>`   | вычесть из аккумулятора значение                                    |
| `mul <val>`   | умножить аккумулятор на значение                                    |
| `div <val>`   | поделить аккумулятор на значение (целочисленное деление)            |
| `inv`         | инвертировать значение аккумулятора                                 |

где:
  * `<val>` - аргумент будет интерпретирован как значение (значение по адресу), с которым необходимо выполнить операцию
  * `<addr>` - аргумент будет интерпретирован как адрес, с которым необходимо выполнить операцию

Поток управления:
  * вызов `call` или возврат `ret` из функции
  * условные `bre`, `brg`, `brge` и безусловные `br` переходы
  * инкремент `ip` после любой другой инструкции

Машинный код сериализуется в список JSON объектов.

Пример:

```json
[
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "cmp",
      "arg": {
        "tag": "#",
        "val": 128
      }
    }
  },
  {
    "tag": "BINARY",
    "val": "l"
  }
]
```

где:
* `tag` - метка машинного слова, определяющая тип того, что находится в ячейке памяти (`INSTRUCTION` - инструкция, 
  `BINARY` - число)
* `instr` - структура описания инструкции (при `tag` равном `INSTRUCTION`):
  * `op` - код операции
  * `arg` - структура описания аргумента (только для инструкций с аргументом):
    * `tag` - тип адресации (см. типы адресации)
    * `val` - значение смещения при заданной адресации
* `val` - число (или код символа), хранящееся в ячейке (при `tag` равном `BINARY`)

Типы данных в модуле [isa](isa.py):
  * `Opcode` - перечисление кодов операций
  * `AddressType` - перечисление типов адресации
  * `Address` - структура объединение типа адресации и значения
  * `Term` - структура для описания одной инструкции
  * `WordTag` - перечисление типов машинного слова
  * `Word` - структура описания одного слова при сериализации машинного кода

Стандартная библиотека реализована в модуле [stdlib](stdlib.py).


### Транслятор

Интерфейс командной строки: 

```text
usage: translator.py [-h] [--output output_file] source_file

Translates source code into en executable file.

positional arguments:
  source_file           file with source code

options:
  -h, --help            show this help message and exit
  --output output_file, -o output_file
                        file for storing an executable (default: output)
```

Реализовано в модуле: [translator](translator.py)

Этапы трансляции:
  * чтение исходного кода
  * трансформация текста в последовательность токенов с тегами
  * преобразование токенов в абстрактное дерево (выражение - вершина, литерал/идентификатор - лист)
  * вычленение Statement на основе дерева и валидация и проверка корректности использования функций
  * генерация машинного кода
  * сериализация полученного кода в файл

Правила генерации машинного кода:
  * каждый Statement должен к концу исполнения должен установить в аккумулятор возвращаемое значение, а также
    вернуть spr в то состояние, в котором он был в начале исполнения
  * при вызове функции вызывающая сторона обязана установить все требуемые аргументы, а также после возврата
    снять со стека все положенные аргументы
  * Statement содержащий переменную или литерал должен загрузить в аккумулятор нужное значение
  * Statement с несколькими аргументами для вычисления производят генерацию кода вычисления с последнего к первому
    (справа налево)
  * при необходимости выделения места в памяти под константу/литерал/буфер, происходит обращение в специальный
    класс, который запоминает все обращения и выдает идентификаторы для последующей генерации памяти данных
    и замены символов на непосредственные адреса
  * при трансляции кода для функции каждый Statement должен учитывать то, где сейчас находятся (в аккумуляторе, в стеке)
    аргументы и помещать их на стек в случае необходимости, а также отслеживать их актуальное положение 
    (смещение относительно spr)
  * после завершения генерации кода, все символы в инструкциях заменяются на адреса в зависимости от их отображения
    в память


### Модель процессора

Интерфейс командной строки:

```text
usage: machine.py [-h] [--input input_file] executable_file

Execute lisp executable file.

positional arguments:
  executable_file       executable file

options:
  -h, --help            show this help message and exit
  --input input_file, -i input_file
                        file with input data for executable (default: empty file)
```

Реализовано в модуле: [machine](machine.py)

#### Data path

```text
                       latch --->+--------+                               +--------+<--- latch   
                                 |   ac   |---------+           +---------|   ar   |             
                    +----------->+--------+         |           |         +--------+<-----------+
                    |                               |           |                               |
                    |  latch --->+--------+         |           |         +--------+<--- latch  |
                    |            |   ip   |-------+ |           | +-------|   dr   |            |
                    +----------->+--------+       | |           | |       +--------+<-----------+
                    |                             | |           | |                             |
                    |            +--------+       | | 0       0 | |       +--------+<--- latch  |
                    |            |   ir   |-----+ | | |       | | | +-----|   sp   |            |
                    |            +--------+     | | | |       | | | |     +--------+<-----------+
                    |                           v v v v       v v v v                           |
                    |                         +---------+   +---------+                         |
                    |                 sel --->|   MUX   |   |   MUX   |<--- sel                 |
                    |                         +---------+   +---------+                         |
                    |                              |             |                              |
                    |                              v             v                              |
          latch     |            inv_left --->+---------+   +---------+<--- inv_right           |
            |       |         extend_bits --->|          \_/          |<--- (+1)                |
            v       |                         |                       |                         |  
       +--------+   |              opcode --->|          ALU          |                         |
       |   fl   |<-----------------------------\                     /                          |
       +--------+   |                           +-------------------+                           |
                    |                                     |                                     |
                    +-------------------------------------+-------------------------------------+
```

#### Взаимодействие с памятью

```text
                                     read   write
                                       |      |
                                       v      v
                                   +------------+----------------------------------------------------------+
                           +------>| Comparator |                                                          |
    +--------+      sel    |       +------------+------------------------------+                           |
    |   ir   |----+  |     |           |      |                                |                           |
    +--------+    |  |     |   +--------------------------------------------------------------------+      |
                  v  v     |   |       v      v                                |                    |      |
    +--------+   +-----+   |   |   +------------+                              v read               v      v write
    |   ar   |-->| MUX |---+------>|            |                        +--------------+        +--------------+
    +--------+   +-----+       |   |            |            input ----->|    INPUT     |        |    OUTPUT    |-----> output
                               |   |   MEMORY   |                        |    BUFFER    |        |    BUFFER    |
                               |   |            |                        +--------------+        +--------------+
               +--------+      |   |            |                               |
    latch ---->|   dr   |------+-->|            |-------+  +--------------------+
               +--------+          +------------+       |  |
                    ^                                   |  |
                    |                                   |  |  +-------- <alu_out>
                    |                                   |  |  |
                    |                                   v  v  v
                    |                                +---------+
                    +--------------------------------|   MUX   |<--- sel
                                                     +---------+
```

Реализован в классе `DataPath`.

Сигналы:
  * `read_memory` - чтение данных по адресу `ar` в `dr`:
    * из памяти данных (`dr <- mem[ar]`)
    * из порта ввода `input`:
      * извлечь из входного буфера токен и подать его на выход
      * если буфер пуст - исключение
  * `write_memory` - запись данных `dr` по адресу `ar`:
    * в память данных (`mem[ar] <- dr`)
    * в порт вывода `output`:
      * записать значение `dr` в буфер вывода
  * `latch_ac`, `latch_ip`, `latch_ar`, `latch_sp` - записать значение с выхода ALU в регистр
  * `sel_dr` - выбрать значение из памяти, выхода ALU или буфера ввода для записи в `dr`
  * `latch_dr` - записать выставленное значение в `dr`
  * `sel_addr` - выбрать адресный регистр для операции с памятью (`ar` или `ip`)
  * `latch_fl` - записать значения флагов операции суммы из ALU в `fl`
  * `sel_left`, `sel_right` - выбрать значения для левого и правого входов ALU
  * `alu_opcode` - выбор операции для осуществления на ALU (sum, mul, div, mod)
  * `alu_inv_left`, `alu_inv_right` - инвертировать левый вход, правый вход ALU соответственно
  * `alu_extend_bits` - расширить знак левого входа ALU (достать число из `ir`)
  * `alu_plus_1` - прибавить 1 к операции суммы ALU


#### ControlUnit

```text
                                                                          +---------+
                                                                      +-->|  step   |--+                 input   output
                                                          latch       |   | counter |  |                   |       ^
         latch                   +--------------+          |          |   +---------+  v                   v       |
           |            read --->|              |          v          |     +---------------+  signals   +-----------+
           v                     |    MEMORY    |       +--------+    +-----|  instruction  |----------->| DataPath* |
        +--------+    +-----+    |              |------>|   ir   |--------->|    decoder    |            +-----------+
   +--->|   ip   |--->| MUX |--->|              |       +--------+          +---------------+               |    |
   |    +--------+    +-----+    +--------------+                                         ^                 |    |
   |                   ^   ^                                                              |                 |    |
   |    +--------+     |   |                                                              +-----------------+    |
   |    |   ar   |-----+  sel                                                               feedback_signals     |
   |    +--------+                                                                                               |
   +-------------------------------------------------------------------------------------------------------------+
```

Реализован в классе `ControlUnit`.

Особенности:
  * hardwired (реализован полностью на Python, для каждого типа инструкции можно однозначно 
    определить сигналы и их порядок для каждого такта исполнения инструкции)
  * step counter - необходим для много-тактовых инструкций

Сигналы:
  * `read_memory` - чтение данных по адресу `ip` в `ir` (`ir <- mem[ip]`)
  * `latch_ir` - записать значение из памяти инструкций в `ir`
  * signals - управляющие сигналы в DataPath
  * feedback_signals - сигналы обратной связи (`fl`)

Шаг декодирования и исполнения одной инструкции выполняется в функции `execute_next_instruction`.
Во время шага в журнал моделирования записывается исполняемая инструкция и состояние модели на конец исполнения.

Цикл симуляции осуществляется в функции simulation.

Остановка моделирования осуществляется при превышении лимита количества выполняемых инструкций, 
при отсутствии данных для чтения из порта ввода, при выполнении инструкции halt.


### Тестирование

Для тестирования выбраны 4 алгоритма:
1. [hello](./golden/hello.yml) ([source](./examples/hello))
2. [cat](./golden/cat.yml) ([source](./examples/cat))
3. [hello_user_name](./golden/hello_user_name.yml) ([source](./examples/hello_user_name))
4. [prob2](./golden/prob2.yml) ([source](./examples/prob2))

Golden-тесты реализованы в [integration_test.py](integration_test.py), конфигурация к ним 
находится в директории [golden](./golden).

CI реализован через GitHub Actions:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

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

  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

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

* `poetry` - управления зависимостями для языка программирования Python.
* `coverage` - формирование отчёта об уровне покрытия исходного кода.
* `pytest` - утилита для запуска тестов.
* `ruff` - утилита для форматирования и проверки стиля кодирования.

Пример использования и журнал работы процессора на примере `hello`:

```bash
% cat ./examples/hello
(print "Hello, world!")

% cat ./examples/input/hello

% python translator.py ./examples/hello
LoC: 1 code instr: 20

% cat ./output
[
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "jmp",
      "arg": {
        "tag": "*",
        "val": 17
      },
      "desc": "'start' function"
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "push"
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "ld",
      "arg": {
        "tag": "#",
        "val": 0
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "push"
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "ld",
      "arg": {
        "tag": "**sp",
        "val": 1
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "cmp",
      "arg": {
        "tag": "#",
        "val": 0
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "jme",
      "arg": {
        "tag": "*ip",
        "val": 8
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "st",
      "arg": {
        "tag": "*",
        "val": 5556
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "inc",
      "arg": {
        "tag": "*sp",
        "val": 1
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "inc",
      "arg": {
        "tag": "*sp",
        "val": 0
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "ld",
      "arg": {
        "tag": "*sp",
        "val": 0
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "cmp",
      "arg": {
        "tag": "#",
        "val": 128
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "jme",
      "arg": {
        "tag": "*ip",
        "val": 2
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "jmp",
      "arg": {
        "tag": "*ip",
        "val": -9
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "pop"
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "popn"
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "ret"
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "ld",
      "arg": {
        "tag": "#",
        "val": 20
      },
      "desc": "'Hello, world!' const"
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "call",
      "arg": {
        "tag": "*",
        "val": 1
      },
      "desc": "'print' function"
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "halt"
    }
  },
  {
    "tag": "BINARY",
    "val": "H"
  },
  {
    "tag": "BINARY",
    "val": "e"
  },
  {
    "tag": "BINARY",
    "val": "l"
  },
  {
    "tag": "BINARY",
    "val": "l"
  },
  {
    "tag": "BINARY",
    "val": "o"
  },
  {
    "tag": "BINARY",
    "val": ","
  },
  {
    "tag": "BINARY",
    "val": " "
  },
  {
    "tag": "BINARY",
    "val": "w"
  },
  {
    "tag": "BINARY",
    "val": "o"
  },
  {
    "tag": "BINARY",
    "val": "r"
  },
  {
    "tag": "BINARY",
    "val": "l"
  },
  {
    "tag": "BINARY",
    "val": "d"
  },
  {
    "tag": "BINARY",
    "val": "!"
  },
  {
    "tag": "BINARY",
    "val": "\u0000"
  }
]

% python machine.py output
DEBUG:root:tick=0    ac=0x0 ip=0x0 ar=0x0 dr=0x0 sp=0x1fff fl=0x0 stack_top=?
DEBUG:root:JUMP
DEBUG:root:tick=1    ac=0x0 ip=0x11 ar=0x0 dr=0x0 sp=0x1fff fl=0x0 stack_top=?
DEBUG:root:LOAD
DEBUG:root:tick=3    ac=0x14 ip=0x12 ar=0x0 dr=0x14 sp=0x1fff fl=0x0 stack_top=?
DEBUG:root:CALL
DEBUG:root:tick=7    ac=0x14 ip=0x1 ar=0x1ffe dr=0x13 sp=0x1ffe fl=0x0 stack_top=0x13
DEBUG:root:PUSH
DEBUG:root:tick=10   ac=0x14 ip=0x2 ar=0x1ffd dr=0x14 sp=0x1ffd fl=0x0 stack_top=0x14
DEBUG:root:LOAD
DEBUG:root:tick=12   ac=0x0 ip=0x3 ar=0x1ffd dr=0x0 sp=0x1ffd fl=0x0 stack_top=0x14
DEBUG:root:PUSH
DEBUG:root:tick=15   ac=0x0 ip=0x4 ar=0x1ffc dr=0x0 sp=0x1ffc fl=0x0 stack_top=0x0
DEBUG:root:LOAD
DEBUG:root:tick=20   ac=0x48 ip=0x5 ar=0x14 dr=0x48 sp=0x1ffc fl=0x0 stack_top=0x0
DEBUG:root:COMPARE
DEBUG:root:tick=22   ac=0x48 ip=0x6 ar=0x14 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x0
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=23   ac=0x48 ip=0x7 ar=0x14 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x0
DEBUG:root:STORE
DEBUG:root:output: '' <- 'H'
DEBUG:root:tick=26   ac=0x48 ip=0x8 ar=0x15b4 dr=0x48 sp=0x1ffc fl=0x1 stack_top=0x0
DEBUG:root:INCREMENT
DEBUG:root:tick=30   ac=0x48 ip=0x9 ar=0x1ffd dr=0x15 sp=0x1ffc fl=0x1 stack_top=0x0
DEBUG:root:INCREMENT
DEBUG:root:tick=34   ac=0x48 ip=0xa ar=0x1ffc dr=0x1 sp=0x1ffc fl=0x1 stack_top=0x1
DEBUG:root:LOAD
DEBUG:root:tick=37   ac=0x1 ip=0xb ar=0x1ffc dr=0x1 sp=0x1ffc fl=0x1 stack_top=0x1
DEBUG:root:COMPARE
DEBUG:root:tick=39   ac=0x1 ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x1
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=40   ac=0x1 ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x1
DEBUG:root:JUMP
DEBUG:root:tick=42   ac=0x1 ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x1
DEBUG:root:LOAD
DEBUG:root:tick=47   ac=0x65 ip=0x5 ar=0x15 dr=0x65 sp=0x1ffc fl=0x8 stack_top=0x1
DEBUG:root:COMPARE
DEBUG:root:tick=49   ac=0x65 ip=0x6 ar=0x15 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x1
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=50   ac=0x65 ip=0x7 ar=0x15 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x1
DEBUG:root:STORE
DEBUG:root:output: 'H' <- 'e'
DEBUG:root:tick=53   ac=0x65 ip=0x8 ar=0x15b4 dr=0x65 sp=0x1ffc fl=0x1 stack_top=0x1
DEBUG:root:INCREMENT
DEBUG:root:tick=57   ac=0x65 ip=0x9 ar=0x1ffd dr=0x16 sp=0x1ffc fl=0x1 stack_top=0x1
DEBUG:root:INCREMENT
DEBUG:root:tick=61   ac=0x65 ip=0xa ar=0x1ffc dr=0x2 sp=0x1ffc fl=0x1 stack_top=0x2
DEBUG:root:LOAD
DEBUG:root:tick=64   ac=0x2 ip=0xb ar=0x1ffc dr=0x2 sp=0x1ffc fl=0x1 stack_top=0x2
DEBUG:root:COMPARE
DEBUG:root:tick=66   ac=0x2 ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x2
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=67   ac=0x2 ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x2
DEBUG:root:JUMP
DEBUG:root:tick=69   ac=0x2 ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x2
DEBUG:root:LOAD
DEBUG:root:tick=74   ac=0x6c ip=0x5 ar=0x16 dr=0x6c sp=0x1ffc fl=0x8 stack_top=0x2
DEBUG:root:COMPARE
DEBUG:root:tick=76   ac=0x6c ip=0x6 ar=0x16 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x2
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=77   ac=0x6c ip=0x7 ar=0x16 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x2
DEBUG:root:STORE
DEBUG:root:output: 'He' <- 'l'
DEBUG:root:tick=80   ac=0x6c ip=0x8 ar=0x15b4 dr=0x6c sp=0x1ffc fl=0x1 stack_top=0x2
DEBUG:root:INCREMENT
DEBUG:root:tick=84   ac=0x6c ip=0x9 ar=0x1ffd dr=0x17 sp=0x1ffc fl=0x1 stack_top=0x2
DEBUG:root:INCREMENT
DEBUG:root:tick=88   ac=0x6c ip=0xa ar=0x1ffc dr=0x3 sp=0x1ffc fl=0x1 stack_top=0x3
DEBUG:root:LOAD
DEBUG:root:tick=91   ac=0x3 ip=0xb ar=0x1ffc dr=0x3 sp=0x1ffc fl=0x1 stack_top=0x3
DEBUG:root:COMPARE
DEBUG:root:tick=93   ac=0x3 ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x3
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=94   ac=0x3 ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x3
DEBUG:root:JUMP
DEBUG:root:tick=96   ac=0x3 ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x3
DEBUG:root:LOAD
DEBUG:root:tick=101  ac=0x6c ip=0x5 ar=0x17 dr=0x6c sp=0x1ffc fl=0x8 stack_top=0x3
DEBUG:root:COMPARE
DEBUG:root:tick=103  ac=0x6c ip=0x6 ar=0x17 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x3
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=104  ac=0x6c ip=0x7 ar=0x17 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x3
DEBUG:root:STORE
DEBUG:root:output: 'Hel' <- 'l'
DEBUG:root:tick=107  ac=0x6c ip=0x8 ar=0x15b4 dr=0x6c sp=0x1ffc fl=0x1 stack_top=0x3
DEBUG:root:INCREMENT
DEBUG:root:tick=111  ac=0x6c ip=0x9 ar=0x1ffd dr=0x18 sp=0x1ffc fl=0x1 stack_top=0x3
DEBUG:root:INCREMENT
DEBUG:root:tick=115  ac=0x6c ip=0xa ar=0x1ffc dr=0x4 sp=0x1ffc fl=0x1 stack_top=0x4
DEBUG:root:LOAD
DEBUG:root:tick=118  ac=0x4 ip=0xb ar=0x1ffc dr=0x4 sp=0x1ffc fl=0x1 stack_top=0x4
DEBUG:root:COMPARE
DEBUG:root:tick=120  ac=0x4 ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x4
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=121  ac=0x4 ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x4
DEBUG:root:JUMP
DEBUG:root:tick=123  ac=0x4 ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x4
DEBUG:root:LOAD
DEBUG:root:tick=128  ac=0x6f ip=0x5 ar=0x18 dr=0x6f sp=0x1ffc fl=0x8 stack_top=0x4
DEBUG:root:COMPARE
DEBUG:root:tick=130  ac=0x6f ip=0x6 ar=0x18 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x4
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=131  ac=0x6f ip=0x7 ar=0x18 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x4
DEBUG:root:STORE
DEBUG:root:output: 'Hell' <- 'o'
DEBUG:root:tick=134  ac=0x6f ip=0x8 ar=0x15b4 dr=0x6f sp=0x1ffc fl=0x1 stack_top=0x4
DEBUG:root:INCREMENT
DEBUG:root:tick=138  ac=0x6f ip=0x9 ar=0x1ffd dr=0x19 sp=0x1ffc fl=0x1 stack_top=0x4
DEBUG:root:INCREMENT
DEBUG:root:tick=142  ac=0x6f ip=0xa ar=0x1ffc dr=0x5 sp=0x1ffc fl=0x1 stack_top=0x5
DEBUG:root:LOAD
DEBUG:root:tick=145  ac=0x5 ip=0xb ar=0x1ffc dr=0x5 sp=0x1ffc fl=0x1 stack_top=0x5
DEBUG:root:COMPARE
DEBUG:root:tick=147  ac=0x5 ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x5
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=148  ac=0x5 ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x5
DEBUG:root:JUMP
DEBUG:root:tick=150  ac=0x5 ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x5
DEBUG:root:LOAD
DEBUG:root:tick=155  ac=0x2c ip=0x5 ar=0x19 dr=0x2c sp=0x1ffc fl=0x8 stack_top=0x5
DEBUG:root:COMPARE
DEBUG:root:tick=157  ac=0x2c ip=0x6 ar=0x19 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x5
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=158  ac=0x2c ip=0x7 ar=0x19 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x5
DEBUG:root:STORE
DEBUG:root:output: 'Hello' <- ','
DEBUG:root:tick=161  ac=0x2c ip=0x8 ar=0x15b4 dr=0x2c sp=0x1ffc fl=0x1 stack_top=0x5
DEBUG:root:INCREMENT
DEBUG:root:tick=165  ac=0x2c ip=0x9 ar=0x1ffd dr=0x1a sp=0x1ffc fl=0x1 stack_top=0x5
DEBUG:root:INCREMENT
DEBUG:root:tick=169  ac=0x2c ip=0xa ar=0x1ffc dr=0x6 sp=0x1ffc fl=0x1 stack_top=0x6
DEBUG:root:LOAD
DEBUG:root:tick=172  ac=0x6 ip=0xb ar=0x1ffc dr=0x6 sp=0x1ffc fl=0x1 stack_top=0x6
DEBUG:root:COMPARE
DEBUG:root:tick=174  ac=0x6 ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x6
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=175  ac=0x6 ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x6
DEBUG:root:JUMP
DEBUG:root:tick=177  ac=0x6 ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x6
DEBUG:root:LOAD
DEBUG:root:tick=182  ac=0x20 ip=0x5 ar=0x1a dr=0x20 sp=0x1ffc fl=0x8 stack_top=0x6
DEBUG:root:COMPARE
DEBUG:root:tick=184  ac=0x20 ip=0x6 ar=0x1a dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x6
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=185  ac=0x20 ip=0x7 ar=0x1a dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x6
DEBUG:root:STORE
DEBUG:root:output: 'Hello,' <- ' '
DEBUG:root:tick=188  ac=0x20 ip=0x8 ar=0x15b4 dr=0x20 sp=0x1ffc fl=0x1 stack_top=0x6
DEBUG:root:INCREMENT
DEBUG:root:tick=192  ac=0x20 ip=0x9 ar=0x1ffd dr=0x1b sp=0x1ffc fl=0x1 stack_top=0x6
DEBUG:root:INCREMENT
DEBUG:root:tick=196  ac=0x20 ip=0xa ar=0x1ffc dr=0x7 sp=0x1ffc fl=0x1 stack_top=0x7
DEBUG:root:LOAD
DEBUG:root:tick=199  ac=0x7 ip=0xb ar=0x1ffc dr=0x7 sp=0x1ffc fl=0x1 stack_top=0x7
DEBUG:root:COMPARE
DEBUG:root:tick=201  ac=0x7 ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x7
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=202  ac=0x7 ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x7
DEBUG:root:JUMP
DEBUG:root:tick=204  ac=0x7 ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x7
DEBUG:root:LOAD
DEBUG:root:tick=209  ac=0x77 ip=0x5 ar=0x1b dr=0x77 sp=0x1ffc fl=0x8 stack_top=0x7
DEBUG:root:COMPARE
DEBUG:root:tick=211  ac=0x77 ip=0x6 ar=0x1b dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x7
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=212  ac=0x77 ip=0x7 ar=0x1b dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x7
DEBUG:root:STORE
DEBUG:root:output: 'Hello, ' <- 'w'
DEBUG:root:tick=215  ac=0x77 ip=0x8 ar=0x15b4 dr=0x77 sp=0x1ffc fl=0x1 stack_top=0x7
DEBUG:root:INCREMENT
DEBUG:root:tick=219  ac=0x77 ip=0x9 ar=0x1ffd dr=0x1c sp=0x1ffc fl=0x1 stack_top=0x7
DEBUG:root:INCREMENT
DEBUG:root:tick=223  ac=0x77 ip=0xa ar=0x1ffc dr=0x8 sp=0x1ffc fl=0x1 stack_top=0x8
DEBUG:root:LOAD
DEBUG:root:tick=226  ac=0x8 ip=0xb ar=0x1ffc dr=0x8 sp=0x1ffc fl=0x1 stack_top=0x8
DEBUG:root:COMPARE
DEBUG:root:tick=228  ac=0x8 ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x8
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=229  ac=0x8 ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x8
DEBUG:root:JUMP
DEBUG:root:tick=231  ac=0x8 ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x8
DEBUG:root:LOAD
DEBUG:root:tick=236  ac=0x6f ip=0x5 ar=0x1c dr=0x6f sp=0x1ffc fl=0x8 stack_top=0x8
DEBUG:root:COMPARE
DEBUG:root:tick=238  ac=0x6f ip=0x6 ar=0x1c dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x8
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=239  ac=0x6f ip=0x7 ar=0x1c dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x8
DEBUG:root:STORE
DEBUG:root:output: 'Hello, w' <- 'o'
DEBUG:root:tick=242  ac=0x6f ip=0x8 ar=0x15b4 dr=0x6f sp=0x1ffc fl=0x1 stack_top=0x8
DEBUG:root:INCREMENT
DEBUG:root:tick=246  ac=0x6f ip=0x9 ar=0x1ffd dr=0x1d sp=0x1ffc fl=0x1 stack_top=0x8
DEBUG:root:INCREMENT
DEBUG:root:tick=250  ac=0x6f ip=0xa ar=0x1ffc dr=0x9 sp=0x1ffc fl=0x1 stack_top=0x9
DEBUG:root:LOAD
DEBUG:root:tick=253  ac=0x9 ip=0xb ar=0x1ffc dr=0x9 sp=0x1ffc fl=0x1 stack_top=0x9
DEBUG:root:COMPARE
DEBUG:root:tick=255  ac=0x9 ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x9
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=256  ac=0x9 ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x9
DEBUG:root:JUMP
DEBUG:root:tick=258  ac=0x9 ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0x9
DEBUG:root:LOAD
DEBUG:root:tick=263  ac=0x72 ip=0x5 ar=0x1d dr=0x72 sp=0x1ffc fl=0x8 stack_top=0x9
DEBUG:root:COMPARE
DEBUG:root:tick=265  ac=0x72 ip=0x6 ar=0x1d dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x9
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=266  ac=0x72 ip=0x7 ar=0x1d dr=0x0 sp=0x1ffc fl=0x1 stack_top=0x9
DEBUG:root:STORE
DEBUG:root:output: 'Hello, wo' <- 'r'
DEBUG:root:tick=269  ac=0x72 ip=0x8 ar=0x15b4 dr=0x72 sp=0x1ffc fl=0x1 stack_top=0x9
DEBUG:root:INCREMENT
DEBUG:root:tick=273  ac=0x72 ip=0x9 ar=0x1ffd dr=0x1e sp=0x1ffc fl=0x1 stack_top=0x9
DEBUG:root:INCREMENT
DEBUG:root:tick=277  ac=0x72 ip=0xa ar=0x1ffc dr=0xa sp=0x1ffc fl=0x1 stack_top=0xa
DEBUG:root:LOAD
DEBUG:root:tick=280  ac=0xa ip=0xb ar=0x1ffc dr=0xa sp=0x1ffc fl=0x1 stack_top=0xa
DEBUG:root:COMPARE
DEBUG:root:tick=282  ac=0xa ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xa
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=283  ac=0xa ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xa
DEBUG:root:JUMP
DEBUG:root:tick=285  ac=0xa ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xa
DEBUG:root:LOAD
DEBUG:root:tick=290  ac=0x6c ip=0x5 ar=0x1e dr=0x6c sp=0x1ffc fl=0x8 stack_top=0xa
DEBUG:root:COMPARE
DEBUG:root:tick=292  ac=0x6c ip=0x6 ar=0x1e dr=0x0 sp=0x1ffc fl=0x1 stack_top=0xa
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=293  ac=0x6c ip=0x7 ar=0x1e dr=0x0 sp=0x1ffc fl=0x1 stack_top=0xa
DEBUG:root:STORE
DEBUG:root:output: 'Hello, wor' <- 'l'
DEBUG:root:tick=296  ac=0x6c ip=0x8 ar=0x15b4 dr=0x6c sp=0x1ffc fl=0x1 stack_top=0xa
DEBUG:root:INCREMENT
DEBUG:root:tick=300  ac=0x6c ip=0x9 ar=0x1ffd dr=0x1f sp=0x1ffc fl=0x1 stack_top=0xa
DEBUG:root:INCREMENT
DEBUG:root:tick=304  ac=0x6c ip=0xa ar=0x1ffc dr=0xb sp=0x1ffc fl=0x1 stack_top=0xb
DEBUG:root:LOAD
DEBUG:root:tick=307  ac=0xb ip=0xb ar=0x1ffc dr=0xb sp=0x1ffc fl=0x1 stack_top=0xb
DEBUG:root:COMPARE
DEBUG:root:tick=309  ac=0xb ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xb
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=310  ac=0xb ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xb
DEBUG:root:JUMP
DEBUG:root:tick=312  ac=0xb ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xb
DEBUG:root:LOAD
DEBUG:root:tick=317  ac=0x64 ip=0x5 ar=0x1f dr=0x64 sp=0x1ffc fl=0x8 stack_top=0xb
DEBUG:root:COMPARE
DEBUG:root:tick=319  ac=0x64 ip=0x6 ar=0x1f dr=0x0 sp=0x1ffc fl=0x1 stack_top=0xb
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=320  ac=0x64 ip=0x7 ar=0x1f dr=0x0 sp=0x1ffc fl=0x1 stack_top=0xb
DEBUG:root:STORE
DEBUG:root:output: 'Hello, worl' <- 'd'
DEBUG:root:tick=323  ac=0x64 ip=0x8 ar=0x15b4 dr=0x64 sp=0x1ffc fl=0x1 stack_top=0xb
DEBUG:root:INCREMENT
DEBUG:root:tick=327  ac=0x64 ip=0x9 ar=0x1ffd dr=0x20 sp=0x1ffc fl=0x1 stack_top=0xb
DEBUG:root:INCREMENT
DEBUG:root:tick=331  ac=0x64 ip=0xa ar=0x1ffc dr=0xc sp=0x1ffc fl=0x1 stack_top=0xc
DEBUG:root:LOAD
DEBUG:root:tick=334  ac=0xc ip=0xb ar=0x1ffc dr=0xc sp=0x1ffc fl=0x1 stack_top=0xc
DEBUG:root:COMPARE
DEBUG:root:tick=336  ac=0xc ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xc
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=337  ac=0xc ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xc
DEBUG:root:JUMP
DEBUG:root:tick=339  ac=0xc ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xc
DEBUG:root:LOAD
DEBUG:root:tick=344  ac=0x21 ip=0x5 ar=0x20 dr=0x21 sp=0x1ffc fl=0x8 stack_top=0xc
DEBUG:root:COMPARE
DEBUG:root:tick=346  ac=0x21 ip=0x6 ar=0x20 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0xc
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=347  ac=0x21 ip=0x7 ar=0x20 dr=0x0 sp=0x1ffc fl=0x1 stack_top=0xc
DEBUG:root:STORE
DEBUG:root:output: 'Hello, world' <- '!'
DEBUG:root:tick=350  ac=0x21 ip=0x8 ar=0x15b4 dr=0x21 sp=0x1ffc fl=0x1 stack_top=0xc
DEBUG:root:INCREMENT
DEBUG:root:tick=354  ac=0x21 ip=0x9 ar=0x1ffd dr=0x21 sp=0x1ffc fl=0x1 stack_top=0xc
DEBUG:root:INCREMENT
DEBUG:root:tick=358  ac=0x21 ip=0xa ar=0x1ffc dr=0xd sp=0x1ffc fl=0x1 stack_top=0xd
DEBUG:root:LOAD
DEBUG:root:tick=361  ac=0xd ip=0xb ar=0x1ffc dr=0xd sp=0x1ffc fl=0x1 stack_top=0xd
DEBUG:root:COMPARE
DEBUG:root:tick=363  ac=0xd ip=0xc ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xd
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=364  ac=0xd ip=0xd ar=0x1ffc dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xd
DEBUG:root:JUMP
DEBUG:root:tick=366  ac=0xd ip=0x4 ar=0xd dr=0x80 sp=0x1ffc fl=0x8 stack_top=0xd
DEBUG:root:LOAD
DEBUG:root:tick=371  ac=0x0 ip=0x5 ar=0x21 dr=0x0 sp=0x1ffc fl=0x8 stack_top=0xd
DEBUG:root:COMPARE
DEBUG:root:tick=373  ac=0x0 ip=0x6 ar=0x21 dr=0x0 sp=0x1ffc fl=0x5 stack_top=0xd
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=375  ac=0x0 ip=0xe ar=0x6 dr=0x0 sp=0x1ffc fl=0x5 stack_top=0xd
DEBUG:root:POP
DEBUG:root:tick=379  ac=0xd ip=0xf ar=0x1ffc dr=0xd sp=0x1ffd fl=0x5 stack_top=0x21
DEBUG:root:POPN
DEBUG:root:tick=380  ac=0xd ip=0x10 ar=0x1ffc dr=0xd sp=0x1ffe fl=0x5 stack_top=0x13
DEBUG:root:RETURN
DEBUG:root:tick=384  ac=0xd ip=0x13 ar=0x1ffe dr=0x13 sp=0x1fff fl=0x5 stack_top=?
DEBUG:root:HALT
INFO:root:instr: 142 ticks: 384
Hello, world!
```

Пример проверки исходного кода:

```bash
% poetry run pytest . -v
========================================================================================================= test session starts =========================================================================================================
platform win32 -- Python 3.11.0, pytest-7.4.4, pluggy-1.4.0 -- C:\Users\andrk\AppData\Local\pypoetry\Cache\virtualenvs\acl-4Gl_EPqY-py3.11\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Programming\Projects\Python\ITMO\CompArchFall2023\ACL3
configfile: pyproject.toml
plugins: golden-0.2.2
collected 4 items                                                                                                                                                                                                                      

integration_test.py::test_translator_and_machine[golden/cat.yml] PASSED                                                                                                                                                          [ 25%]
integration_test.py::test_translator_and_machine[golden/hello.yml] PASSED                                                                                                                                                        [ 50%]
integration_test.py::test_translator_and_machine[golden/hello_user_name.yml] PASSED                                                                                                                                              [ 75%]
integration_test.py::test_translator_and_machine[golden/prob2.yml] PASSED                                                                                                                                                        [100%]

========================================================================================================== 4 passed in 1.33s ========================================================================================================== 

% poetry run ruff check .

% poetry run ruff format .
6 files left unchanged
```

Статистика:

```text
| ФИО                        | алг   | LoC | code инстр. | инстр. | такт. | вариант                                                                        |
| Черных Роман Александрович | hello | 1   | 20          | 142    | 384   | `lisp | acc | neum | hw | instr | struct | stream | mem | cstr | prob2 | 8bit` |
| Черных Роман Александрович | cat   | 1   | 10          | 50     | 162   | `lisp | acc | neum | hw | instr | struct | stream | mem | cstr | prob2 | 8bit` |
| Черных Роман Александрович | prob2 | 11  | 121         | 1773   | 4600  | `lisp | acc | neum | hw | instr | struct | stream | mem | cstr | prob2 | 8bit` |
```
