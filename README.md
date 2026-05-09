# Bot Colosseum

Стенд для пошаговых игр между ботами. Боты — любые исполняемые программы, общение через стандартные потоки ввода-вывода. Состояние игры сохраняется после каждого хода.

---

## Быстрый старт

```bash
python run_match.py \
  --game tictactoe \
  --bot1 "python bots/random_bot.py" \
  --bot2 "python bots/tictactoe/minimax_bot.py"
```

---

## Структура проекта

```
bot-colosseum/
├── colosseum/
│   ├── game.py          # Абстрактный базовый класс игры
│   ├── bot.py           # Обёртка над subprocess-ботом
│   ├── runner.py        # Оркестрация матча
│   └── persistence.py   # Сохранение истории и снапшотов
├── games/
│   └── tictactoe/
│       └── game.py      # Реализация крестиков-ноликов
├── bots/
│   ├── random_bot.py            # Универсальный случайный бот
│   └── tictactoe/
│       ├── greedy_bot.py        # Жадный бот (выигрыш → блок → центр → угол)
│       └── minimax_bot.py       # Оптимальный бот (minimax + alpha-beta)
├── matches/             # Сохранённые матчи (в .gitignore)
└── run_match.py         # CLI
```

---

## Как работает стенд

Стенд (`MatchRunner`) оркеструет матч между двумя ботами в рамках одной игры:

```
MatchRunner
├── Game  — правила и логика (не знает про ботов)
├── Bot 0 — subprocess игрока 0
└── Bot 1 — subprocess игрока 1
```

На каждом шаге:

```
1. runner узнаёт у game список допустимых ходов
2. runner отправляет боту текущее состояние + допустимые ходы
3. бот возвращает выбранный ход
4. runner проверяет, что ход допустим
5. runner передаёт ход в game → получает новое состояние
6. runner сохраняет ход и снапшот состояния на диск
7. если игра завершена — цикл останавливается
```

Если бот нарушает протокол (таймаут, некорректный JSON, недопустимый ход) — он проигрывает по техническим причинам (forfeit).

### Сохранение матча

Каждый матч получает уникальный ID и сохраняется в `matches/{match_id}/`:

```
matches/{match_id}/
├── meta.json        # игра, боты, время начала
├── moves.jsonl      # история ходов (одна JSON-строка на ход)
├── result.json      # итог матча
└── snapshots/
    ├── step_0000.json   # полное состояние после хода 0
    ├── step_0001.json
    └── ...
```

---

## Обобщённая модель игры

Каждая игра — Python-класс, наследующий `colosseum.game.Game`. Игра описывает только правила — она ничего не знает про ботов и транспорт.

```python
from colosseum.game import Game

class MyGame(Game):

    @property
    def num_players(self) -> int:
        # Количество игроков
        return 2

    def initial_state(self) -> dict:
        # Начальное состояние игры.
        # Должно быть JSON-сериализуемым dict.
        # Обязательное поле: "current_player" (int, 0-based).
        return {"board": [...], "current_player": 0}

    def valid_moves(self, state: dict) -> list:
        # Список допустимых ходов для текущего игрока.
        # Каждый ход — JSON-сериализуемый dict.
        return [{"row": 0, "col": 1}, ...]

    def apply_move(self, state: dict, move: dict) -> dict:
        # Применить ход к состоянию, вернуть новое состояние.
        # Не мутировать входное состояние!
        ...

    def is_terminal(self, state: dict) -> bool:
        # True если игра завершена.
        ...

    def get_result(self, state: dict) -> dict:
        # Результат завершённой игры.
        # Ключи — индексы игроков (int), значения — float:
        #   1.0 = победа, 0.5 = ничья, 0.0 = поражение
        return {0: 1.0, 1: 0.0}

    def render(self, state: dict) -> str:
        # Текстовое представление состояния для вывода в консоль.
        ...
```

**Соглашения по состоянию:**
- Состояние — обычный `dict`, полностью JSON-сериализуемый.
- Обязательное поле `"current_player"` — индекс игрока, чья сейчас очередь (0-based).
- Каждая игра сама определяет остальную схему состояния.

### Регистрация игры

Добавить игру в `GAME_REGISTRY` в файле `run_match.py`:

```python
GAME_REGISTRY = {
    "tictactoe": "games.tictactoe.game.TicTacToe",
    "mygame":    "games.mygame.game.MyGame",       # новая игра
}
```

---

## Обобщённая модель бота

Бот — любой исполняемый файл на любом языке. Стенд запускает его как subprocess и общается через stdin/stdout в формате JSON (по одной строке на сообщение).

### Протокол

**Стенд → бот** (пишется в stdin бота):

```json
{
  "step": 4,
  "player": 1,
  "state": { "board": [[1,0,2],[0,1,0],[0,0,0]], "current_player": 1 },
  "valid_moves": [{"row": 0, "col": 1}, {"row": 1, "col": 1}, ...]
}
```

| Поле | Тип | Описание |
|------|-----|----------|
| `step` | int | Номер хода (с нуля) |
| `player` | int | Индекс игрока, которым ходит бот |
| `state` | dict | Полное текущее состояние игры |
| `valid_moves` | list | Список допустимых ходов |

**Бот → стенд** (пишется в stdout бота):

```json
{"move": {"row": 1, "col": 1}}
```

Ход должен быть одним из элементов `valid_moves`. Если бот вернул ход не из этого списка — он проигрывает.

### Жизненный цикл бота

Процесс бота запускается **один раз** на весь матч и остаётся живым до его конца. Это позволяет боту хранить внутреннее состояние между ходами. Бот читает запросы из stdin в цикле и отвечает на каждый.

### Минимальный бот (Python)

```python
import json, sys, random

for line in sys.stdin:
    req = json.loads(line.strip())
    move = random.choice(req["valid_moves"])
    print(json.dumps({"move": move}), flush=True)
```

### Минимальный бот (любой язык)

Условия:
- читать одну строку из stdin → парсить JSON
- выбрать ход из `valid_moves`
- вывести в stdout одну строку `{"move": ...}` и сбросить буфер (`flush`)
- повторять в цикле

### Форфейт

Бот проигрывает автоматически если:
- не ответил за отведённое время (по умолчанию 5 секунд)
- вернул невалидный JSON
- вернул ход не из `valid_moves`
- процесс завершился раньше времени

---

## Параметры CLI

```
python run_match.py --game <name>
                    --bot1 "<command>"
                    --bot2 "<command>"
                    [--timeout <seconds>]   # таймаут на ход (по умолчанию 5.0)
                    [--output <dir>]        # куда сохранять (по умолчанию matches/)
                    [--quiet]               # не выводить ходы в консоль
```

### Примеры

```bash
# Случайный против жадного
python run_match.py --game tictactoe \
  --bot1 "python bots/random_bot.py" \
  --bot2 "python bots/tictactoe/greedy_bot.py"

# Жадный против оптимального
python run_match.py --game tictactoe \
  --bot1 "python bots/tictactoe/greedy_bot.py" \
  --bot2 "python bots/tictactoe/minimax_bot.py"

# Бот на другом языке
python run_match.py --game tictactoe \
  --bot1 "python bots/random_bot.py" \
  --bot2 "./my_bot"

# Тихий режим (только результат)
python run_match.py --game tictactoe \
  --bot1 "python bots/random_bot.py" \
  --bot2 "python bots/random_bot.py" \
  --quiet
```

---

## Доступные игры и боты

### Крестики-нолики (`tictactoe`)

Классическая игра 3×3. Побеждает тот, кто первым выстроит три своих знака в ряд (по горизонтали, вертикали или диагонали).

| Бот | Команда | Описание |
|-----|---------|----------|
| Random | `python bots/random_bot.py` | Случайный ход |
| Greedy | `python bots/tictactoe/greedy_bot.py` | Выигрыш → блок → центр → угол |
| Minimax | `python bots/tictactoe/minimax_bot.py` | Оптимальная игра, никогда не проигрывает |
