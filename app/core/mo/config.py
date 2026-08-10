from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


ACCESS_ALL_DEPT = "ALL_DEPT"
ACCESS_DIVISION_ONLY = "DIVISION_ONLY"
ACCESS_OWN_ONLY = "OWN_ONLY"

@dataclass(frozen=True)
class MoPositionRank:
    rank_level: int
    rank_code: str
    rank_name: str
    position_id: int
    position_name: str


MO_POSITION_RANKS: tuple[MoPositionRank, ...] = (
    MoPositionRank(
        rank_level=1,
        rank_code="DIRECTOR",
        rank_name="ผู้อำนวยการ",
        position_id=1,
        position_name="ผู้อำนวยการ",
    ),
    MoPositionRank(
        rank_level=1,
        rank_code="DIRECTOR",
        rank_name="ผู้อำนวยการ",
        position_id=5,
        position_name="รองผู้อำนวยการ",
    ),
    MoPositionRank(
        rank_level=2,
        rank_code="MANAGER",
        rank_name="ผู้จัดการ",
        position_id=2,
        position_name="ผู้จัดการเขต",
    ),
    MoPositionRank(
        rank_level=2,
        rank_code="MANAGER",
        rank_name="ผู้จัดการ",
        position_id=6,
        position_name="รองผู้จัดการเขต",
    ),
)


def get_position_rank(position_id: Optional[int]) -> MoPositionRank | None:
    return next(
        (item for item in MO_POSITION_RANKS if item.position_id == position_id),
        None,
    )


def get_workflow_rank(position_id: Optional[int]) -> str | None:
    rank = get_position_rank(position_id)
    return rank.rank_code if rank else None


def get_rank_label(rank_code: str | None) -> str:
    normalized_rank = (rank_code or "").strip().upper()
    rank = next(
        (item for item in MO_POSITION_RANKS if item.rank_code == normalized_rank),
        None,
    )
    return rank.rank_name if rank else "ตำแหน่งอื่น"


def get_workflow_ranks() -> list[str]:
    ranks: dict[str, int] = {}
    for item in MO_POSITION_RANKS:
        ranks[item.rank_code] = item.rank_level
    return [
        rank_code
        for rank_code, _rank_level in sorted(
            ranks.items(), key=lambda item: item[1], reverse=True
        )
    ]


def get_access_level(position_id: Optional[int]) -> str:
    rank = get_position_rank(position_id)
    if not rank:
        return ACCESS_OWN_ONLY
    if rank.rank_level == 1:
        return ACCESS_ALL_DEPT
    return ACCESS_DIVISION_ONLY


def has_department_scope(position_id: Optional[int]) -> bool:
    return get_access_level(position_id) == ACCESS_ALL_DEPT


def is_mo_workflow_position(position_id: Optional[int]) -> bool:
    return get_position_rank(position_id) is not None
