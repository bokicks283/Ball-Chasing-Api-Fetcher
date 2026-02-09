import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, TypeAlias, overload

SteamID64: TypeAlias = int | Literal["me"]

_MIN_17_DIGIT = 10**16
_MAX_17_DIGIT = 10**17 - 1

def _is_17_digit_int(n: int) -> bool:
    return _MIN_17_DIGIT <= n <= _MAX_17_DIGIT

@overload
def parse_steam_id64(value: int) -> int: ...
@overload
def parse_steam_id64(value: Literal["me"]) -> Literal["me"]: ...
@overload
def parse_steam_id64(value: str) -> SteamID64: ...

def parse_steam_id64(value: int | str) -> SteamID64:
    # Reject bool (bool is a subclass of int in Python)
    if type(value) is int:
        if _is_17_digit_int(value):
            return value
        raise ValueError("SteamID64 int must be exactly 17 digits")

    if isinstance(value, str):
        s = value.strip()

        if s == "me":
            return "me"

        # Explicit float/decimal-string rejection
        if "." in s:
            raise ValueError("SteamID64 cannot contain decimal points")

        # Must be only digits for numeric strings
        if not s.isdigit():
            raise ValueError("SteamID64 must be 'me' or digits only")

        if len(s) != 17:
            raise ValueError("SteamID64 numeric string must be exactly 17 digits")

        # safe to convert now
        return int(s)

    raise TypeError("SteamID64 must be int, 'me', or numeric string")

class Platform(str, enum.Enum):
    """Enum representing the different platforms in Rocket League."""
    STEAM = "steam"
    EPIC = "epic"
    PS4 = "ps4"
    XBOX = "xbox"

class Player:
    """Class representing a player in Rocket League."""
    def __init__(
        self, 
        player_id: Optional[str] = None,
        platform: Optional[Platform] = None,
        name: Optional[str] = None
    ):
        if player_id is None and name is None:
            raise ValueError("Either id or name must be provided")
        if player_id is not None and platform is None:
            raise ValueError("Platform must be provided if id is provided")
        self.id = player_id
        self.platform = platform
        self.name = name
        

class Playlist(str, enum.Enum):
    """Enum representing different playlists in Rocket League."""
    UNRANKED_DUELS = "unranked-duels"
    UNRANKED_DOUBLES = "unranked-doubles"
    UNRANKED_STANDARD = "unranked-standard"
    UNRANKED_CHAOS = "unranked-chaos"
    PRIVATE = "private"
    SEASON = "season"
    OFFLINE = "offline"
    RANKED_DUELS = "ranked-duels"
    RANKED_DOUBLES = "ranked-doubles"
    RANKED_SOLO_STANDARD = "ranked-solo-standard"
    RANKED_STANDARD = "ranked-standard"
    SNOWDAY = "snowday"
    ROCKETLABS = "rocketlabs"
    HOOPS = "hoops"
    RUMBLE = "rumble"
    TOURNAMENT = "tournament"
    DROP_SHOT = "dropshot"
    RANKED_HOOPS = "ranked-hoops"
    RANKED_RUMBLE = "ranked-rumble"
    RANKED_DROPSHOT = "ranked-dropshot"
    RANKED_SNOWDAY = "ranked-snowday"
    DROPSHOT_RUMBLE = "dropshot-rumble"
    HEATSEEKER = "heatseeker"
    RANKED_CHAOS = "ranked-chaos"

class MatchResult(str, enum.Enum):
    """Enum representing the result of a match."""
    WIN = "win"
    LOSS = "loss"

class Rank(str, enum.Enum):
    """Enum representing the different ranks in Rocket League."""
    UNRANKED = "unranked"
    BRONZE_1 = "bronze-1"
    BRONZE_2 = "bronze-2"
    BRONZE_3 = "bronze-3"
    SILVER_1 = "silver-1"
    SILVER_2 = "silver-2"
    SILVER_3 = "silver-3"
    GOLD_1 = "gold-1"
    GOLD_2 = "gold-2"
    GOLD_3 = "gold-3"
    PLATINUM_1 = "platinum-1"
    PLATINUM_2 = "platinum-2"
    PLATINUM_3 = "platinum-3"
    DIAMOND_1 = "diamond-1"
    DIAMOND_2 = "diamond-2"
    DIAMOND_3 = "diamond-3"
    CHAMPION_1 = "champion-1"
    CHAMPION_2 = "champion-2"
    CHAMPION_3 = "champion-3"
    GRAND_CHAMPION = "grand-champion"

class SortBy(str, enum.Enum):
    """Enum representing the fields to sort by."""
    UPLOAD_DATE = "upload-date"
    REPLAY_DATE = "replay-date"

class SortDir(str, enum.Enum):
    """Enum representing the sort direction."""
    ASC = "asc"
    DESC = "desc"

@dataclass(slots=True)
class ReplayQuery:
    """Query class for list_replays endpoint.
    """
    players: Optional[list[Player]] = None
    """A list of players to filter by."""
    playlists: Optional[list[Playlist]] = None
    """A list of playlists to filter by."""
    season: Optional[str] = None
    """The season to filter by."""
    match_result: Optional[MatchResult] = None
    """The match result to filter by."""
    min_rank: Optional[Rank] = None
    """The minimum rank to filter by."""
    max_rank: Optional[Rank] = None
    """The maximum rank to filter by."""
    pro: Optional[bool] = None
    """Whether to filter by professional matches."""
    uploader: Optional[SteamID64] = None
    """The uploader to filter by."""
    # TODO: Determine if group_id is a uuid or some other known format.
    group: Optional[str] = None
    """The group id to filter by."""
    map: Optional[str] = None
    """The map to filter by."""
    created_before: Optional[datetime] = None
    """Filter replays created before this date."""
    created_after: Optional[datetime] = None
    """Filter replays created after this date."""
    replay_date_after: Optional[datetime] = None
    """Filter replays by the date they were played."""
    replay_date_before: Optional[datetime] = None
    """Filter replays by the date they were played."""
    count: Optional[int] = 50
    """The number of replays to return per page. default is 50, max is 200"""
    sort_by: Optional[SortBy] = None
    """The field to sort by. default is upload-date."""
    sort_dir: Optional[SortDir] = None
    """The direction to sort by. default is desc."""
    limit: Optional[int] = 50
    """The number of replays to return. The default is 50. If None is passed, all replays will be returned (may be insanely slow)."""
