# Структура Figma-файла — шаблон

```text
00 Cover
   About / Version / Design decisions
01 Foundations
   Color primitives and semantic roles
   Type styles / spacing / radius / elevation / icons
   Variables collections / modes / naming
02 Components
   Actions / Forms / Navigation / Feedback
   Tables / Data display / Overlays
   State galleries and documentation
03 Patterns
   App shell / Filter toolbar / Data table
   Entity detail / Dashboard widgets / Modals
04 Screens — desktop
   Overview / List / Detail / Settings
05 Screens — responsive
   Laptop / Narrow / Mobile (where needed)
06 Prototype flows
   First-run / Main job / Error recovery
99 Archive
   Deprecated / Experiments
```

## Правила
- Прежде чем копировать компонент, проверь библиотеку и статус версии.
- Main components храни отдельно от экранных инстансов.
- Используй Sections и однозначные имена экранов.
- В Foundations записывай назначение каждого семантического цвета.
- В Patterns размещай композиции, которые реально повторяются в Screens.
- На каждой критической странице покажи состояния и требования к responsive.
- В Archive только устаревшее; рабочие компоненты оттуда не инстанцировать.
- Figma Design Library публикуй только при доступности и достаточных правах.
