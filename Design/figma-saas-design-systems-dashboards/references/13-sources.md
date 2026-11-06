# 13. Источники и обновление рекомендаций

**Срез:** 2026-11-06. При изменении функций Figma, тарифных ограничений и WCAG проверяй текущие официальные страницы. Здесь сохранены первоисточники и полезные открытые дизайн-системы; это не разрешение копировать чужие ассеты.

## Figma: официальная документация
1. [Variables, collections and modes](https://help.figma.com/hc/en-us/articles/14506821864087-Overview-of-variables-collections-and-modes) — типы variables, collections, alias, режимы и зависимость от плана.
2. [Guide to variables](https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma) — применение в макетах и прототипах.
3. [Modes for variables](https://help.figma.com/hc/en-us/articles/15343816063383-Modes-for-variables) — theme/context.
4. [Auto Layout](https://help.figma.com/hc/en-us/articles/360040451373-Guide-to-auto-layout-in-Figma) — layout и адаптивность.
5. [Component properties](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties) — варианты, properties и slots по актуальной доступности.
6. [Design tokens — Figma](https://www.figma.com/resource-library/design-tokens/) — модель токенов.
7. [Components, styles, shared libraries](https://www.figma.com/best-practices/components-styles-and-shared-libraries/) — единая библиотека.
8. [Design system examples](https://www.figma.com/resource-library/design-system-examples/) — разбор референсов.

## Дизайн-системы как методологические референсы
- [IBM Carbon](https://carbondesignsystem.com/) — B2B UI, таблицы, состояния, документация.
- [Atlassian Design System](https://atlassian.design/) — navigation, patterns, content и enterprise UI.
- [Material Design 3](https://m3.material.io/) — цвет, типографика, адаптивность и состояния.
- [Shopify Polaris](https://polaris.shopify.com/) — рабочие кабинеты и коммерческие операции.
- [Ant Design](https://ant.design/) — таблицы и rich CRUD-паттерны.
- [Microsoft Fluent 2](https://fluent2.microsoft.design/) — enterprise patterns и accessible UI.

**Важно:** Material Design (Google) и MUI (отдельная экосистема компонентных решений) — не один и тот же продукт. Не утверждай, что конкретная Figma-библиотека официальная, пока это не подтверждено её владельцем.

## Доступность
- [WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/) — нормативная основа.
- [Understanding: Focus Appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance) — критерий AAA, не путать с AA.
- [WAI tutorials](https://www.w3.org/WAI/tutorials/) — паттерны доступных взаимодействий.

## Как использовать источники
1. При создании нового дизайна выбери 1–2 референса под **конкретный** паттерн; объясни, какое поведение заимствуешь.
2. Проверяй актуальность возможностей Figma и лицензии Community assets до импорта.
3. Не копируй уникальную айдентику, защищённые тексты, иллюстрации и коммерческие компоненты без прав.
4. Ничего в Git само по себе не создаёт реальные Figma variables/components: это инструкции по их проектированию.
