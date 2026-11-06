# Component spec — шаблон

## Component: [название]
- **Путь в библиотеке:** Components / ...
- **Статус:** Proposed / Beta / Stable / Deprecated
- **Задача:** ...
- **Когда применять:** ...
- **Когда не применять:** ...
- **Роли и разрешения:** ...
- **Состав:** icon, text, label, helper/error, container...
- **Tokens/styles:** ...
- **Auto Layout:** direction, gap, padding, Hug/Fill/Fixed, min/max
- **Responsive / Density:** ...
- **Content contract:** максимальная/минимальная длина, пустые значения, локализация

## Properties
| Property | Type | Values / default | Примечания |
| --- | --- | --- | --- |
| state | Variant | default/hover/focus/pressed/disabled/loading | Только применимые |
| size | Variant | sm/md/lg | Только нужные размеры |
| label | Text | Пример текста | Локализация |
| leadingIcon | Boolean/Instance | off/on | Не плодить копии |

## States
- Default:
- Hover:
- Keyboard focus:
- Pressed:
- Disabled + причина:
- Loading:
- Validation error:
- Success:

## Interactions
- Trigger:
- Expected action:
- Feedback:
- Error/recovery:
- Tab/focus order:
- Accessible name:
- Destructive confirmation, если нужно:

## QA
- Длинный текст:
- Узкий viewport:
- Light/Dark:
- Повторное использование instances:
- Известные исключения:
- Ссылка на Figma main component:
