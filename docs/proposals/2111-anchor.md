# Деталь = якорь темы (заменяет правило «детали только у контейнеров»)

Только текст. Код не менял, генерацию не запускал.

## Принцип

Составитель для каждого объекта отвечает на один вопрос: **«Узнает ли игрок тему набора по этому предмету без подписи?»**
- Да → `anchor: null`. Предмет чистый, без лишних деталей.
- Нет → `anchor: "одна конкретная деталь"`, которая привязывает предмет к теме. Деталь может быть на предмете (наклейки на чемодане), внутри (монеты в сундуке) или рядом (пустыня за колонкой).

Если якорей в варианте больше 4, это мягкое предупреждение: в наборе много нейтральных предметов, лучше заменить часть на однозначно тематические.

Почему так: раньше признак темы ставили на всё (подкова на 7 карточках, молнии у супергероев). Потом убрали, и нейтральные кружка, колба и часы выпали из жанра. Якорь решает обе проблемы.

## Diff

**`studio/rules.md`**, раздел про `theme_marker` заменить:
```diff
-- Every card has a field theme_marker: the concrete visual detail that makes it read as the theme.
-  "Western style" is not a marker; "spurs and a pointed toe" is.
+- Anchor. For every object answer one question: would a player recognise the set's theme from this
+  object alone, without a caption?
+  - Yes -> "anchor": null. The object stays clean: no emblems, stickers, wear or extra decorations.
+  - No -> "anchor": ONE concrete detail that ties it to the theme: on the object (a suitcase covered
+    with city stickers), inside it (a chest with gold coins) or right next to it (a fuel pump with a desert behind).
+  - Never add an anchor to an object that is already clearly on theme.
+  - More than 4 anchors in a variant = too many neutral objects; replace some with clearly themed ones.
```

**Схема JSON (`compose.py: SCHEMA_HINT`, примеры в `studio/examples/`)**
```diff
-"theme_marker": "spurs and a pointed toe",
+"anchor": null,                        // or "a cowboy hat resting on top"
```

**Проверка (`compose.py: validate`)**: предупреждение, не ошибка
```diff
+n = sum(1 for c in v["cards"] if c.get("anchor"))
+if n > 4: warnings.append(f"{v['id']}: {n} anchors - too many neutral objects?")
```

**Промпт (`prompts.py: build`)**: чистая механика, промптёр не думает
```diff
-create a new card illustration of {scene(c)}
+obj = c["object"] + (f", with {c['anchor']}" if c.get("anchor")
+                     else ", a clean object with no extra details, no emblems, no stickers, no wear")
+create a new card illustration of {scene(c, obj)}
```

**Слепой судья (`blindcheck.py`)**: угадывает ещё и тему
```diff
 1. What is this object? Answer in 1-3 words.
+2. This card belongs to a themed collection set. Guess the theme of the set from this one picture
+   (1-3 words, e.g. "Wild West", "beach vacation", "space").
```
Потом код сравнивает догадку с жанром набора одним текстовым вызовом. Не угадал тему → пометка `theme_not_recognized` в report.md: якоря не хватило или он не прочитался. Это мягкий сигнал, карточку не валит.

## Пример: космоопера A

| # | Карточка | Узнаётся без подписи? | anchor |
|---|---|---|---|
| 1 | Space Helmet | да | null |
| 2 | Star Map | да (голограмма звёзд) | null |
| 3 | Pilot Seat | нет, просто кресло | "a small control panel with round buttons on each armrest" |
| 4 | Ray Gun | да | null |
| 5 | Food Tray | нет, столовая | "a round porthole with stars behind the tray" |
| 6 | Communicator | нет, рация | "a tiny ringed planet on its screen" |
| 7 | Retro Robot | да | null |
| 8 | Space Station | да | null |
| 9 | Alien Plant | нет, комнатный цветок | "a round porthole with stars behind the pot" |
| 10 | ★ Starship | да | null |

Якорей 4, на границе. Для варианта лучше заменить Communicator на однозначный предмет (например, Jetpack), тогда якорей 3.

## Пример: вестерн A

| # | Карточка | Узнаётся без подписи? | anchor |
|---|---|---|---|
| 1 | Cowboy Hat | да | null |
| 2 | Banjo | нет, просто инструмент | "resting on a hay bale" |
| 3 | Saddle | да | null |
| 4 | Sheriff Star | да | null |
| 5 | Apple Pie | нет, просто пирог | "cooling on a wooden saloon window sill" |
| 6 | Revolver | да (кобура) | null |
| 7 | Saloon Piano | нет, просто пианино | "a cowboy hat resting on top" |
| 8 | Stagecoach | да | null |
| 9 | Saguaro | да | null |
| 10 | ★ Saloon | да | null |

Якорей 3.

Открытый вопрос: фоновый узор темы (подковы на фоне) — это тоже якорь? Я бы считал его якорем и давал только нейтральным предметам. Тогда у Sheriff Star подков на фоне не будет.

## Как проверить

Без денег: я прогоняю составителя (себя) на 4 утверждённых жанрах и показываю таблицы якорей. Дальше по твоему «да» генерация одного жанра, около $8.
