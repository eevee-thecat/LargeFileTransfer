import hashlib

import aiofiles.os
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pathlib import Path
import time

SECONDS_IN_DAY = 86400
COUNTER = 0
SEED = int(time.time_ns() % 1e9)
HASHER = hashlib.new("blake2b")

app = FastAPI()


async def cleanup():
    """
    Clean up the files directory of files that have not been accessed in over a day.
    :return:
    """
    files = await aiofiles.os.listdir("files")
    for file in files:
        info = await aiofiles.os.stat(f"files/{file}")
        at = int(info.st_atime)
        now = int(time.time())
        delta = now - at

        if delta >= SECONDS_IN_DAY:
            # delete file
            await aiofiles.os.remove(f"files/{file}")


@app.post("/upload/")
async def upload_and_get_hash(file: UploadFile):
    """
    Receive an uploaded file and generate a hash for it.
    :param file:
    :return:
    """
    global COUNTER
    COUNTER += 1
    HASHER.update((COUNTER + SEED).to_bytes(64, "big"))
    digest = HASHER.hexdigest()
    async with aiofiles.open(f"files/{digest}", "w") as f:
        await f.write((await file.read()).decode("utf-8"))
    return f"http://localhost:8080/download/{digest}"


@app.get("/download/{digest}/")
async def download(digest: str):
    """
    Fetch a file based on its hash.
    :param digest:
    :return:
    """
    if not await aiofiles.os.path.isfile(f"files/{digest}"):
        raise HTTPException(status_code=404, detail="File not found")

    async with aiofiles.open(f"files/{digest}", "r") as f:
        return await f.read()


scheduler = AsyncIOScheduler()
# Every hour, clean up the files directory
scheduler.add_job(cleanup, "cron", minute="0")
scheduler.start()


if __name__ == "__main__":
    Path("files").mkdir(parents=True, exist_ok=True)
    uvicorn.run("main:app", port=8080)
