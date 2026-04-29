from enum import StrEnum

GITHUB_DOMAIN = "github.com"


class AvatarColor(StrEnum):
    RED = '#E57373'
    GREEN = '#81C784'
    BLUE = '#64B5F6'
    YELLOW = '#FFD54F'
    PURPLE = '#BA68C8'


AVATAR_SIZE = 200
AVATAR_TEXT_POSITION = (85, 85)
USERS_PER_PAGE = 12
MAX_AUTOCOMPLETE_SKILLS = 10
