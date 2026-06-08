from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


# 1. Таблица партий
class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    state = Column(String(20), default="draft")
    current_player_id = Column(Integer, ForeignKey("players_in_games.id"), nullable=True)
    round_number = Column(Integer, default=1)
    winner_id = Column(Integer, ForeignKey("players_in_games.id"), nullable=True)

    participants = relationship("PlayerInGame", back_populates="game")
    game_cards = relationship("GameCard", back_populates="game")


# 2. Таблица пользователей
class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    game_participations = relationship("PlayerInGame", back_populates="player")


# 3. Игроки в конкретной партии
class PlayerInGame(Base):
    __tablename__ = "players_in_games"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("players.id"))

    role = Column(String(20))
    health = Column(Integer, default=5)
    coins = Column(Integer, default=5)
    capital = Column(Integer, default=1)
    is_alive = Column(Boolean, default=True)

    game = relationship("Game", back_populates="participants")
    player = relationship("Player", back_populates="game_participations")
    cards = relationship("GameCard", back_populates="player_in_game")


# 4. Спец-свойства
class SpecialAbility(Base):
    __tablename__ = "special_abilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    is_unique = Column(Boolean, default=False)


# 5. Колода карт
class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    faction = Column(String(20))
    base_strength = Column(Integer)
    cost = Column(Integer)
    special_ability_id = Column(Integer, ForeignKey("special_abilities.id"), nullable=True)

    ability = relationship("SpecialAbility")


# 6. Карты в конкретной игре
class GameCard(Base):
    __tablename__ = "game_cards"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("players_in_games.id"), nullable=True)

    location = Column(String(20))
    position = Column(Integer, default=0)

    card = relationship("Card")
    game = relationship("Game", back_populates="game_cards")
    player_in_game = relationship("PlayerInGame", back_populates="cards")