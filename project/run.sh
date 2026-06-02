echo "Запуск приложения почты"

if command -v py &> /dev/null; then
  PYTHON_CMD="py"
elif command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
fi

if [ ! -d "inbox" ]; then
  echo "Директория 'inbox' не найдена, папка добавлена автоматически"
  mkdir -p inbox
fi

if [ ! -d "data" ]; then
  echo "Директория 'data' не найдена, папка добавлена автоматически"
  mkdir -p data
fi

if [ ! -d "data/logs" ]; then
  mkdir -p data/logs
fi

if [ ! -d "data/Important" ]; then
  echo "Директория 'Important' не найдена, папка добавлена автоматически"
  mkdir -p data/Important
fi

if [ ! -d "data/Important/client_support" ]; then
  echo "Директория 'client_support' не найдена, папка добавлена автоматически"
  mkdir -p data/Important/client_support
fi

if [ ! -d "data/Important/tech_support" ]; then
  echo "Директория 'tech_support' не найдена, папка добавлена автоматически"
  mkdir -p data/Important/tech_support
fi

if [ ! -d "data/Newsletter" ]; then
  echo "Директория 'Newsletter' не найдена, папка добавлена автоматически"
  mkdir -p data/Newsletter
fi

if [ ! -d "data/Service" ]; then
  echo "Директория 'Service' не найдена, папка добавлена автоматически"
  mkdir -p data/Service
fi

if [ ! -d "data/Spam" ]; then
  echo "Директория 'Spam' не найдена, папка добавлена автоматически"
  mkdir -p data/Spam
fi

$PYTHON_CMD -m pytest tests/ -v || { echo "Приложение не прошло тестирование, запуск не возможен"; exit 1; }

$PYTHON_CMD -u -m src.__main__ --inbox inbox --out data --visualize 2>&1 | tee data/logs/run.log

echo "Приложение почты запущено успешно"
