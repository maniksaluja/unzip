import os
import asyncio
import zipfile
import rarfile
import py7zr
import mimetypes
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter

BOT_TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Send me a ZIP/RAR/7Z file. I’ll extract it and send all media back as videos 🎬")


@dp.message(lambda msg: msg.document)
async def handle_file(message: types.Message):
    doc = message.document
    file_name = doc.file_name
    file_path = os.path.join(DOWNLOAD_DIR, file_name)

    if doc.file_size > MAX_FILE_SIZE:
        await message.answer("❌ File too large! Max 2GB supported.")
        return

    await message.answer("📥 Downloading file...")
    file = await bot.get_file(doc.file_id)
    await bot.download_file(file.file_path, file_path)

    await message.answer("📂 Extracting...")

    extract_dir = os.path.join(DOWNLOAD_DIR, f"extracted_{message.from_user.id}")
    os.makedirs(extract_dir, exist_ok=True)

    try:
        if file_name.endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as z:
                z.extractall(extract_dir)
        elif file_name.endswith(".rar"):
            with rarfile.RarFile(file_path, "r") as r:
                r.extractall(extract_dir)
        elif file_name.endswith(".7z"):
            with py7zr.SevenZipFile(file_path, "r") as z:
                z.extractall(extract_dir)
        else:
            await message.answer("⚠️ Unsupported file type!")
            return
    except Exception as e:
        await message.answer(f"❌ Extraction failed: {e}")
        return

    await message.answer("📤 Sending extracted files as video...")

    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)

            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                await message.answer(f"⚠️ Skipping {file} (too large for Telegram)")
                continue

            mime, _ = mimetypes.guess_type(file_path)

            try:
                if mime and mime.startswith("video"):
                    await message.answer_video(FSInputFile(file_path))
                else:
                    # Agar video nahi hai → dummy conversion needed (future scope)
                    await message.answer(f"ℹ️ {file} is not video, skipping (convert required).")
            except TelegramRetryAfter as e:
                await message.answer(f"⏳ Flood wait {e.retry_after}s, pausing...")
                await asyncio.sleep(e.retry_after + 1)
            except Exception as e:
                await message.answer(f"⚠️ Could not send {file}: {e}")

            await asyncio.sleep(2)  # flood control

    await message.answer("✅ Done!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
