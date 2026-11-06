# 11. Design QA, передача дизайна и поддержка системы

## Review по слоям
1. **Business:** каждый экран решает задачу роли, no ghost metrics/actions.
2. **Flow:** маршрут полон; есть выход, возврат, отмена, ошибка и разрешения.
3. **Visual:** иерархия, отступы, типографика, контраст, цифровые форматы.
4. **System:** Variables/modes/styles, component instances, naming, Auto Layout.
5. **Data:** формулы/единицы, источники, fresh vs stale, фильтры, нулевые и неизвестные.
6. **Responsive:** desktop/laptop/narrow, таблицы, drawers, длинный текст.
7. **Accessibility:** focus, state distinction, не только цвет, крупные значения.
8. **Handoff:** разработчик понимает каждое состояние, переход, граничный случай.

## Артефакт на экран
Заполни [screen spec](../assets/screen-spec.md):
- Цель, роли, вход и выход.
- Компоненты, данные и владение фильтрами.
- Порядок/приоритет блоков, layout/resizing и реакция на контент.
- Интерактивность, клавиатура, переходы.
- Empty/loading/error/permission/success.
- Перечень неизвестных решений и владельца уточнения.

## Handoff разработке
- Figma-ссылки на конкретные sections/frames/main components, статус версии, принятого design decision.
- UI tokens: имена, light/dark modes и примеры.
- Свойства компонентов и state matrix, responsive behavior.
- Типы данных: format, sort/filter rules, max length, date/timezones, currency.
- Scenarios: пользовательское действие → результат → feedback → exception.
- Не требуй от разработчика читать все страницы макета, укажи минимальный маршрут по handoff.

## Governance
- Есть владелец библиотеки и статус компонентов: Proposed / Beta / Stable / Deprecated.
- Новое имя/токен появляется только с обоснованием и демонстрацией применения.
- Breaking changes и замены документируются до публикации.
- Публикация Figma Library и обновление экземпляров контролируются, не выдаются за автоматическую синхронизацию с кодом.
- Анализ drift: разница между Figma и реализованным UI фиксируется и устраняется согласованным способом.
- По мере расширения продукта регулярно удаляй дубликаты и устаревшие overrides.

## Приёмка на типовой задаче
Для проверки самого скилла спроектируй «операционный список с фильтром + bulk action + детальная карточка + аналитический обзор», затем проведи review. Это проверяет и design system, и data-heavy UI.

Чек-лист: [review-checklist](../assets/review-checklist.md).
