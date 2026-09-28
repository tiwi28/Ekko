"""The user's todo list."""

from fastapi import APIRouter, Depends, status
from psycopg import Connection

from app.db import get_conn
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.security import get_current_user_id

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def list_tasks(
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> list[TaskOut]:
    """The user's tasks, open ones first, newest first.

    TODO:
      - SQL: select this user's tasks (uses tasks_user_id_created_at_idx)
      - decide how long completed tasks stay visible
      - carry-over: unfinished tasks from a previous day -> set carried_from_date?
        (could live here, on first load of the day, or in the daily cron)
    """
    raise NotImplementedError("list_tasks")


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> TaskOut:
    """Add a task.

    TODO:
      - SQL: insert and RETURNING the new row
    """
    raise NotImplementedError("create_task")


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    body: TaskUpdate,
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> TaskOut:
    """Rename and/or complete/uncomplete a task.

    TODO:
      - completed=True -> completed_at = now(); completed=False -> NULL
      - SQL: update ... WHERE id = task_id AND user_id = user_id RETURNING ...
        (the user_id check stops people editing each other's tasks)
      - 404 if no row came back
    """
    raise NotImplementedError("update_task")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> None:
    """Delete a task.

    TODO:
      - SQL: delete scoped to user_id; 404 if nothing was deleted (cursor.rowcount)
    """
    raise NotImplementedError("delete_task")
