__all__ = [
    "UnfollowInput",
    "UnfollowResult",
    "UnfollowUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.profile import Profile, ProfileRepository
from conduit.core.entities.user import UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class UnfollowInput(WithAuthenticationInput):
    username: Username

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class UnfollowResult:
    profile: Profile | None


class UnfollowUseCase(UseCase[UnfollowInput, UnfollowResult]):
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self._profile_repository = profile_repository

    async def execute(self, input: UnfollowInput, /) -> UnfollowResult:
        """Unfollow an user.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        profile = await self._profile_repository.unfollow(input.username, following_by=user_id)
        LOG.info("profile is unfollowed", extra={"input": input, "profile": profile})
        return UnfollowResult(profile)