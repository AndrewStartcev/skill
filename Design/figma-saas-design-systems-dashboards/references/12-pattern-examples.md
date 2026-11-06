# 12. Типовые задания: примеры спецификаций для Figma

Во всех примерах названия и цифры вымышленные, не привязаны к реальным проектам.

## А. Операционная CRM/ERP
**Задача:** исполнитель видит просрочки, открывает заказ, обновляет ответственного.
- Desktop shell с nav и табличным списком, строка 44–52 px как отправная гипотеза (проверить density, a11y).
- Колонки: ID, объект, клиент, статус, срок, ответственный, приоритет, действие.
- Toolbar: Search, Status, Owner, Due Date, Save View; выбранные фильтры — chips.
- Row selection → bulk toolbar. Указать, что делать с записями без прав на edit.
- Детальная карточка: заголовок, status, primary action, tabs, история изменений.
- States: no items; no filter matches; loading; forbidden; conflict; saved.

**Компоненты:** `AppShell`, `NavItem`, `DataTable`, `FilterChip`, `StatusBadge`, `Avatar`, `Drawer`, `Toast`.

## Б. Аналитика выручки
**Задача:** руководитель быстро находит отклонение от ожиданий.
- Global range + organization filter.
- KPI: revenue, new customers, outstanding payment, variance.
- Line chart (time) с показанным периодом и единицей; category bars по источникам.
- Drilldown по нужной категории в таблицу первичных операций.
- Состояния: текущий неполный период, пропуск источника, отсутствие данных, ошибки, один сегмент.
- Спецификация точных определений KPI обязательна до построения графиков.

**Компоненты:** `MetricCard`, `DateRange`, `Chart/Line`, `Chart/Bar`, `Legend`, `Table`.

## В. Admin/workspace management
**Задача:** администратор приглашает сотрудника с подходящей ролью.
- Form: email, role, scope; доступные пояснения для каждой роли.
- Confirmation с уровнем доступа и чем поделятся.
- После отправки состояние `Invite pending`; ошибка неверного email и ограничения тарифа различаются.
- В таблице команды отдельный permission state для не-администратора.
- Важна явная связь: workspace → membership → permission.

## Г. Audit существующего Figma
Упорядочи замечания:
| Приоритет | Наблюдение | Риск | Действие | Критерий |
| --- | --- | --- | --- | --- |
| P0 | Удаление не имеет подтверждения | Ошибочная потеря данных | Запроектировать confirmation | Есть full flow |
| P1 | Badges различаются только цветом | Недоступность | Добавить текст статуса | Различимо без цвета |
| P1 | 8 копий одинаковой кнопки | Design drift | Main component + instances | 0 случайных detach |
| P2 | Разные радиусы карточек | Визуальная непоследовательность | Semantic radius | Использован один токен |

## Д. Сборка Figma-файла
1. Foundations: colors/typography/spacing.
2. Components: controls, status, navigation.
3. Patterns: table, filters, detail panel, charts.
4. Screens: list, detail, analytics, team settings.
5. Prototype Flows: основное действие, error, permission, undo.
6. QA: variants, overflow, user-roles, narrow widths.

Для начала заполни [brief](../assets/product-brief.md) и [screen spec](../assets/screen-spec.md).
