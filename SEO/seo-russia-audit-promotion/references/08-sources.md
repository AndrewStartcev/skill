# Первоисточники, инструменты и проверка актуальности

Дата последней редакторской сверки: 2026-11-06. Ссылки и правила необходимо перепроверять при применении: интерфейсы, названия отчётов, алгоритмы и требования могут меняться.

## Официальные источники Яндекса
- [Индексирование сайта](https://yandex.ru/support/webmaster/ru/recommendations/indexing)
- [Как добавить сайт в поиск](https://yandex.ru/support/webmaster/ru/robot-workings/robot)
- [Как работает поиск Яндекса](https://yandex.ru/support/webmaster/ru/yandex-indexing/site-indexing)
- [Использование robots.txt](https://yandex.ru/support/webmaster/ru/controlling-robot/robots-txt)
- [Использование Sitemap](https://www.yandex.ru/support/webmaster/ru/controlling-robot/sitemap)
- [Канонический адрес страницы](https://yandex.ru/support/webmaster/ru/robot-workings/canonical)
- [Анализ индексации страницы](https://www.yandex.ru/support/webmaster/ru/site-indexing/page-indexing-analysis)
- [Региональность](https://yandex.ru/support/webmaster/ru/site-geography/site-region.html)
- [Качество сайта](https://www.yandex.ru/support/webmaster/ru/yandex-indexing/webmaster-advice)
- [Безопасность и нарушения](https://www.yandex.ru/support/webmaster/ru/service/security-threats)
- [Метрика: отчёты](https://yandex.ru/support/metrica/ru/reports/report-general.html)
- [Метрика: настройка счётчика](https://yandex.ru/support/metrica/ru/general/counter-general)

## Официальные источники Google
- [Search Essentials](https://developers.google.com/search/docs/essentials)
- [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [JavaScript SEO](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
- [Robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [Sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)
- [Canonicalization](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Structured data](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
- [Core Web Vitals](https://developers.google.com/search/docs/appearance/core-web-vitals)
- [Spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [Search Console](https://support.google.com/webmasters/)

## Спецификации
- [Robots Exclusion Protocol, RFC 9309](https://www.rfc-editor.org/rfc/rfc9309)
- [Sitemaps.org](https://www.sitemaps.org/protocol.html)
- [Schema.org](https://schema.org/)
- [HTML Living Standard](https://html.spec.whatwg.org/)

## Инструменты по задаче
- Индексация/поисковые запросы: Яндекс Вебмастер, Google Search Console.
- Спрос/сезонность: Wordstat, данные спроса, аналитика, собственный поиск.
- Поведение/конверсии: Яндекс Метрика, CRM, коллтрекинг.
- Обход: Screaming Frog, Sitebulb, собственный безопасный crawler, HTTP/логи.
- Скорость: PageSpeed Insights, Lighthouse, CrUX, WebPageTest.
- Разметка: Schema Markup Validator, Google Rich Results Test, инструменты Яндекс Вебмастера.
- Позиции/конкуренты: региональный мониторинг выдачи с зафиксированными настройками, а не обещание точного «среднего ТОП».

## Протокол работы с источниками
1. Приоритет: официальная документация и реальные данные проекта → независимые эксперименты → экспертные статьи/сообщества как гипотезы.
2. Для утверждений о правилах роботов, санкциях и поддержке разметки укажи точный URL документа, дату проверки и поисковик.
3. Отделяй документированные правила от распространённых практик. Не заявляй, что title «обязан иметь 60 символов», что `meta keywords` влияет на ранжирование или что валидная микроразметка гарантирует rich result.
4. При расхождении Google/Яндекс описывай две отдельные стратегии. При отсутствии подтверждения отмечай «не проверено».
5. Изменения поисковых алгоритмов и SERP требуют повторной проверки перед внедрением рискованных решений.
