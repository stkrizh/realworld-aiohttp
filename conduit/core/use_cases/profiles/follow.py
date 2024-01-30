__all__ = [
    "FollowInput",
    "FollowResult",
    "FollowUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.profile import Profile, ProfileRepository, UpdateProfileInput
from conduit.core.entities.user import UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class FollowInput(WithAuthenticationInput):
    username: Username

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class FollowResult:
    profile: Profile | None


class FollowUseCase(UseCase[FollowInput, FollowResult]):
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self._profile_repository = profile_repository

    async def execute(self, input: FollowInput, /) -> FollowResult:
        """Follow an user.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        profile = await self._profile_repository.get_by_username(input.username, by=user_id)
        if profile is None:
            LOG.info("could not follow profile, profile not found", extra={"input": input})
            return FollowResult(None)
        followed_profile = await self._profile_repository.update(
            profile.id,
            UpdateProfileInput(is_following=True),
            by=user_id,
        )
        LOG.info("profile is followed", extra={"input": input, "profile": followed_profile})
        return FollowResult(followed_profile)
