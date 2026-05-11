# Bot Colosseum

Стенд для пошаговых игр между ботами. Боты — любые исполняемые программы, общение через стандартные потоки ввода-вывода. Состояние игры сохраняется после каждого хода.

---

## Установка

```cmd
pip install -e .
```

После этого в системе появляется команда `colosseum`. Запускать нужно из папки проекта (боты и игры указываются относительными путями).

## Быстрый старт

```cmd
colosseum --game tictactoe --bot1 "python bots/random_bot.py" --bot2 "python bots/tictactoe/minimax_bot.py"
```

Без установки — напрямую через Python:

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
│   ├── tictactoe/       # Крестики-нолики 3×3
│   ├── nim/             # Ним (кучки камней)
│   └── twentyone/       # 21 (Очко)
├── bots/
│   ├── random_bot.py            # Универсальный случайный бот
│   ├── tictactoe/
│   │   ├── greedy_bot.py        # Выигрыш → блок → центр → угол
│   │   └── minimax_bot.py       # Minimax + alpha-beta, оптимальная игра
│   ├── nim/
│   │   ├── optimal_bot.py       # XOR-стратегия Шпрага-Гранди
│   │   ├── greedy_bot.py        # Максимум из наибольшей кучки
│   │   ├── conservative_bot.py  # Всегда берёт 1
│   │   ├── copycat_bot.py       # Повторяет ход противника
│   │   └── endgame_bot.py       # Случайный → оптимальный в эндшпиле
│   └── twentyone/
│       ├── cautious_bot.py      # Хит < 17, стоп ≥ 17 (стратегия дилера)
│       ├── aggressive_bot.py    # Всегда хит до 21 или перебора
│       ├── probability_bot.py   # Хит если P(bust) < 40%
│       └── counter_bot.py       # Адаптируется к состоянию противника
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
        return 2

    def initial_state(self) -> dict:
        # Обязательное поле: "current_player" (int, 0-based)
        return {"board": [...], "current_player": 0}

    def valid_moves(self, state: dict) -> list:
        # Каждый ход — JSON-сериализуемый dict
        return [{"row": 0, "col": 1}, ...]

    def apply_move(self, state: dict, move: dict) -> dict:
        # Не мутировать входное состояние!
        ...

    def is_terminal(self, state: dict) -> bool:
        ...

    def get_result(self, state: dict) -> dict:
        # 1.0 = победа, 0.5 = ничья, 0.0 = поражение
        return {0: 1.0, 1: 0.0}

    def render(self, state: dict) -> str:
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
    "nim":       "games.nim.game.Nim",
    "21":        "games.twentyone.game.TwentyOne",
    "mygame":    "games.mygame.game.MyGame",   # новая игра
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
  "state": { "current_player": 1, "...": "..." },
  "valid_moves": [{"row": 0, "col": 1}, ...]
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

Процесс бота запускается **один раз** на весь матч и остаётся живым до его конца. Это позволяет боту хранить внутреннее состояние между ходами (например, история ходов противника). Бот читает запросы из stdin в цикле и отвечает на каждый.

### Минимальный бот (Python)

```python
import json, sys, random

for line in sys.stdin:
    req = json.loads(line.strip())
    move = random.choice(req["valid_moves"])
    print(json.dumps({"move": move}), flush=True)
```

### Минимальный бот (любой язык)

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
colosseum --game    <name>        # имя игры (обязательно)
          --bot1    "<command>"   # команда запуска бота 1 (обязательно)
          --bot2    "<command>"   # команда запуска бота 2 (обязательно)
          --rounds  <N>           # количество раундов (по умолчанию: 1)
          --timeout <seconds>     # таймаут на ход (по умолчанию: 5.0)
          --output  <dir>         # куда сохранять матчи (по умолчанию: matches/)
          --quiet                 # не выводить ходы в консоль (один раунд)
```

При `--rounds > 1` ходы отдельных матчей не выводятся — показывается только прогресс и итоговая статистика.

### Примеры

```cmd
# Одиночный матч
colosseum --game tictactoe --bot1 "python bots/random_bot.py" --bot2 "python bots/tictactoe/minimax_bot.py"

# Серия из 200 раундов со статистикой
colosseum --game 21 --bot1 "python bots/twentyone/probability_bot.py" --bot2 "python bots/twentyone/cautious_bot.py" --rounds 200

# Проверка детерминированности: 50 раундов в ним
colosseum --game nim --bot1 "python bots/random_bot.py" --bot2 "python bots/nim/optimal_bot.py" --rounds 50

# Бот на другом языке
colosseum --game tictactoe --bot1 "python bots/random_bot.py" --bot2 "./my_bot_binary"

# Тихий режим (только итог, один раунд)
colosseum --game nim --bot1 "python bots/nim/optimal_bot.py" --bot2 "python bots/nim/greedy_bot.py" --quiet
```

---

## Доступные игры

| Игра | Ключ | Описание | Документация |
|------|------|----------|--------------|
| Крестики-нолики | `tictactoe` | 3×3, три в ряд | [games/tictactoe/](games/tictactoe/README.md) |
| Ним | `nim` | Кучки камней, берёт последний — победитель | [games/nim/](games/nim/README.md) |
| 21 (Очко) | `21` | Набери 21 не перебрав | [games/twentyone/](games/twentyone/README.md) |

---

## Документация

| Документ | Описание |
|----------|----------|
| [docs/creating-a-game.md](docs/creating-a-game.md) | Пошаговый гайд по добавлению новой игры с полным примером |
| [docs/creating-a-bot.md](docs/creating-a-bot.md) | Гайд по написанию бота на Python, JS, Go и любом другом языке |
| [games/tictactoe/README.md](games/tictactoe/README.md) | Правила, боты и результаты матчей для крестиков-ноликов |
| [games/nim/README.md](games/nim/README.md) | Правила, XOR-стратегия, боты и результаты матчей для Нима |
| [games/twentyone/README.md](games/twentyone/README.md) | Правила, боты и результаты матчей для 21 |

---

## Вклад в проект

Вклад приветствуется — новые игры, боты, исправления, документация.
Подробнее: [CONTRIBUTING.md](CONTRIBUTING.md)
