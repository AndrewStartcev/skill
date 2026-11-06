# 05. Компонентная библиотека и паттерны

## Сначала inventory
Разделяй foundations, primitive controls, composite components, patterns и page templates. Предпочитай доработку существующего компонента создание нового с почти тем же поведением.

## Приоритет для SaaS
**P0:** Button, IconButton, Input, Select, Checkbox/Radio, Tabs, Badge/Status, Alert, Card/Panel, Modal/Drawer, NavigationItem, Tooltip, TableCell/Row, FilterChip, Skeleton, EmptyState.
**P1:** Search, DateRange, Pagination, BulkToolbar, CommandPalette (если нужна), Toast, Popover, Stepper, MetricCard, ChartContainer, Table, KanbanCard.
**P2:** продуктовые паттерны, построенные из базовых элементов.

## Свойства, варианты, Auto Layout
- Используй variants для действительно взаимоисключающих визуальных/поведенческих состояний: `state=default|hover|pressed|focus|disabled|loading`, `size=sm|md|lg`.
- Component properties: текстовые подписи, включение/скрытие иконки, замена вложенных instances. При доступности slots можно применять их для гибкого содержимого.
- Не делай все комбинации `color × size × icon × state × density`, если часть решается свойствами.
- Auto Layout, min/max, Hug/Fill, вложенность и доступные overrides должны сохранять работоспособность при длинном тексте.
- Component description: назначение, когда использовать, когда нельзя, состав, токены, interaction, a11y, ограничения и состояния.
- Управляй компонентами через main + instances; не правь detached copy на каждой странице.

## Контракт компонента: пример Button
| Поле | Спецификация |
| --- | --- |
| Задача | Запуск одного понятного действия |
| Hierarchy | primary на доминирующее действие, secondary для альтернатив |
| State | default, hover, focus, pressed, disabled, loading |
| Properties | `label`, `iconLeading`, `iconTrailing`, `size`, `variant` |
| Behaviour | Enter/Space, feedback, loading, защита от повторного отправления (описать разработке) |
| Content | Глагол + предмет: «Сохранить изменения» |
| A11y | Видимый focus, contrast, имя для icon-only |
| QA | Текст 2× длиннее, 320–375 px экран, Dark mode если предусмотрен |

## Компонентные документы
Для каждого P0/P1 заполни [assets/component-spec.md](../assets/component-spec.md). Тестируй компонент **в контексте экрана**, а не только на витрине.

**Антипаттерны:** компонент-«бог» на сотни вариантов; цвета зашиты в 40 инстансах; компоненты без focus/error; random detach; отключение системных свойств ради одного мокапа.

Figma components: https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties
