> **21.11, итог:** часть 1 (глянец) отклонена слепым тестом ab-style-02: текущий стиль ближе всего к референсам. Часть 2 заменена принципом якоря (2111-anchor.md).

# Правки после слепого теста 21.11: глянец и «детали только у контейнеров»

Только текст. Код не менял, генерацию не запускал.

## 1. Откуда глянец и вид 3D-рендера

Нашёл 5 источников, от самого сильного к слабому.

| # | Где | Что тянет к рендеру |
|---|---|---|
| 1 | Стиль-блок `prompts.py` | Начинается со слов **«stylized 3D … warm animated-movie look»**. Для модели это прямой заказ на CG-рендер как в мультфильмах Pixar: блики, отражения, гладкий пластик. Плюс «gentle soft highlights», «satin» (= полублеск) и «glass» в списке материалов |
| 2 | Эталоны в `config.py` | 5 из 12 эталонов, которые идут в каждый запрос, глянцевые: пластиковая бутылка (кат.1), стакан мохито (кат.2), стеклянный кофейник (кат.3), пластиковые горки и мяч (кат.4). Модель переносит блеск эталона на любой объект |
| 3 | Чек-лист человека `rating-checklist.md` | Пункт 1 «Материал» прямо хвалит **«гладкий игрушечный пластик с мягкими бликами»**. Судья по задумке повторяет этот чек-лист |
| 4 | Судья `judge.py` | Наказывает «glossy plastic, chrome, neon», но нигде не требует «рисованная иллюстрация, а не 3D-рендер». Гладкий CG-рендер без хрома получает 2 из 2 за стиль |
| 5 | Шапка промпта | «style reference (**rendering**, materials, lighting…)» и в кат.3 «gentle light glow behind the object» |

Запрет «glossy plastic toy look» в негативе почти не работает: модели плохо слушаются отрицаний, а слово glossy в промпте само подталкивает к блеску.

### Правка 1.1: стиль-блок (`studio/prompts.py`)

```diff
-STYLE = ("stylized 3D casual mobile game collectible card art, warm animated-movie look, "
-         "soft rounded chunky shapes, slightly exaggerated proportions, no outlines, "
-         "every object keeps its real material (painted wood, brass, iron, leather, fabric, ceramic, glass, baked food) "
-         "with soft hand-painted texture and medium detail, matte or satin surfaces, "
-         "warm soft diffuse lighting like a sunny afternoon, gentle soft highlights, soft contact shadow, "
+STYLE = ("hand-painted casual mobile game collectible card illustration, digital painting with volume, "
+         "looks painted by an artist, not a 3D render, "
+         "soft rounded chunky shapes, slightly exaggerated proportions, no outlines, "
+         "every object keeps its real material (painted wood, brass, iron, leather, fabric, ceramic, baked food) "
+         "shown with painted brush shading, medium detail, matte surfaces, "
+         "broad soft light-to-shadow gradients, highlights only as a few soft pale painted strokes on rounded edges, "
+         "warm soft diffuse lighting like a sunny afternoon, soft contact shadow, "
          "the object is the most saturated element, background slightly softer, single object centered, ...")
 NEG = ("No text, ..., people, "
-       "glossy plastic toy look, wet shine, chrome or mirror reflections, neon glow.")
+       "3D render look, CGI, specular hotspots, reflections, wet shine, chrome, neon glow.")
```

```diff
-"Using the attached images ONLY as a style reference (rendering, materials, lighting, palette, ...)"
+"Using the attached images ONLY as a style reference (painting manner, materials, lighting, palette, ...)"
```
В кат.3 убрать «and a gentle light glow behind the object».

**Риск:** если перегнуть, уйдём в плоское 2D, а референсы объёмные. Поэтому формулировка «digital painting with volume», а не «flat 2D». Проверять только слепым A/B.

### Правка 1.2: эталоны (`studio/config.py`)

Меняю 4 глянцевых эталона на матовые из той же папки (все — арты Playrix):

| Кат. | Убрать | Поставить |
|---|---|---|
| 1 | `cat1_bottle` (пластик) | `cat1_fanfold` (веер, бумага и дерево) |
| 2 | `cat2_mojito` (стекло) | `cat2_lemontree` (дерево в горшке) |
| 3 | `cat3_coffeepot` (стекло) | `cat3_pie` (пирог) |
| 4 | `cat4_coaster` (пластик) | `cat4_antiquity` (колонна) |

Мяч `cat4_fieldball` пока оставляю, у него блик мягкий. Эталоны «с содержимым» (корзина, пляжная сумка) в общий набор не беру, иначе модель будет добавлять содержимое всем подряд.

### Правка 1.3: чек-лист и судья

`rating-checklist.md`, пункт 1:
```diff
-| 1 | **Материал** | Гладкий «игрушечный» пластик с мягкими бликами, а не фактура (волокна, зерно дерева, царапины, шум) |
+| 1 | **Материал** | Матовая рисованная поверхность: мягкая заливка с кистевой светотенью, блики — пара светлых мазков на рёбрах. Не 3D-рендер (зеркальные блики, отражения, «пластик»), и не фотофактура (волокна, зерно, царапины) |
```
`judge.py`, критерий style:
```diff
-real materials (...) rendered softly with warm light, no outlines, NOT glossy plastic toy, chrome or neon, ...
+matte hand-painted look like the references: soft painted shading, highlights only as a few pale strokes;
+score style 0-1 if it looks like a 3D/CGI render (specular hotspots, reflections, glossy smooth plastic, chrome, neon), ...
```

## 2. Принцип «детали только у контейнеров, 1–2 на набор»

Что ещё нашёл: у нас есть поле `theme_marker` («деталь, по которой видно тему»). Оно заставляет составителя добавлять каждой карточке значок или узор: отсюда молнии и звёзды на половине супергеройских карточек. Это и есть «детали появляются случайно».

### Где встраивается

| Шаг | Правка |
|---|---|
| Правила `rules.md` | Новый раздел: «Содержимое и следы использования есть только у предмета, который что-то несёт или хранит (сундук, чемодан, корзина, поднос, книга, бутылка с запиской). Таких 1–2 на набор. Остальные чистые и новые: без износа, наклеек, царапин, мелких украшений, без содержимого. Тему показывает форма предмета, а не значок на нём» |
| Поля карточки | Новое поле `contents`: пусто или 3–6 слов («gold coins and two gems»). `theme_marker` описывает только форму («round visor and side lights»), не добавленный значок |
| Отборщик | Квота: в каждом варианте 1–2 карточки с непустым `contents`, только у класса «хранит/несёт» |
| Проверка `validate()` | Ошибка, если `contents` у 0 или больше 2 карточек варианта |
| Промпт `prompts.py` | С содержимым: «…, open/visible, showing its contents: {contents}». Без содержимого: «clean and new, plain surfaces, no wear, no scratches, no stickers, no small decorations, nothing inside or on top» |
| Судья | Новый пункт в defects: на «чистой» карточке появились содержимое, износ или мелкие украшения → defects максимум 1 |

## 3. Пример: космоопера A, как изменится промпт

Показываю только изменившуюся часть. Стиль-блок у всех трёх заменяется на новый из правки 1.1.

**A5 Food Tray (кат.3) — контейнер, 1 из 1 в наборе A**
```diff
-a metal space food tray with compartments of colourful food placed on a white galley table ...
+a metal space food tray, showing its contents: colourful food in four compartments,
+placed on a white galley table ...
-Behind it ... a saturated yellow wall with plain wall with light glow and a gentle light glow behind the object
+Behind it ... a saturated yellow plain wall
```

**A1 Space Helmet (кат.1) — чистый предмет**
```diff
-a round white space helmet with an orange visor, floating in the air, ...
+a round white space helmet with an orange visor, clean and new, plain surfaces,
+no wear, no scratches, no stickers, no small decorations, floating in the air, ...
```

**A3 Pilot Seat (кат.2) — чистый предмет**
```diff
-a padded orange starship pilot seat with chunky armrests standing on ...
+a padded orange starship pilot seat with chunky armrests, clean and new, plain surfaces,
+no wear, no stickers, no small decorations, nothing on the seat, standing on ...
```
На старой картинке у кресла на подлокотнике была эмблема-планета: это как раз «случайная деталь», которая уйдёт.

## 4. Как проверить, когда скажешь «да»

Слепой A/B на 6 карточках (по 1–2 каждой категории, из разных жанров): старые промпты и эталоны против новых. Около 12 картинок, примерно $1. Смотрим ты и те же люди, что в тесте. Только если новая версия выигрывает, переносим в рабочий код.
