"""Data models for Quests, Objectives, and Story Progression."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class QuestStatus(Enum):
    """Lifecycle state of a quest."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    READY_TO_TURN_IN = "ready_to_turn_in"
    COMPLETED = "completed"
    FAILED = "failed"


class ObjectiveType(Enum):
    """Types of requirements for completing a quest objective."""
    WIN_ENCOUNTER = "win_encounter"
    GATHER_ITEM = "gather_item"
    VISIT_CITY = "visit_city"
    CRAFT_ITEM = "craft_item"
    TALK_TO_NPC = "talk_to_npc"


@dataclass
class QuestObjective:
    """A single task within a quest."""
    id: str
    description: str
    objective_type: ObjectiveType
    target_id: str                # e.g. encounter_id, item_id, city_id
    required_count: int = 1
    current_count: int = 0

    def is_complete(self) -> bool:
        return self.current_count >= self.required_count

    def update_progress(self, amount: int = 1) -> bool:
        """Increment progress. Returns True if newly completed."""
        was_complete = self.is_complete()
        self.current_count = min(self.required_count, self.current_count + amount)
        return not was_complete and self.is_complete()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "objective_type": self.objective_type.value,
            "target_id": self.target_id,
            "required_count": self.required_count,
            "current_count": self.current_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestObjective":
        return cls(
            id=data["id"],
            description=data["description"],
            objective_type=ObjectiveType(data["objective_type"]),
            target_id=data["target_id"],
            required_count=data.get("required_count", 1),
            current_count=data.get("current_count", 0),
        )


@dataclass
class QuestReward:
    """Rewards awarded upon completing a quest."""
    gold: int = 0
    experience: int = 0
    cards: List[str] = field(default_factory=list)
    items: Dict[str, int] = field(default_factory=dict)
    unlocked_city_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gold": self.gold,
            "experience": self.experience,
            "cards": list(self.cards),
            "items": dict(self.items),
            "unlocked_city_ids": list(self.unlocked_city_ids),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestReward":
        return cls(
            gold=data.get("gold", 0),
            experience=data.get("experience", 0),
            cards=list(data.get("cards", [])),
            items=dict(data.get("items", {})),
            unlocked_city_ids=list(data.get("unlocked_city_ids", [])),
        )


@dataclass
class Quest:
    """A full story or side quest."""
    id: str
    title: str
    description: str
    chapter: int = 1
    is_main_quest: bool = True
    status: QuestStatus = QuestStatus.NOT_STARTED
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: QuestReward = field(default_factory=QuestReward)

    def is_all_objectives_met(self) -> bool:
        return all(obj.is_complete() for obj in self.objectives)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "chapter": self.chapter,
            "is_main_quest": self.is_main_quest,
            "status": self.status.value,
            "objectives": [o.to_dict() for o in self.objectives],
            "rewards": self.rewards.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quest":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            chapter=data.get("chapter", 1),
            is_main_quest=data.get("is_main_quest", True),
            status=QuestStatus(data.get("status", "not_started")),
            objectives=[QuestObjective.from_dict(o) for o in data.get("objectives", [])],
            rewards=QuestReward.from_dict(data.get("rewards", {})),
        )


# Starter Quest Line
DEFAULT_QUESTS: Dict[str, Quest] = {
    "quest_ch1_01": Quest(
        id="quest_ch1_01",
        title="Gefahr auf der Handelsstraße",
        description="Befreie die Handelsstraße von den Wölfen und erreiche Silverport.",
        chapter=1,
        is_main_quest=True,
        objectives=[
            QuestObjective(
                id="obj_defeat_wolves",
                description="Besiege das wilde Wolfsrudel",
                objective_type=ObjectiveType.WIN_ENCOUNTER,
                target_id="enc_wild_wolf",
                required_count=1,
            ),
            QuestObjective(
                id="obj_reach_silverport",
                description="Reise nach Silverport",
                objective_type=ObjectiveType.VISIT_CITY,
                target_id="city_silverport",
                required_count=1,
            ),
        ],
        rewards=QuestReward(
            gold=100,
            experience=200,
            unlocked_city_ids=["city_silverport"],
        ),
    )
}


def get_quest(quest_id: str) -> Optional[Quest]:
    return DEFAULT_QUESTS.get(quest_id)
