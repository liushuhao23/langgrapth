from typing import Final, Tuple
from langgraph.store.postgres import PostgresStore




DB_URL = "postgresql://admin:123456@localhost:5432/test_db"
with PostgresStore.from_conn_string(DB_URL) as store:
    store.setup();
    USERS_NS: Final[Tuple[str]] = ("users", )
    PREFERENCES_KEY: Final[str] = "preferences"
    namespace1 = (*USERS_NS, "Alice")
    value1 = {
        "course": "计算机组成原理",
        "sports": "跑步",
        "food": "紫光园奶皮子酸奶"
    }
    namespace2 = (*USERS_NS, "Bob")
    value2 = {
        "course": "数字电路与模拟电路",
        "sports": "跑步",
        "food": "奶皮子糖葫芦"
    }

    namespace3 = (*USERS_NS, "Black")
    value3 = {
        "course": "数字电路与模拟电路",
        "sports": "羽毛球",
        "food": "紫光园奶皮子酸奶"
    }

    store.put(namespace1, PREFERENCES_KEY, value1)
    store.put(namespace2, PREFERENCES_KEY, value2)
    store.put(namespace3, PREFERENCES_KEY, value3)
