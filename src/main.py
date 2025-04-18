from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints import router as api_endpoint_router
from src.config.events import execute_backend_server_event_handler, terminate_backend_server_event_handler
from src.config.manager import settings
from src.utilities.exceptions.database import EntityDoesNotExist
from src.utilities.exceptions.exceptions import *


def initialize_backend_application() -> FastAPI:
    app = FastAPI(**settings.set_backend_app_attributes)  # type: ignore

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=settings.IS_ALLOWED_CREDENTIALS,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    app.add_exception_handler(UserNotFoundException, user_not_found_exception_handler)
    app.add_exception_handler(UserAlreadyExistsException, user_already_exists_exception_handler)
    app.add_exception_handler(InvalidCredentialsException, invalid_credentials_exception_handler)
    app.add_exception_handler(AuthorizationHeaderException, authorization_header_exception_handler)
    app.add_exception_handler(SecurityException, security_exception_handler)
    app.add_exception_handler(EntityDoesNotExist, entity_does_not_exist_exception_handler)
    app.add_exception_handler(EntityAlreadyExists, entity_already_exists_exception_handler)
    app.add_exception_handler(InternalServerErrorException, internal_server_error_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    app.add_event_handler(
        "startup",
        execute_backend_server_event_handler(backend_app=app),
    )
    app.add_event_handler(
        "shutdown",
        terminate_backend_server_event_handler(backend_app=app),
    )

    app.include_router(router=api_endpoint_router, prefix=settings.API_PREFIX)

    return app


backend_app: FastAPI = initialize_backend_application()

if __name__ == "__main__":
    uvicorn.run(
        app="main:backend_app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        workers=settings.SERVER_WORKERS,
        log_level=settings.LOGGING_LEVEL,
    )
