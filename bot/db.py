import hashlib
from typing import Annotated
from typing_extensions import Doc
import aiosqlite

status = Annotated[bool, Doc("operation status")]
balance = Annotated[int, Doc("balance")]

class DB:
    def __init__(self, path: str):
        self._db_path = path
        self._db = None

    async def connect(self):
        self._db = await aiosqlite.connect(self._db_path)

    async def check_balance(self, name: str, password: str) -> balance:
        async with self._db.execute(
            "SELECT BALANCE FROM USERS WHERE NAME=? AND PASSWORD=?",
            (name, hashlib.sha256(password.encode()).hexdigest(),)) as cursor:
            if result := await cursor.fetchone():
                return result[0]
            else:
                return None

    async def transfer(self, name: str, password: str, value: float, endpoint: str) -> status:
        async with self._db.execute(
            "SELECT BALANCE FROM USERS WHERE NAME=? AND PASSWORD=?",
            (name, hashlib.sha256(password.encode()).hexdigest()),
        ) as cursor:
            # guide how you should NOT do
            cursor: aiosqlite.Cursor

            if value <= 0:
                return False

            if not (sender_b := await cursor.fetchone()):
                return False
            sender_b = sender_b[0]

            await cursor.execute("SELECT BALANCE FROM USERS WHERE NAME=?", (endpoint,))

            if not (receiver_b := await cursor.fetchone()):
                return False
            receiver_b = receiver_b[0]

            if (new_sender_b := sender_b-value) < 0:
                return False

            await cursor.execute("UPDATE USERS SET BALANCE=? WHERE NAME=? AND PASSWORD=?", (new_sender_b, name,))
            if cursor.rowcount != 1:
                return False

            await cursor.execute("UPDATE USERS SET BALANCE=? WHERE NAME=?", (receiver_b+value, endpoint,))
            if cursor.rowcount != 1:
                return False

            await self._db.commit()

            return True

    async def check_is_username_exists(self, name: str) -> status:
        async with self._db.execute("SELECT 1 FROM USERS WHERE NAME=?", (name,)) as cursor:
            if await cursor.fetchone():
                return True
            return False

    async def check_is_valid_password(self, name: str, password: str) -> status:
        async with self._db.execute(
            "SELECT 1 FROM USERS WHERE NAME=? AND password=?",
            (name, hashlib.sha256(password.encode()).hexdigest(),)
        ) as cursor:
            if await cursor.fetchone():
                return True
            return False

    async def update_password(self, name: str, oldpassword: str, newpassword: str) -> status:
        async with self._db.execute(
            "UPDATE USERS SET PASSWORD=? WHERE NAME=? AND PASSWORD=?",
            (hashlib.sha256(newpassword.encode()).hexdigest(),
            name,
            hashlib.sha256(oldpassword.encode()).hexdigest(),)
        ) as cursor:
            if cursor.rowcount == 1:
                await self._db.commit()
                return True
            return False
