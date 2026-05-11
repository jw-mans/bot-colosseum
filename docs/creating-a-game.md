# Как добавить новую игру

Каждая игра — Python-класс, наследующий `colosseum.game.Game`. Игра отвечает только за правила: начальное состояние, допустимые ходы, переходы между состояниями и определение победителя. Про ботов и транспорт она ничего не знает.

---

## Шаг 1. Создать папку игры

```
games/
└── mygame/
    ├── __init__.py   # пустой
    └── game.py       # реализация
```

```bash
mkdir games/mygame
touch games/mygame/__init__.py
```

---

## Шаг 2. Реализовать класс Game

Скопируй шаблон и заполни каждый метод:

```python
# games/mygame/game.py
import copy
from colosseum.game import Game


class MyGame(Game):

    @property
    def num_players(self) -> int:
        """Количество игроков. Обычно 2."""
        return 2

    def initial_state(self) -> dict:
        """
        Начальное состояние игры.

        Требования:
        - Возвращает JSON-сериализуемый dict.
        - Обязательное поле: "current_player" (int, 0-based) —
          индекс того, кто ходит первым.
        """
        return {
            "current_player": 0,
            # ... поля специфичные для игры
        }

    def valid_moves(self, state: dict) -> list:
        """
        Список допустимых ходов для текущего игрока.

        - Каждый ход — JSON-сериализуемый dict.
        - Список не должен быть пустым пока is_terminal() == False.
        - Runner автоматически проверяет, что ход бота входит в этот список.
        """
        return [{"action": "..."}, ...]

    def apply_move(self, state: dict, move: dict) -> dict:
        """
        Применить ход к состоянию и вернуть новое состояние.

        ВАЖНО: не мутировать входной state — возвращать глубокую копию.
        Используй copy.deepcopy(state) в начале метода.
        """
        new_state = copy.deepcopy(state)
        # ... изменить new_state согласно move
        new_state["current_player"] = 1 - state["current_player"]  # пример для 2 игроков
        return new_state

    def is_terminal(self, state: dict) -> bool:
        """True если игра завершена (победа, ничья, ни одного хода)."""
        return False  # реализовать

    def get_result(self, state: dict) -> dict:
        """
        Результат завершённой игры.

        Возвращает dict: {player_index (int): score (float)}
          1.0 = победа
          0.5 = ничья
          0.0 = поражение

        Вызывается только при is_terminal() == True.
        """
        return {0: 1.0, 1: 0.0}  # реализовать

    def render(self, state: dict) -> str:
        """Текстовое представление состояния для вывода в консоль."""
        return str(state)
```

---

## Шаг 3. Зарегистрировать игру в CLI

Открой `run_match.py` и добавь строку в `GAME_REGISTRY`:

```python
GAME_REGISTRY = {
    "tictactoe": "games.tictactoe.game.TicTacToe",
    "nim":       "games.nim.game.Nim",
    "21":        "games.twentyone.game.TwentyOne",
    "mygame":    "games.mygame.game.MyGame",   # ← добавить
}
```

---

## Шаг 4. Проверить с универсальным ботом

Универсальный `random_bot.py` работает с любой игрой — идеален для первоначальной проверки:

```bash
colosseum --game mygame \
  --bot1 "python bots/random_bot.py" \
  --bot2 "python bots/random_bot.py"
```

Если матч дошёл до конца без ошибок — базовая реализация работает.

---

## Соглашения

### Состояние (state)

- Всегда обычный `dict`, полностью JSON-сериализуемый (без объектов, set, tuple).
- Обязательное поле `"current_player": int`.
- Не хранить в состоянии ничего лишнего — только то, что нужно для определения следующего хода.
- Иммутабельность: `apply_move` **никогда** не меняет переданный state.

### Ходы (moves)

- Каждый ход — `dict` с понятными ключами: `{"row": 1, "col": 2}`, `{"pile": 0, "count": 3}`, `{"action": "hit"}`.
- Избегать числовых индексов без контекста: `{"move": 5}` хуже, чем `{"col": 5}`.

### Результат

- `get_result` вызывается только на терминальном состоянии.
- Сумма очков не обязана равняться 1 — например, в играх с несколькими победителями допустимо `{0: 1.0, 1: 1.0, 2: 0.0}`.

### Случайность

Если игра использует случайность (перемешанная колода, кубик), инициализировать её в `initial_state()`, результат хранить в state. Это гарантирует воспроизводимость матча по снапшотам.

---

## Полный пример: Connect Four (Четыре в ряд)

Минимальная рабочая реализация для иллюстрации структуры:

```python
import copy
from colosseum.game import Game

ROWS, COLS = 6, 7
WIN = 4


class ConnectFour(Game):

    @property
    def num_players(self):
        return 2

    def initial_state(self):
        return {
            "board": [[0] * COLS for _ in range(ROWS)],
            "current_player": 0,
        }

    def valid_moves(self, state):
        board = state["board"]
        return [{"col": c} for c in range(COLS) if board[0][c] == 0]

    def apply_move(self, state, move):
        new_state = copy.deepcopy(state)
        player = new_state["current_player"]
        mark = player + 1
        col = move["col"]
        board = new_state["board"]
        for row in range(ROWS - 1, -1, -1):
            if board[row][col] == 0:
                board[row][col] = mark
                break
        new_state["current_player"] = 1 - player
        return new_state

    def is_terminal(self, state):
        return self._winner(state) is not None or not self.valid_moves(state)

    def get_result(self, state):
        winner_mark = self._winner(state)
        if winner_mark is None:
            return {0: 0.5, 1: 0.5}
        w = winner_mark - 1
        return {w: 1.0, 1 - w: 0.0}

    def render(self, state):
        symbols = {0: ".", 1: "X", 2: "O"}
        rows = []
        for row in state["board"]:
            rows.append(" ".join(symbols[c] for c in row))
        rows.append(" ".join(str(i) for i in range(COLS)))
        return "\n".join(rows)

    def _winner(self, state):
        board = state["board"]
        for r in range(ROWS):
            for c in range(COLS):
                mark = board[r][c]
                if mark == 0:
                    continue
                for dr, dc in [(0,1),(1,0),(1,1),(1,-1)]:
                    cells = [(r + dr*i, c + dc*i) for i in range(WIN)]
                    if all(0 <= nr < ROWS and 0 <= nc < COLS
                           and board[nr][nc] == mark
                           for nr, nc in cells):
                        return mark
        return None
```

Зарегистрировать как `"connect4": "games.connect4.game.ConnectFour"` и запустить.
