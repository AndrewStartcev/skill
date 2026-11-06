# 04. Figma Variables, modes и архитектура токенов

## Слои токенов
1. **Primitive** — базовое значение, например `primitives/color/blue/600` или `primitives/space/4`.
2. **Semantic** — роль в интерфейсе, например `semantic/text/primary`, `semantic/surface/default`, `semantic/border/subtle`, `semantic/status/danger`.
3. **Component** — контракт конкретного элемента, например `component/button/primary/bg`, с alias на семантику. Не обязательно выделять отдельный токен для каждой мелочи, если достаточно семантического.

Схема зависимости: `Button background → semantic/action/primary → primitives/blue/600`. При тёмной теме может измениться alias, но не смысловая роль.

## Коллекции и режимы
Предложение для Figma:
- `Primitives / Colors` — цвета, независимые от темы.
- `Semantic / Color` — modes `Light` и `Dark` только когда действительно нужно; alias на primitives.
- `Spacing and Sizing` — number variables для 4px-шкалы и размеров.
- `Context` — mode Compact / Comfortable, только если продукт поддерживает плотности.
- Text styles для комбинированных типографических решений (семейство, размеры, интерлиньяж, начертание); возможности variables для текстовых атрибутов сверяй с актуальной Figma.

Режимы не бесплатны: не создавай «brand × theme × density × device» как декартово произведение ради видимости зрелости системы. Избегай циклических alias.

## Семантическая схема цветов
`text/primary`, `text/secondary`, `text/inverse`, `surface/canvas`, `surface/raised`, `surface/overlay`, `border/default`, `border/focus`, `action/primary`, `status/success`, `status/warning`, `status/danger`, `chart/series/01..n`.

Цвет для статуса дополняй текстом, иконкой или формой. Цвет серии на графике должен быть различим, а не только красив. Проверяй контраст в каждом mode.

## Типографика, elevation и иконки
- Типографика: `Display` (если действительно нужна), `Heading/L`, `Heading/M`, `Body/M`, `Body/S`, `Label`, `Caption`; таблицы и формы должны быть читаемы.
- Radius: `none / sm / md / lg`. Elevation — отдельные эффекты/стили, не произвольные тени на каждом слое.
- Иконки: согласованная система stroke/fill/optical-size; одинаковая семантика и hit area.

## Процесс создания
Audit values → выделение повторов → primitives → semantic naming → aliases → applied styles → modes → проверка реальными компонентами → документация. Не публикуй токены до проверки на кнопке, карточке, таблице и экране с ошибкой.

## Проверка
Меняешь primitive — изменения наследуются предсказуемо; меняешь mode — смысловые цвета и контрасты сохраняются; не остаются случайные hex на критических слоях. Пример **документационного** JSON в [assets/tokens-example.json](../assets/tokens-example.json); это **не** автоматический экспорт или импорт Figma.

Официально:
- https://help.figma.com/hc/en-us/articles/14506821864087-Overview-of-variables-collections-and-modes
- https://help.figma.com/hc/en-us/articles/15343816063383-Modes-for-variables
- https://www.figma.com/resource-library/design-tokens/
