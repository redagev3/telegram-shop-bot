import subprocess
import sys

# Запускаем оба бота одновременно
process1 = subprocess.Popen([sys.executable, "bot.py"])
process2 = subprocess.Popen([sys.executable, "admin_bot.py"])

# Ждём оба процесса
process1.wait()
process2.wait()
