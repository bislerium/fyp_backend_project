import enum


class ENotificationChannel(enum.Enum):
    reaction = 0
    poll = 1
    join = 2
    petition = 3
    poke = 4
    remove = 5
    verify = 6


class EPostType(enum.Enum):
    Normal = 0
    Poll = 1
    Request = 2


class EReactionType(enum.Enum):
    Upvote = 0
    Downvote = 1
