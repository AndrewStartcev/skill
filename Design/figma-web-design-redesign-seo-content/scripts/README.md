# Проверка SEO-контента и URL-map

**content_qa.py** — read-only валидатор CSV для проектирования и редизайна. Только Python 3.10+ и стандартная библиотека; не требует токенов, сети и доступа к Figma.

## Запуск
~~~bash
python Design/figma-web-design-redesign-seo-content/scripts/content_qa.py \
  --pages Design/figma-web-design-redesign-seo-content/assets/page-content-matrix.csv \
  --redirects Design/figma-web-design-redesign-seo-content/assets/redirect-map.csv

# Для CI: warnings тоже считаются ошибкой
python Design/figma-web-design-redesign-seo-content/scripts/content_qa.py \
  --pages path/to/page-content-matrix.csv \
  --redirects path/to/redirect-map.csv \
  --format json --strict

# Тесты
python -m unittest discover \
  -s Design/figma-web-design-redesign-seo-content/scripts \
  -p 'test_*.py' -v
~~~

## Что проверяет
- Корректность URL и обязательных полей контент-матрицы.
- Повторяющиеся URL, Title и H1; последние два — **предупреждение для редактора**, не доказательство SEO-проблемы.
- Отсутствие CTA на коммерческих типах страниц, описания, семантики и outline.
- Canonical на другой URL, отсутствие источника для статуса approved.
- Корректность keep/301/404/410, self-redirect, цепочки, циклы, редиректы внутренних URL на главную.
- Пустые reason/owner в карте редиректов.

**Не проверяет:** реальную индексацию, спрос, интент, фактическую релевантность 301, WCAG, Figma, доступность сайта, ранжирование, законность текстов. Проверка CSV не заменяет crawl, экспертную редактуру и ручное QA.

## Коды завершения
- 0 — ошибок нет (warnings допустимы без --strict).
- 1 — ошибки или warnings при --strict.
- 2 — ошибка чтения или структуры входного CSV.

Входные CSV не изменяются; результаты печатаются в stdout. Не загружай в репозиторий реальные клиентские материалы или персональные данные.
