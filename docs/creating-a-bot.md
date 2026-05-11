# Как написать бота

Бот — любой исполняемый файл, который читает JSON из stdin и пишет JSON в stdout. Язык программирования не важен.

---

## Протокол

Стенд запускает бота **один раз** на весь матч и держит процесс живым. На каждый ход:

**Runner → Bot (stdin, одна строка):**
```json
{
  "step": 4,
  "player": 1,
  "state": { "current_player": 1, "...": "..." },
  "valid_moves": [{"row": 0, "col": 1}, {"row": 2, "col": 0}]
}
```

**Bot → Runner (stdout, одна строка):**
```json
{"move": {"row": 0, "col": 1}}
```

Ход обязан быть одним из элементов `valid_moves`. Если нет — бот проигрывает по техническим причинам (forfeit).

**Важно:** всегда делать `flush` после вывода — иначе ответ зависнет в буфере.

---

## Шаблоны

### Python

```python
#!/usr/bin/env python3
import json
import sys


def choose_move(state, player, valid_moves):
    # Реализовать логику выбора хода
    ...
    return valid_moves[0]


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
        move = choose_move(req["state"], req["player"], req["valid_moves"])
        print(json.dumps({"move": move}), flush=True)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
```

### JavaScript (Node.js)

```javascript
const readline = require("readline");

const rl = readline.createInterface({ input: process.stdin });

function chooseMove(state, player, validMoves) {
  // Реализовать логику
  return validMoves[0];
}

rl.on("line", (line) => {
  line = line.trim();
  if (!line) return;
  const req = JSON.parse(line);
  const move = chooseMove(req.state, req.player, req.valid_moves);
  process.stdout.write(JSON.stringify({ move }) + "\n");
});
```

```bash
colosseum --game tictactoe --bot1 "python bots/random_bot.py" --bot2 "node my_bot.js"
```

### Go

```go
package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "os"
)

type Request struct {
    Step       int                    `json:"step"`
    Player     int                    `json:"player"`
    State      map[string]interface{} `json:"state"`
    ValidMoves []map[string]interface{} `json:"valid_moves"`
}

func chooseMove(req Request) map[string]interface{} {
    // Реализовать логику
    return req.ValidMoves[0]
}

func main() {
    scanner := bufio.NewScanner(os.Stdin)
    for scanner.Scan() {
        var req Request
        json.Unmarshal(scanner.Bytes(), &req)
        move := chooseMove(req)
        resp, _ := json.Marshal(map[string]interface{}{"move": move})
        fmt.Println(string(resp))
    }
}
```

```bash
colosseum --game nim --bot1 "python bots/nim/optimal_bot.py" --bot2 "./my_bot"
```

---

## Внутреннее состояние бота

Так как процесс бота живёт весь матч, можно хранить данные между ходами в переменных:

```python
import json
import sys

# Переменные между ходами
move_history = []
prev_piles = None

for line in sys.stdin:
    req = json.loads(line.strip())
    state = req["state"]
    player = req["player"]
    valid_moves = req["valid_moves"]

    # Отслеживать историю
    move_history.append(req["step"])

    # Вычислить ход противника (пример для Nim)
    if prev_piles is not None:
        for i, (old, new) in enumerate(zip(prev_piles, state["piles"])):
            if old != new:
                opponent_move = {"pile": i, "count": old - new}
                break

    move = valid_moves[0]  # заменить реальной логикой

    # Сохранить для следующего хода
    prev_piles = state["piles"][:]

    print(json.dumps({"move": move}), flush=True)
```

---

## Советы

### Читать valid_moves, не считать самому

Стенд уже посчитал допустимые ходы и передал их в `valid_moves`. Не надо пересчитывать логику игры в боте — просто выбирать из готового списка.

```python
# Правильно: выбирать из списка
move = random.choice(valid_moves)

# Лишняя работа: вычислять самому
moves = [(r, c) for r in range(3) for c in range(3) if state["board"][r][c] == 0]
```

### Использовать state["current_player"]

Поле `current_player` в state совпадает с полем `player` в запросе. Используй то, что удобнее:

```python
player = req["player"]  # то же самое, что req["state"]["current_player"]
```

### Ошибки писать в stderr

Вывод в stdout нарушает протокол — всё что туда попадает будет воспринято как ответ.

```python
print("DEBUG: thinking...", file=sys.stderr)  # не нарушает протокол
print("DEBUG: thinking...")                    # сломает парсинг!
```

### Таймаут по умолчанию — 5 секунд

Если бот думает дольше — он проигрывает. Для сложных алгоритмов (minimax с большой глубиной) увеличь таймаут:

```bash
colosseum --game mygame --bot1 "..." --bot2 "..." --timeout 30
```

---

## Размещение ботов

Рекомендуемая структура:

```
bots/
├── random_bot.py          # универсальный, для любой игры
└── mygame/
    ├── simple_bot.py      # простая эвристика
    └── smart_bot.py       # более сложная стратегия
```

Универсальные боты (которые работают с любой игрой через `valid_moves`) размещать прямо в `bots/`. Боты, использующие специфику конкретной игры — в `bots/{game_name}/`.

---

## Проверка бота вручную

Можно протестировать бота отдельно от стенда — просто передать JSON в stdin:

```bash
echo '{"step":0,"player":0,"state":{"board":[[0,0,0],[0,0,0],[0,0,0]],"current_player":0},"valid_moves":[{"row":0,"col":0}]}' | python bots/tictactoe/greedy_bot.py
```

Ожидаемый вывод:
```json
{"move": {"row": 1, "col": 1}}
```
