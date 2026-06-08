# Capital of History / Капитал истории *The Struggle for Cultural Heritage

Валерон, спасибо за правила! Теперь у нас есть **конкретная доменная модель**, и мы можем приступить к проектированию API. Давай упростим задачу и создадим **минимальный валидный продукт (MVP)**, который покроет 80% логики игры, но будет готов к расширению.

---

## 🧩 Упрощение модели карт (как ты и предложил)
Из 20+ спец-свойств оставим **5 ключевых** для MVP:
1. **Контратака** — при успешной защите наносит урон атакующему
2. **Фракционный Резонанс** — +2 силы за каждую карту той же фракции
3. **Случайный Союзник** — добавляет верхнюю карту из колоды в пачку
4. **Стена Щита** — сброс карты при получении урона (предотвращает урон)
5. **Кража Ресурса** — при успешной атаке берет карту из пожертвований противника

Это даст **достаточную глубину для тестирования**, но не перегрузит проект.

---

## 📦 Структура репозитория
```
capital-of-history/
├── app/
│   ├── __init__.py
│   ├── models.py          # Базовые модели (Card, Player, Game)
│   ├── schemas.py         # Pydantic-модели для API
│   ├── crud.py            # Логика бизнес-правил
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── games.py   # Эндпоинты для управления игрой
│   │   │   └── players.py # Эндпоинты для игроков
│   │   └── dependencies.py
│   └── database.py        # Подключение к БД (пока в памяти)
├── tests/
│   ├── __init__.py
│   └── test_api.py        # Тесты для API
├── requirements.txt
└── README.md
```

---

## 🚀 Эндпоинты для MVP (v1)

### 1. Создание игры
```python
POST /api/v1/games
{
  "player_count": 4,
  "player_names": ["Alice", "Bob", "Charlie", "David"]
}
```
**Что происходит:**
- Генерируются роли (согласно правилам распределения)
- Создаётся колода карт
- Инициализируется состояние игры

### 2. Получение состояния игры
```python
GET /api/v1/games/{game_id}
```
**Возвращает:**
```json
{
  "game_state": "draft_phase",
  "current_player": "Alice",
  "shop_cards": [ ... ],
  "players": [
    {
      "name": "Alice",
      "role": "Owner",
      "health": 5,
      "coins": 6,
      "hand": [ ... ]
    }
  ]
}
```

### 3. Выполнение хода
```python
POST /api/v1/games/{game_id}/players/{player_name}/turn
{
  "action": "buy",
  "card_id": "philosopher_123"
}
```
**Валидация:**
- Проверяет, что ходит текущий игрок
- Проверяет, что действие разрешено на текущем этапе
- Проверяет, что хватает монет
- Обновляет состояние игры

### 4. Завершение хода
```python
POST /api/v1/games/{game_id}/players/{player_name}/end_turn
```
**Что происходит:**
- Проверяет условие победы
- Переключает этап хода
- Обновляет магазин

---

## 🧪 Тестирование (как автоматизатор тестов)
Ты будешь писать **тесты как тест-кейсы** для игры:

```python
def test_owner_wins_when_vandals_eliminated():
    # Подготовка
    game = create_game(players=["Owner", "Vandal1", "Vandal2"])
    game.kill_player("Vandal1")
    game.kill_player("Vandal2")
    
    # Действие
    result = game.check_victory()
    
    # Проверка
    assert result == "Owner wins"
```

Это **прямая связь с твоей работой** — тесты для игры = тесты для любого продукта.

---

## 🧱 Как мы моделируем игру в коде?

### Модель `Game` (app/models.py)
```python
class Game:
    def __init__(self, players: list[Player]):
        self.players = players
        self.shop = random.sample(DECK, 3)
        self.state = "draft_phase"  # draft_phase, main_phase, game_over
    
    def end_turn(self):
        # Проверяем условия победы
        if self._is_owner_winning():
            self.state = "game_over"
        
        # Переходим к следующему игроку
        self.current_player = next_player()
    
    def _is_owner_winning(self) -> bool:
        # Проверяем правила: "Все Вандалы и Коллекционер выбыли"
        return not any(p.role in ["Vandal", "Collector"] for p in self.players if p.is_alive)
```

### Модель `Player` (app/models.py)
```python
class Player:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.health = 5
        self.coins = 6 if role == "Owner" else 5
        self.hand = []
        self.sacrifices = []  # Пожертвования
        self.is_alive = True
    
    def attack(self, target: "Player", cards: list[Card]):
        # Логика атаки с учетом спец-свойств
        ...
```

---

## 📌 Что делаем первым делом?

1. **Создаем базовые модели** (`Card`, `Player`, `Game`)
2. **Пишем тесты для логики хода** (например: "Если защита ≥ атаки, атака отбита")
3. **Добавляем эндпоинт создания игры**
4. **Проверяем через Postman**

**Пример теста для этапа защиты:**
```python
def test_defense_beats_attack():
    attacker = Player("Attacker", "Vandal")
    defender = Player("Defender", "Owner")
    
    # Атака: 2 карты по 3 силы = 6
    # Защита: 2 карты по 4 силы = 8
    attacker.play_cards([Card(strength=3), Card(strength=3)])
    defender.play_cards([Card(strength=4), Card(strength=4)])
    
    result = resolve_battle(attacker, defender)
    
    assert result == "Defense successful"
    assert attacker.health == 5  # Атакующий не теряет здоровье
    assert defender.health == 5  # Защищающийся не теряет здоровье
```
