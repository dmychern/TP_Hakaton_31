echo "Запуск приложения почты"

if [ ! -d "project" ]; then
  echo "Ошибка: Директория 'project' не найдена"
  exit 1
fi

if [ ! -d "project/inbox" ]; then
  echo "Ошибка: Директория 'ibox' не найден в директории 'project'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "project/data" ]; then
  echo "Ошибка: Директория 'data' не найден в директории 'project'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "project/data/Important" ]; then
  echo "Ошибка: Директория 'Important' не найден в директории 'data'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "project/data/Important/client_support" ]; then
  echo "Ошибка: Директория 'client_support' не найден в директории 'Important'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "project/data/Important/tech_support" ]; then
  echo "Ошибка: Директория 'tech_support' не найден в директории 'Important'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "project/data/Newsletter" ]; then
  echo "Ошибка: Директория 'Newsletter' не найден в директории 'data'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "project/data/Service" ]; then
  echo "Ошибка: Директория 'Service' не найден в директории 'data'. Невозможно запустить приложение."
  exit 1
fi

if [ ! -d "project/data/Spam" ]; then
  echo "Ошибка: Директория 'Spam' не найден в директории 'data'. Невозможно запустить приложение."
  exit 1
fi

mkdir -p project/data/logs

python src/__main__.py
echo "Приложение почты запущено успешно"
