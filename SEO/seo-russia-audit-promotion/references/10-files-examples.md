# Примеры SEO-файлов и HTML (только шаблоны)

Это **иллюстрации**, не готовые настройки для любого сайта. Адаптируй под реальную структуру, индексируемые страницы и поисковые системы. Никогда не закрывай служебные данные одним лишь robots.txt — это не контроль доступа.

## robots.txt
```text
User-agent: *
Disallow: /private-area/
Allow: /
Sitemap: https://example.com/sitemap.xml
```

Здесь `/private-area/` — условный путь; он **не защищает** содержимое. Для приватного контента используй авторизацию. Перед публикацией протестируй разрешения на главной, категории, карточке, статье и CSS/JS; отдельно проверь Яндекс и Google. Не добавляй `Disallow: /` на production.

## sitemap.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-11-01</lastmod>
  </url>
  <url>
    <loc>https://example.com/services/</loc>
    <lastmod>2026-11-01</lastmod>
  </url>
</urlset>
```

`lastmod` отражает фактическое существенное обновление; не проставляй сегодняшнюю дату без изменений. Не включай неканонические, `noindex`, удалённые или редиректящие URL.

## HTML head индексируемой страницы
```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Услуги компании — Пример</title>
  <meta name="description" content="Описание услуг, условий и преимуществ компании.">
  <link rel="canonical" href="https://example.com/services/">
</head>
<body>
  <main>
    <h1>Услуги компании</h1>
    <a href="/services/example/">Подробнее об услуге</a>
  </main>
</body>
</html>
```

Не добавляй `meta robots="index,follow"` без необходимости: индексирование по умолчанию не требует явного разрешения. `canonical` для страницы — подсказка, а не гарантия.

## noindex для публичной, но не предназначенной к поиску страницы
```html
<meta name="robots" content="noindex,follow">
```

Страница должна оставаться доступной роботу, иначе он может не увидеть `noindex`. Для PDF или других не-HTML ресурсов используй HTTP-заголовок `X-Robots-Tag`, если это поддерживается целевой поисковой системой.

## JSON-LD: хлебные крошки
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Главная",
      "item": "https://example.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Услуги",
      "item": "https://example.com/services/"
    }
  ]
}
</script>
```

Проверяй синтаксис, реальное соответствие видимым хлебным крошкам и поддержку нужным поисковиком. Не добавляй вымышленные рейтинги, цены и отзывы.

## 301-переезд
Для старой страницы `https://example.com/old-service/`, которой соответствует `https://example.com/services/example/`, нужен **один постоянный** редирект на конечный адрес. Правило зависит от веб-сервера и уже существующих правил. После изменения проверь статус, `Location`, отсутствие цепочек и новый self-canonical. Не редиректь все удалённые URL на главную.

## Карта SEO-файлов
| Файл / источник | Для чего | Что проверять |
| --- | --- | --- |
| `robots.txt` | Правила обхода | Группы роботов, Disallow/Allow, Sitemap |
| `sitemap.xml` | Обнаружение URL | 200, валидность, canonical, lastmod |
| `.htaccess` / Nginx | Редиректы, ответы, заголовки | 301/308, 404/410, HTTPS, X-Robots |
| HTML `head` | Представление URL | title, description, canonical, robots, hreflang |
| JSON-LD | Описание сущностей | Поддержка и фактическое соответствие |
| Фиды товаров | Внешние сервисы | Актуальность цены/наличия, требования сервиса |
| Логи HTTP | Обход и ошибки | Боты, коды, скорость, шаблоны, приватность |
| Экспорты Вебмастера/Метрики | Фактическая динамика | Даты, сегменты, фильтры, права доступа |
