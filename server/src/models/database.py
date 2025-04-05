from config import settings
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from typing import Optional

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def init_database():
    global _client, _db

    try:
        if _client is None:
            _client = AsyncIOMotorClient(settings.MONGODB_URI)
            _db = _client[settings.DB_NAME]
            print("Connect to database successfully!")
    except ConnectionFailure:
        print("Connect to database failed!")
    except Exception as e:
        print(e)


def get_database() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database is not initialized!")
    return _db


def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    return get_database()[collection_name]
