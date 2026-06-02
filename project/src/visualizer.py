import json
import logging
from pathlib import Path
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def generate_dashboard(report_path: Path, output_path: Path):
    try:
        if not report_path.exists():
            logger.error(f"Отчет не найден: {report_path}")
            return

        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        dist = report.get("distribution", {})
        if not dist:
            logger.warning("Нет данных для визуализации")
            return

        # Подготовка данных
        labels = list(dist.keys())
        sizes = list(dist.values())
        
        # Создание графиков
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        fig.suptitle('Аналитика обработки почты', fontsize=16)

        # 1. Круговая диаграмма
        colors = plt.cm.Paired(range(len(labels)))
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
        ax1.set_title('Распределение по категориям')

        # 2. Столбчатая диаграмма
        bars = ax2.bar(labels, sizes, color=colors)
        ax2.set_title('Количество писем')
        ax2.set_ylabel('Количество')
        plt.xticks(rotation=45, ha='right')
        
        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        
        logger.info(f"Дашборд успешно сохранен: {output_path}")
        print(f"Дашборд создан: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка при генерации дашборда: {e}")
