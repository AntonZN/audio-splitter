import asyncio


async def run_command(cmd: str) -> bool:
    process = await asyncio.subprocess.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE
    )

    await process.communicate()

    if process.returncode == 0:
        return True
    else:
        return False
