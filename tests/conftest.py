from datetime import timedelta

from scripts.db_default_tables_values import link_role_permission
from src.models import Permission
from src.models import Role
from src.core.config import settings
from src.models import User
from src.services.utils import (
    create_access_token,
    create_refresh_token,
    get_tokens,
    get_password_hash,
)
from src.repositories.core import get_async_session
from src.models.core import Base

import os

import pytest
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport


from src.main import app
from tests.utils import fake_factory


from testcontainers.postgres import PostgresContainer

# Database configuration
postgres = PostgresContainer("postgres:16-alpine")


@pytest.fixture(scope="session", autouse=True)
def setup_db_container(request):
    postgres.start()

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)
    os.environ["DB_CONN"] = postgres.get_connection_url(driver="asyncpg")
    os.environ["DB_HOST"] = postgres.get_container_host_ip()
    os.environ["DB_PORT"] = postgres.get_exposed_port(postgres.port)
    os.environ["DB_USERNAME"] = postgres.username
    os.environ["DB_PASSWORD"] = postgres.password
    os.environ["DB_NAME"] = postgres.dbname

    return os.getenv("DB_CONN")


@pytest.fixture(scope="session")
async def engine_test(setup_db_container):
    engine_test = create_async_engine(setup_db_container, poolclass=NullPool)
    return engine_test


@pytest.fixture(scope="function")
async def get_test_session(engine_test):
    """
    Function to get a database session
    """
    async_test_session = async_sessionmaker(
        engine_test,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_test_session() as session:
        yield session


@pytest.fixture(scope="session")
async def get_test_session_session(engine_test):
    async_test_session = async_sessionmaker(
        engine_test,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_test_session() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
async def dependency_overrides(get_test_session):
    app.dependency_overrides[get_async_session] = lambda: get_test_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_db(engine_test):
    """
    Prepare the database before running tests
    """
    async with engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        os.system("python -m scripts/db_default_tables_values.py")
    yield
    async with engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True, scope="session")
async def add_default_roles_permissions(get_test_session_session, prepare_db):
    default_roles = settings.ROLES.split()
    default_permissions = settings.PERMISSIONS.split()
    for role in default_roles:
        if role == "user":
            get_test_session_session.add(Role(name=role, id=1))
        if role == "admin":
            get_test_session_session.add(Role(name=role, id=2))

    for permission in default_permissions:
        get_test_session_session.add(Permission(name=permission))

    await get_test_session_session.commit()


@pytest.fixture(autouse=True, scope="session")
async def link_roles_permissions(
    get_test_session_session, add_default_roles_permissions
):
    await link_role_permission(get_test_session_session, "admin", ["all"])
    await link_role_permission(get_test_session_session, "user", ["owner", "read_only"])


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    """
    Fixture to create an asynchronous client for testing
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
async def add_user(get_test_session, request):
    user_type = request.param
    user_generator = {
        "base": fake_factory.generate_base_user,
        "verified": fake_factory.generate_verified_user,
        "blocked": fake_factory.generate_blocked_user,
        "admin": fake_factory.generate_admin_user,
    }[user_type]

    user = user_generator()
    user_for_db = user.copy()
    user_for_db["password"] = get_password_hash(user["password"])
    session = get_test_session
    new_user = User(**user_for_db)
    session.add(new_user)
    await session.commit()
    return user


@pytest.fixture(scope="function")
async def login_fake_user(client, add_user):
    response = await client.post(
        "/api/auth/login",
        data={"username": add_user["username"], "password": add_user["password"]},
    )
    data = response.json()
    data.update(add_user)
    return data


@pytest.fixture(scope="function")
def get_access_token(add_user):
    return create_access_token(
        data={"user_id": str(add_user["id"]), "user_role_id": add_user["role_id"]},
        expires_delta=timedelta(hours=1),
    )


@pytest.fixture(scope="function")
def get_refresh_token():
    return create_refresh_token(
        data={"user_id": 1, "user_role": "user"},
    )


@pytest.fixture(scope="function")
def create_tokens():
    data = {"user_id": 1, "user_role": "user"}
    return get_tokens(data)


@pytest.fixture(scope="function")
def get_expired_token():
    return create_access_token(
        data={"user_id": 1, "user_role": "admin"}, expires_delta=timedelta(hours=-1)
    )


@pytest.fixture(scope="function")
def get_invalid_token():
    token = create_access_token(
        data={"user_id": 1, "user_role": "admin"}, expires_delta=timedelta(hours=-1)
    )
    token = "qwer" + token[4:]
    return token
