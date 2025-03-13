from fastapi import APIRouter, status, Depends

from src.api.dependencies.repository import get_repository
from src.models.schemas.user import UserInCreate, UserInLogin, UserInResponse, UserWithToken
from src.repository.crud.user import UserCRUDRepository
from src.securities.authorizations.jwt import jwt_generator
from src.utilities.exceptions.database import EntityAlreadyExists
from src.utilities.exceptions.http.exc_400 import (
    http_exc_400_credentials_bad_signin_request,
    http_exc_400_credentials_bad_signup_request,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/signup",
    name="auth:signup",
    response_model=UserInResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_create: UserInCreate,
    user_repo: UserCRUDRepository = Depends(get_repository(repo_type=UserCRUDRepository)),
) -> UserInResponse:
    try:
        await user_repo.is_username_taken(username=user_create.username)
        await user_repo.is_email_taken(email=user_create.email)

    except EntityAlreadyExists:
        raise await http_exc_400_credentials_bad_signup_request()

    new_user = await user_repo.create_user(user_create=user_create)
    access_token = jwt_generator.generate_access_token(user=new_user)

    return UserInResponse(
        id=new_user.id,
        authorized_user=UserWithToken(
            token=access_token,
            username=new_user.username,
            email=new_user.email,  # type: ignore
            is_verified=new_user.is_verified,
            is_active=new_user.is_active,
            is_logged_in=new_user.is_logged_in,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
        ),
    )


@router.post(
    path="/signin",
    name="auth:signin",
    response_model=UserInResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def signin(
    user_login: UserInLogin,
    user_repo: UserCRUDRepository = Depends(get_repository(repo_type=UserCRUDRepository)),
) -> UserInResponse:
    try:
        db_user = await user_repo.read_user_by_password_authentication(user_login=user_login)

    except Exception:
        raise await http_exc_400_credentials_bad_signin_request()

    access_token = jwt_generator.generate_access_token(user=db_user)

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