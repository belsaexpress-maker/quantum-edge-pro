import asyncio

from app.ai.bot_engine import run_bot_cycle
from app.ai.quantum_pro_engine import run_quantum_pro_cycle

bot_runner_task = None


async def bot_runner_loop():
    while True:
        try:
            run_bot_cycle()
            run_quantum_pro_cycle()
        except Exception as error:
            print("BOT RUNNER ERROR:", error)

        await asyncio.sleep(10)


def start_bot_runner():
    global bot_runner_task

    if bot_runner_task is None or bot_runner_task.done():
        bot_runner_task = asyncio.create_task(bot_runner_loop())

    return bot_runner_task