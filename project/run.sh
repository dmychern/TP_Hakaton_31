echo "Запуск приложения почты"

if [ ! -d "inbox" ]; then
  echo "Ошибка: Директория 'inbox' не найдена. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "data" ]; then
  echo "Ошибка: Директория 'data' не найдена. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "data/Important" ]; then
  echo "Ошибка: Директория 'Important' не найдена. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "data/Important/client_supprot" ]; then
  echo "Ошибка: Директория 'client_support' не найдена в директории 'Important'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "data/Important/tech_support" ]; then
  echo "Ошибка: Директория 'tech_support' не найдена в директории 'Important'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "data/Newsletter" ]; then
  echo "Ошибка: Директория 'Newsletter' не найдена в директории 'data'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "data/Service" ]; then
  echo "Ошибка: Директория 'Service' не найдена в директории 'data'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "data/Spam" ]; then
  echo "Ошибка: Директория 'Spam' не найдена в директории 'data'. Невозможно запустить приложение."
  exit 1
fi

mkdir -p data/logs
py -u src/__main__.py >> data/logs/run.log 2>&1
py src/__main__.py

echo "Приложение почты запущено успешно"
