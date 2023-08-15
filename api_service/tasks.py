import argparse

from tortoise import run_async

from tasks import (
    remover,
)

TASKS = {
    "remover": remover.remover,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spitter cron tasks")
    parser.add_argument("task", type=str, help="Input task name")
    args = parser.parse_args()
    task = TASKS.get(args.task)

    if task:
        run_async(task())
    else:
        raise ValueError(
            f'Unknown task name: {args.task}. Available tasks are {", ".join(TASKS)}'
        )
