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

| Название   | Разрядность | Описание                                                                    |
|------------|-------------|-----------------------------------------------------------------------------|
| `acr`      | 32          | аккумулятор                                                                 |
| `ipr`      | 32          | указатель на адрес исполняемой инструкции                                   |
| `inr`      | 32          | содержит текущую исполняемую инструкцию                                     |
| `adr`      | 32          | регистр адреса, используется для чтения/записи                              |
| `dar`      | 32          | регистр данных, используется для чтения/записи                              |
| `spr`      | 32          | указатель на вершину стека                                                  |
| `flr`      | 4           | регистр флагов, содержит флаги по результатам операции (NZVC)               |

Доступ к памяти данных осуществляется при помощи регистров `adr`, `dar`. Для чтения необходимо задать адрес ячейки для 
чтения. Для записи необходимо задать адрес и значение для записи.

Ввод/вывод отображается на память. Для вывода необходимо выполнить запись в ячейку памяти по определенному адресу. 
Для ввода необходимо выполнить чтение определенной (другой) ячейки памяти.

Имеется 5 типов адресации:
  * непосредственная
  * абсолютная
  * относительная (`ipr`)
  * относительная (`spr`)
  * относительная косвенная (`spr`)

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
| `popn`        | снять значение со стека без записи куда-либо (spr--)                |
| `cmp <val>`   | установить флаги по результату операции вычитания из аккумулятора   |
| `jme <addr>`  | переход по адресу если равно (Z == 1)                               |
| `jmg <addr>`  | переход по адресу если значение больше (N == V and Z == 0)          |
| `jmge <addr>` | переход по адресу если значение больше или равно (N == V or Z == 1) |
| `jmp <addr>`  | безусловный переход по адресу                                       |
| `inc <addr>`  | инкремент значения по адресу (без изменения аккумулятора)           |
| `dec <addr>`  | декремент значения по адресу (без изменения аккумулятора)           |
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
  * инкремент `ipr` после любой другой инструкции

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
                      latch --->+-------+                               +-------+<--- latch   
                                |  acr  |---------+           +---------|  adr  |             
                   +----------->+-------+         |           |         +-------+<-----------+
                   |                              |           |                              |
                   |  latch --->+-------+         |           |         +-------+<--- latch  |
                   |            |  ipr  |-------+ |           | +-------|  dar  |            |
                   +----------->+-------+       | |           | |       +-------+<-----------+
                   |                            | |           | |                            |
                   |            +-------+       | | 0       0 | |       +-------+<--- latch  |
                   |            |  inr  |-----+ | | |       | | | +-----|  spr  |            |
                   |            +-------+     | | | |       | | | |     +-------+<-----------+
                   |                          v v v v       v v v v                          |
                   |                        +---------+   +---------+                        |
                   |                sel --->|   MUX   |   |   MUX   |<--- sel                |
                   |                        +---------+   +---------+                        |
                   |                             |             |                             |
                   |                             v             v                             |
         latch     |           inv_left --->+---------+   +---------+<--- inv_right          |
           |       |          extend_20 --->|          \_/          |<--- (+1)               |
           v       |                        |                       |                        |  
       +-------+   |             opcode --->|          ALU          |                        |
       |  flr  |<----------------------------\                     /                         |
       +-------+   |                          +-------------------+                          |
                   |                                    |                                    |
                   +------------------------------------+------------------------------------+
```

#### Взаимодействие с памятью

```text
                                    read   write
                                      |      |
                                      v      v
                                  +------------+----------------------------------------------------------+
                          +------>| Comparator |                                                          |
    +-------+      sel    |       +------------+------------------------------+                           |
    |  ipr  |----+  |     |           |      |                                |                           |
    +-------+    |  |     |   +--------------------------------------------------------------------+      |
                 v  v     |   |       v      v                                |                    |      |
    +-------+   +-----+   |   |   +------------+                              v read signal        v      v write signal
    |  adr  |-->| MUX |---+------>|            |                        +--------------+        +--------------+
    +-------+   +-----+       |   |            |            input ----->|    INPUT     |        |    OUTPUT    |-----> output
                              |   |   MEMORY   |                        |    BUFFER    |        |    BUFFER    |
                              |   |            |                        +--------------+        +--------------+
              +--------+      |   |            |                               |
   latch ---->|  dar   |------+-->|            |-------+  +--------------------+
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
  * `read_memory` - чтение данных по адресу `adr` в `dar`:
    * из памяти данных (`dar <- mem[adr]`)
    * из порта ввода `input`:
      * извлечь из входного буфера токен и подать его на выход
      * если буфер пуст - исключение
  * `write_memory` - запись данных `dar` по адресу `adr`:
    * в память данных (`mem[adr] <- dar`)
    * в порт вывода `output`:
      * записать значение `dar` в буфер вывода
  * `latch_acr`, `latch_ipr`, `latch_bur`, `latch_adr`, `latch_spr` - записать значение с выхода ALU в регистр
  * `sel_dar` - выбрать значение из памяти, выхода ALU или буфера ввода для записи в `dar`
  * `latch_dar` - записать выставленное значение в `dar`
  * `sel_addr` - выбрать адресный регистр для операции с памятью (`adr` или `ipr`)
  * `latch_flr` - записать значения флагов операции суммы из ALU в `flr`
  * `sel_left`, `sel_right` - выбрать значения для левого и правого входов ALU
  * `alu_opcode` - выбор операции для осуществления на ALU (sum, mul, div, mod)
  * `alu_inv_left`, `alu_inv_right` - инвертировать левый вход, правый вход ALU соответственно
  * `alu_extend_20` - расширить знак 20 бит левого входа ALU
  * `alu_plus_1` - прибавить 1 к операции суммы ALU


#### ControlUnit

```text
                                                                         +---------+
                                                                     +-->|  step   |--+                 input   output
                                                         latch       |   | counter |  |                   |       ^
         latch                  +--------------+          |          |   +---------+  v                   v       |
           |           read --->|              |          v          |     +---------------+  signals   +-----------+
           v                    |    MEMORY    |       +--------+    +-----|  instruction  |----------->| DataPath* |
        +-------+    +-----+    |              |------>|   ir   |--------->|    decoder    |            +-----------+
   +--->|  ipr  |--->| MUX |--->|              |       +--------+          +---------------+               |    |
   |    +-------+    +-----+    +--------------+                                         ^                 |    |
   |                  ^   ^                                                              |                 |    |
   |    +-------+     |   |                                                              +-----------------+    |
   |    |  adr  |-----+  sel                                                               feedback_signals     |
   |    +-------+                                                                                               |
   +------------------------------------------------------------------------------------------------------------+
```

Реализован в классе `ControlUnit`.

Особенности:
  * hardwired (реализован полностью на Python, для каждого типа инструкции можно однозначно 
    определить сигналы и их порядок для каждого такта исполнения инструкции)
  * step counter - необходим для много-тактовых инструкций

Сигналы:
  * `read_memory` - чтение данных по адресу `ipr` в `inr` (`inr <- mem[ipr]`)
  * `latch_inr` - записать значение из памяти инструкций в `inr`
  * signals - управляющие сигналы в DataPath
  * feedback_signals - сигналы обратной связи (`flr`)

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
        "tag": "**spr",
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
        "tag": "*ipr",
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
        "tag": "*spr",
        "val": 1
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "inc",
      "arg": {
        "tag": "*spr",
        "val": 0
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "ld",
      "arg": {
        "tag": "*spr",
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
        "tag": "*ipr",
        "val": 2
      }
    }
  },
  {
    "tag": "INSTRUCTION",
    "instr": {
      "op": "jmp",
      "arg": {
        "tag": "*ipr",
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
DEBUG:root:tick=0    acr=0x0 ipr=0x0 adr=0x0 dar=0x0 spr=0x1fff flr=0x0 stack_top=?
DEBUG:root:JUMP
DEBUG:root:tick=1    acr=0x0 ipr=0x11 adr=0x0 dar=0x0 spr=0x1fff flr=0x0 stack_top=?
DEBUG:root:LOAD
DEBUG:root:tick=3    acr=0x14 ipr=0x12 adr=0x0 dar=0x14 spr=0x1fff flr=0x0 stack_top=?
DEBUG:root:CALL
DEBUG:root:tick=7    acr=0x14 ipr=0x1 adr=0x1ffe dar=0x13 spr=0x1ffe flr=0x0 stack_top=0x13
DEBUG:root:PUSH
DEBUG:root:tick=10   acr=0x14 ipr=0x2 adr=0x1ffd dar=0x14 spr=0x1ffd flr=0x0 stack_top=0x14
DEBUG:root:LOAD
DEBUG:root:tick=12   acr=0x0 ipr=0x3 adr=0x1ffd dar=0x0 spr=0x1ffd flr=0x0 stack_top=0x14
DEBUG:root:PUSH
DEBUG:root:tick=15   acr=0x0 ipr=0x4 adr=0x1ffc dar=0x0 spr=0x1ffc flr=0x0 stack_top=0x0
DEBUG:root:LOAD
DEBUG:root:tick=20   acr=0x48 ipr=0x5 adr=0x14 dar=0x48 spr=0x1ffc flr=0x0 stack_top=0x0
DEBUG:root:COMPARE
DEBUG:root:tick=22   acr=0x48 ipr=0x6 adr=0x14 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x0
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=23   acr=0x48 ipr=0x7 adr=0x14 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x0
DEBUG:root:STORE
DEBUG:root:output: '' <- 'H'
DEBUG:root:tick=26   acr=0x48 ipr=0x8 adr=0x15b4 dar=0x48 spr=0x1ffc flr=0x1 stack_top=0x0
DEBUG:root:INCREMENT
DEBUG:root:tick=30   acr=0x48 ipr=0x9 adr=0x1ffd dar=0x15 spr=0x1ffc flr=0x1 stack_top=0x0
DEBUG:root:INCREMENT
DEBUG:root:tick=34   acr=0x48 ipr=0xa adr=0x1ffc dar=0x1 spr=0x1ffc flr=0x1 stack_top=0x1
DEBUG:root:LOAD
DEBUG:root:tick=37   acr=0x1 ipr=0xb adr=0x1ffc dar=0x1 spr=0x1ffc flr=0x1 stack_top=0x1
DEBUG:root:COMPARE
DEBUG:root:tick=39   acr=0x1 ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x1
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=40   acr=0x1 ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x1
DEBUG:root:JUMP
DEBUG:root:tick=42   acr=0x1 ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x1
DEBUG:root:LOAD
DEBUG:root:tick=47   acr=0x65 ipr=0x5 adr=0x15 dar=0x65 spr=0x1ffc flr=0x8 stack_top=0x1
DEBUG:root:COMPARE
DEBUG:root:tick=49   acr=0x65 ipr=0x6 adr=0x15 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x1
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=50   acr=0x65 ipr=0x7 adr=0x15 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x1
DEBUG:root:STORE
DEBUG:root:output: 'H' <- 'e'
DEBUG:root:tick=53   acr=0x65 ipr=0x8 adr=0x15b4 dar=0x65 spr=0x1ffc flr=0x1 stack_top=0x1
DEBUG:root:INCREMENT
DEBUG:root:tick=57   acr=0x65 ipr=0x9 adr=0x1ffd dar=0x16 spr=0x1ffc flr=0x1 stack_top=0x1
DEBUG:root:INCREMENT
DEBUG:root:tick=61   acr=0x65 ipr=0xa adr=0x1ffc dar=0x2 spr=0x1ffc flr=0x1 stack_top=0x2
DEBUG:root:LOAD
DEBUG:root:tick=64   acr=0x2 ipr=0xb adr=0x1ffc dar=0x2 spr=0x1ffc flr=0x1 stack_top=0x2
DEBUG:root:COMPARE
DEBUG:root:tick=66   acr=0x2 ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x2
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=67   acr=0x2 ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x2
DEBUG:root:JUMP
DEBUG:root:tick=69   acr=0x2 ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x2
DEBUG:root:LOAD
DEBUG:root:tick=74   acr=0x6c ipr=0x5 adr=0x16 dar=0x6c spr=0x1ffc flr=0x8 stack_top=0x2
DEBUG:root:COMPARE
DEBUG:root:tick=76   acr=0x6c ipr=0x6 adr=0x16 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x2
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=77   acr=0x6c ipr=0x7 adr=0x16 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x2
DEBUG:root:STORE
DEBUG:root:output: 'He' <- 'l'
DEBUG:root:tick=80   acr=0x6c ipr=0x8 adr=0x15b4 dar=0x6c spr=0x1ffc flr=0x1 stack_top=0x2
DEBUG:root:INCREMENT
DEBUG:root:tick=84   acr=0x6c ipr=0x9 adr=0x1ffd dar=0x17 spr=0x1ffc flr=0x1 stack_top=0x2
DEBUG:root:INCREMENT
DEBUG:root:tick=88   acr=0x6c ipr=0xa adr=0x1ffc dar=0x3 spr=0x1ffc flr=0x1 stack_top=0x3
DEBUG:root:LOAD
DEBUG:root:tick=91   acr=0x3 ipr=0xb adr=0x1ffc dar=0x3 spr=0x1ffc flr=0x1 stack_top=0x3
DEBUG:root:COMPARE
DEBUG:root:tick=93   acr=0x3 ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x3
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=94   acr=0x3 ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x3
DEBUG:root:JUMP
DEBUG:root:tick=96   acr=0x3 ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x3
DEBUG:root:LOAD
DEBUG:root:tick=101  acr=0x6c ipr=0x5 adr=0x17 dar=0x6c spr=0x1ffc flr=0x8 stack_top=0x3
DEBUG:root:COMPARE
DEBUG:root:tick=103  acr=0x6c ipr=0x6 adr=0x17 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x3
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=104  acr=0x6c ipr=0x7 adr=0x17 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x3
DEBUG:root:STORE
DEBUG:root:output: 'Hel' <- 'l'
DEBUG:root:tick=107  acr=0x6c ipr=0x8 adr=0x15b4 dar=0x6c spr=0x1ffc flr=0x1 stack_top=0x3
DEBUG:root:INCREMENT
DEBUG:root:tick=111  acr=0x6c ipr=0x9 adr=0x1ffd dar=0x18 spr=0x1ffc flr=0x1 stack_top=0x3
DEBUG:root:INCREMENT
DEBUG:root:tick=115  acr=0x6c ipr=0xa adr=0x1ffc dar=0x4 spr=0x1ffc flr=0x1 stack_top=0x4
DEBUG:root:LOAD
DEBUG:root:tick=118  acr=0x4 ipr=0xb adr=0x1ffc dar=0x4 spr=0x1ffc flr=0x1 stack_top=0x4
DEBUG:root:COMPARE
DEBUG:root:tick=120  acr=0x4 ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x4
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=121  acr=0x4 ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x4
DEBUG:root:JUMP
DEBUG:root:tick=123  acr=0x4 ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x4
DEBUG:root:LOAD
DEBUG:root:tick=128  acr=0x6f ipr=0x5 adr=0x18 dar=0x6f spr=0x1ffc flr=0x8 stack_top=0x4
DEBUG:root:COMPARE
DEBUG:root:tick=130  acr=0x6f ipr=0x6 adr=0x18 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x4
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=131  acr=0x6f ipr=0x7 adr=0x18 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x4
DEBUG:root:STORE
DEBUG:root:output: 'Hell' <- 'o'
DEBUG:root:tick=134  acr=0x6f ipr=0x8 adr=0x15b4 dar=0x6f spr=0x1ffc flr=0x1 stack_top=0x4
DEBUG:root:INCREMENT
DEBUG:root:tick=138  acr=0x6f ipr=0x9 adr=0x1ffd dar=0x19 spr=0x1ffc flr=0x1 stack_top=0x4
DEBUG:root:INCREMENT
DEBUG:root:tick=142  acr=0x6f ipr=0xa adr=0x1ffc dar=0x5 spr=0x1ffc flr=0x1 stack_top=0x5
DEBUG:root:LOAD
DEBUG:root:tick=145  acr=0x5 ipr=0xb adr=0x1ffc dar=0x5 spr=0x1ffc flr=0x1 stack_top=0x5
DEBUG:root:COMPARE
DEBUG:root:tick=147  acr=0x5 ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x5
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=148  acr=0x5 ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x5
DEBUG:root:JUMP
DEBUG:root:tick=150  acr=0x5 ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x5
DEBUG:root:LOAD
DEBUG:root:tick=155  acr=0x2c ipr=0x5 adr=0x19 dar=0x2c spr=0x1ffc flr=0x8 stack_top=0x5
DEBUG:root:COMPARE
DEBUG:root:tick=157  acr=0x2c ipr=0x6 adr=0x19 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x5
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=158  acr=0x2c ipr=0x7 adr=0x19 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x5
DEBUG:root:STORE
DEBUG:root:output: 'Hello' <- ','
DEBUG:root:tick=161  acr=0x2c ipr=0x8 adr=0x15b4 dar=0x2c spr=0x1ffc flr=0x1 stack_top=0x5
DEBUG:root:INCREMENT
DEBUG:root:tick=165  acr=0x2c ipr=0x9 adr=0x1ffd dar=0x1a spr=0x1ffc flr=0x1 stack_top=0x5
DEBUG:root:INCREMENT
DEBUG:root:tick=169  acr=0x2c ipr=0xa adr=0x1ffc dar=0x6 spr=0x1ffc flr=0x1 stack_top=0x6
DEBUG:root:LOAD
DEBUG:root:tick=172  acr=0x6 ipr=0xb adr=0x1ffc dar=0x6 spr=0x1ffc flr=0x1 stack_top=0x6
DEBUG:root:COMPARE
DEBUG:root:tick=174  acr=0x6 ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x6
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=175  acr=0x6 ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x6
DEBUG:root:JUMP
DEBUG:root:tick=177  acr=0x6 ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x6
DEBUG:root:LOAD
DEBUG:root:tick=182  acr=0x20 ipr=0x5 adr=0x1a dar=0x20 spr=0x1ffc flr=0x8 stack_top=0x6
DEBUG:root:COMPARE
DEBUG:root:tick=184  acr=0x20 ipr=0x6 adr=0x1a dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x6
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=185  acr=0x20 ipr=0x7 adr=0x1a dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x6
DEBUG:root:STORE
DEBUG:root:output: 'Hello,' <- ' '
DEBUG:root:tick=188  acr=0x20 ipr=0x8 adr=0x15b4 dar=0x20 spr=0x1ffc flr=0x1 stack_top=0x6
DEBUG:root:INCREMENT
DEBUG:root:tick=192  acr=0x20 ipr=0x9 adr=0x1ffd dar=0x1b spr=0x1ffc flr=0x1 stack_top=0x6
DEBUG:root:INCREMENT
DEBUG:root:tick=196  acr=0x20 ipr=0xa adr=0x1ffc dar=0x7 spr=0x1ffc flr=0x1 stack_top=0x7
DEBUG:root:LOAD
DEBUG:root:tick=199  acr=0x7 ipr=0xb adr=0x1ffc dar=0x7 spr=0x1ffc flr=0x1 stack_top=0x7
DEBUG:root:COMPARE
DEBUG:root:tick=201  acr=0x7 ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x7
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=202  acr=0x7 ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x7
DEBUG:root:JUMP
DEBUG:root:tick=204  acr=0x7 ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x7
DEBUG:root:LOAD
DEBUG:root:tick=209  acr=0x77 ipr=0x5 adr=0x1b dar=0x77 spr=0x1ffc flr=0x8 stack_top=0x7
DEBUG:root:COMPARE
DEBUG:root:tick=211  acr=0x77 ipr=0x6 adr=0x1b dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x7
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=212  acr=0x77 ipr=0x7 adr=0x1b dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x7
DEBUG:root:STORE
DEBUG:root:output: 'Hello, ' <- 'w'
DEBUG:root:tick=215  acr=0x77 ipr=0x8 adr=0x15b4 dar=0x77 spr=0x1ffc flr=0x1 stack_top=0x7
DEBUG:root:INCREMENT
DEBUG:root:tick=219  acr=0x77 ipr=0x9 adr=0x1ffd dar=0x1c spr=0x1ffc flr=0x1 stack_top=0x7
DEBUG:root:INCREMENT
DEBUG:root:tick=223  acr=0x77 ipr=0xa adr=0x1ffc dar=0x8 spr=0x1ffc flr=0x1 stack_top=0x8
DEBUG:root:LOAD
DEBUG:root:tick=226  acr=0x8 ipr=0xb adr=0x1ffc dar=0x8 spr=0x1ffc flr=0x1 stack_top=0x8
DEBUG:root:COMPARE
DEBUG:root:tick=228  acr=0x8 ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x8
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=229  acr=0x8 ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x8
DEBUG:root:JUMP
DEBUG:root:tick=231  acr=0x8 ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x8
DEBUG:root:LOAD
DEBUG:root:tick=236  acr=0x6f ipr=0x5 adr=0x1c dar=0x6f spr=0x1ffc flr=0x8 stack_top=0x8
DEBUG:root:COMPARE
DEBUG:root:tick=238  acr=0x6f ipr=0x6 adr=0x1c dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x8
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=239  acr=0x6f ipr=0x7 adr=0x1c dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x8
DEBUG:root:STORE
DEBUG:root:output: 'Hello, w' <- 'o'
DEBUG:root:tick=242  acr=0x6f ipr=0x8 adr=0x15b4 dar=0x6f spr=0x1ffc flr=0x1 stack_top=0x8
DEBUG:root:INCREMENT
DEBUG:root:tick=246  acr=0x6f ipr=0x9 adr=0x1ffd dar=0x1d spr=0x1ffc flr=0x1 stack_top=0x8
DEBUG:root:INCREMENT
DEBUG:root:tick=250  acr=0x6f ipr=0xa adr=0x1ffc dar=0x9 spr=0x1ffc flr=0x1 stack_top=0x9
DEBUG:root:LOAD
DEBUG:root:tick=253  acr=0x9 ipr=0xb adr=0x1ffc dar=0x9 spr=0x1ffc flr=0x1 stack_top=0x9
DEBUG:root:COMPARE
DEBUG:root:tick=255  acr=0x9 ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x9
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=256  acr=0x9 ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x9
DEBUG:root:JUMP
DEBUG:root:tick=258  acr=0x9 ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0x9
DEBUG:root:LOAD
DEBUG:root:tick=263  acr=0x72 ipr=0x5 adr=0x1d dar=0x72 spr=0x1ffc flr=0x8 stack_top=0x9
DEBUG:root:COMPARE
DEBUG:root:tick=265  acr=0x72 ipr=0x6 adr=0x1d dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x9
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=266  acr=0x72 ipr=0x7 adr=0x1d dar=0x0 spr=0x1ffc flr=0x1 stack_top=0x9
DEBUG:root:STORE
DEBUG:root:output: 'Hello, wo' <- 'r'
DEBUG:root:tick=269  acr=0x72 ipr=0x8 adr=0x15b4 dar=0x72 spr=0x1ffc flr=0x1 stack_top=0x9
DEBUG:root:INCREMENT
DEBUG:root:tick=273  acr=0x72 ipr=0x9 adr=0x1ffd dar=0x1e spr=0x1ffc flr=0x1 stack_top=0x9
DEBUG:root:INCREMENT
DEBUG:root:tick=277  acr=0x72 ipr=0xa adr=0x1ffc dar=0xa spr=0x1ffc flr=0x1 stack_top=0xa
DEBUG:root:LOAD
DEBUG:root:tick=280  acr=0xa ipr=0xb adr=0x1ffc dar=0xa spr=0x1ffc flr=0x1 stack_top=0xa
DEBUG:root:COMPARE
DEBUG:root:tick=282  acr=0xa ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xa
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=283  acr=0xa ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xa
DEBUG:root:JUMP
DEBUG:root:tick=285  acr=0xa ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xa
DEBUG:root:LOAD
DEBUG:root:tick=290  acr=0x6c ipr=0x5 adr=0x1e dar=0x6c spr=0x1ffc flr=0x8 stack_top=0xa
DEBUG:root:COMPARE
DEBUG:root:tick=292  acr=0x6c ipr=0x6 adr=0x1e dar=0x0 spr=0x1ffc flr=0x1 stack_top=0xa
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=293  acr=0x6c ipr=0x7 adr=0x1e dar=0x0 spr=0x1ffc flr=0x1 stack_top=0xa
DEBUG:root:STORE
DEBUG:root:output: 'Hello, wor' <- 'l'
DEBUG:root:tick=296  acr=0x6c ipr=0x8 adr=0x15b4 dar=0x6c spr=0x1ffc flr=0x1 stack_top=0xa
DEBUG:root:INCREMENT
DEBUG:root:tick=300  acr=0x6c ipr=0x9 adr=0x1ffd dar=0x1f spr=0x1ffc flr=0x1 stack_top=0xa
DEBUG:root:INCREMENT
DEBUG:root:tick=304  acr=0x6c ipr=0xa adr=0x1ffc dar=0xb spr=0x1ffc flr=0x1 stack_top=0xb
DEBUG:root:LOAD
DEBUG:root:tick=307  acr=0xb ipr=0xb adr=0x1ffc dar=0xb spr=0x1ffc flr=0x1 stack_top=0xb
DEBUG:root:COMPARE
DEBUG:root:tick=309  acr=0xb ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xb
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=310  acr=0xb ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xb
DEBUG:root:JUMP
DEBUG:root:tick=312  acr=0xb ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xb
DEBUG:root:LOAD
DEBUG:root:tick=317  acr=0x64 ipr=0x5 adr=0x1f dar=0x64 spr=0x1ffc flr=0x8 stack_top=0xb
DEBUG:root:COMPARE
DEBUG:root:tick=319  acr=0x64 ipr=0x6 adr=0x1f dar=0x0 spr=0x1ffc flr=0x1 stack_top=0xb
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=320  acr=0x64 ipr=0x7 adr=0x1f dar=0x0 spr=0x1ffc flr=0x1 stack_top=0xb
DEBUG:root:STORE
DEBUG:root:output: 'Hello, worl' <- 'd'
DEBUG:root:tick=323  acr=0x64 ipr=0x8 adr=0x15b4 dar=0x64 spr=0x1ffc flr=0x1 stack_top=0xb
DEBUG:root:INCREMENT
DEBUG:root:tick=327  acr=0x64 ipr=0x9 adr=0x1ffd dar=0x20 spr=0x1ffc flr=0x1 stack_top=0xb
DEBUG:root:INCREMENT
DEBUG:root:tick=331  acr=0x64 ipr=0xa adr=0x1ffc dar=0xc spr=0x1ffc flr=0x1 stack_top=0xc
DEBUG:root:LOAD
DEBUG:root:tick=334  acr=0xc ipr=0xb adr=0x1ffc dar=0xc spr=0x1ffc flr=0x1 stack_top=0xc
DEBUG:root:COMPARE
DEBUG:root:tick=336  acr=0xc ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xc
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=337  acr=0xc ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xc
DEBUG:root:JUMP
DEBUG:root:tick=339  acr=0xc ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xc
DEBUG:root:LOAD
DEBUG:root:tick=344  acr=0x21 ipr=0x5 adr=0x20 dar=0x21 spr=0x1ffc flr=0x8 stack_top=0xc
DEBUG:root:COMPARE
DEBUG:root:tick=346  acr=0x21 ipr=0x6 adr=0x20 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0xc
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=347  acr=0x21 ipr=0x7 adr=0x20 dar=0x0 spr=0x1ffc flr=0x1 stack_top=0xc
DEBUG:root:STORE
DEBUG:root:output: 'Hello, world' <- '!'
DEBUG:root:tick=350  acr=0x21 ipr=0x8 adr=0x15b4 dar=0x21 spr=0x1ffc flr=0x1 stack_top=0xc
DEBUG:root:INCREMENT
DEBUG:root:tick=354  acr=0x21 ipr=0x9 adr=0x1ffd dar=0x21 spr=0x1ffc flr=0x1 stack_top=0xc
DEBUG:root:INCREMENT
DEBUG:root:tick=358  acr=0x21 ipr=0xa adr=0x1ffc dar=0xd spr=0x1ffc flr=0x1 stack_top=0xd
DEBUG:root:LOAD
DEBUG:root:tick=361  acr=0xd ipr=0xb adr=0x1ffc dar=0xd spr=0x1ffc flr=0x1 stack_top=0xd
DEBUG:root:COMPARE
DEBUG:root:tick=363  acr=0xd ipr=0xc adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xd
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=364  acr=0xd ipr=0xd adr=0x1ffc dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xd
DEBUG:root:JUMP
DEBUG:root:tick=366  acr=0xd ipr=0x4 adr=0xd dar=0x80 spr=0x1ffc flr=0x8 stack_top=0xd
DEBUG:root:LOAD
DEBUG:root:tick=371  acr=0x0 ipr=0x5 adr=0x21 dar=0x0 spr=0x1ffc flr=0x8 stack_top=0xd
DEBUG:root:COMPARE
DEBUG:root:tick=373  acr=0x0 ipr=0x6 adr=0x21 dar=0x0 spr=0x1ffc flr=0x5 stack_top=0xd
DEBUG:root:JUMP_EQUAL
DEBUG:root:tick=375  acr=0x0 ipr=0xe adr=0x6 dar=0x0 spr=0x1ffc flr=0x5 stack_top=0xd
DEBUG:root:POP
DEBUG:root:tick=379  acr=0xd ipr=0xf adr=0x1ffc dar=0xd spr=0x1ffd flr=0x5 stack_top=0x21
DEBUG:root:POPN
DEBUG:root:tick=380  acr=0xd ipr=0x10 adr=0x1ffc dar=0xd spr=0x1ffe flr=0x5 stack_top=0x13
DEBUG:root:RETURN
DEBUG:root:tick=384  acr=0xd ipr=0x13 adr=0x1ffe dar=0x13 spr=0x1fff flr=0x5 stack_top=?
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
integration_test.py::test_translator_and_machine[golden/prob1.yml] PASSED                                                                                                                                                        [100%]

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
