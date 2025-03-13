from fastapi import APIRouter, Depends, status
import pydantic

from src.api.dependencies.repository import get_repository
from src.models.schemas.user import UserInResponse, UserInUpdate, UserWithToken
from src.repository.crud.user import UserCRUDRepository
from src.securities.authorizations.jwt import jwt_generator
from src.utilities.exceptions.database import EntityDoesNotExist
from src.utilities.exceptions.http.exc_404 import (
    http_404_exc_email_not_found_request,
    http_404_exc_id_not_found_request,
    http_404_exc_username_not_found_request,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    path="",
    name="users:read-users",
    response_model=list[UserInResponse],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    user_repo: UserCRUDRepository = Depends(get_repository(repo_type=UserCRUDRepository)),
) -> list[UserInResponse]:
    db_users = await user_repo.read_users()
    db_user_list: list = list()

    for db_user in db_users:
        access_token = jwt_generator.generate_access_token(user=db_user)
        user = UserInResponse(
            id=db_user.id,
            authorized_user=UserWithToken(
                token=access_token,
                username=db_user.username,
                email=db_user.email,  # type: ignore
                is_verified=db_user.is_verified,
                is_active=db_user.is_active,
                is_logged_in=db_user.is_logged_in,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at,
            ),
        )
        db_user_list.append(user)

    return db_user_list


@router.get(
    path="/{id}",
    name="users:read-user-by-id",
    response_model=UserInResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    id: int,
    user_repo: UserCRUDRepository = Depends(get_repository(repo_type=UserCRUDRepository)),
) -> UserInResponse:
    try:
        db_user = await user_repo.read_user_by_id(id=id)
        access_token = jwt_generator.generate_access_token(user=db_user)

    except EntityDoesNotExist:
        raise await http_404_exc_id_not_found_request(id=id)

    return UserInResponse(
        id=db_user.id,
        authorized_user=UserWithToken(
            token=access_token,
            username=db_user.username,
            email=db_user.email,  # type: ignore
            is_verified=db_user.is_verified,
            is_active=db_user.is_active,
            is_logged_in=db_user.is_logged_in,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        ),
    )


@router.patch(
    path="/{id}",
    name="users:update-user-by-id",
    response_model=UserInResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    query_id: int,
    update_username: str | None = None,
    update_email: pydantic.EmailStr | None = None,
    update_password: str | None = None,
    user_repo: UserCRUDRepository = Depends(get_repository(repo_type=UserCRUDRepository)),
) -> UserInResponse:
    user_update = UserInUpdate(username=update_username, email=update_email, password=update_password)
    try:
        updated_db_user = await user_repo.update_user_by_id(id=query_id, user_update=user_update)

    except EntityDoesNotExist:
        raise await http_404_exc_id_not_found_request(id=query_id)

    access_token = jwt_generator.generate_access_token(user=updated_db_user)

    return UserInResponse(
        id=updated_db_user.id,
        authorized_user=UserWithToken(
            token=access_token,
            username=updated_db_user.username,
            email=updated_db_user.email,  # type: ignore
            is_verified=updated_db_user.is_verified,
            is_active=updated_db_user.is_active,
            is_logged_in=updated_db_user.is_logged_in,
            created_at=updated_db_user.created_at,
            updated_at=updated_db_user.updated_at,
        ),
    )


@router.delete(path="", name="users:delete-user-by-id", status_code=status.HTTP_200_OK)
async def delete_user(
    id: int, user_repo: UserCRUDRepository = Depends(get_repository(repo_type=UserCRUDRepository))
) -> dict[str, str]:
    try:
        deletion_result = await user_repo.delete_user_by_id(id=id)

    except EntityDoesNotExist:
        raise await http_404_exc_id_not_found_request(id=id)

    return {"notification": deletion_result}
