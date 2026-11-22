# 03. Как индустрия делает консистентные AI-ассеты: пайплайны и приёмы (21.11.2026)

Desk research: только веб-поиск и чтение страниц. Платные API не вызывались, картинки не генерировались.
Опирается на `/mnt/project-files/research/stable-generation-practices.md` (20.11, 7 советов). Здесь они проверены, углублены и дополнены.

Маркировка: **[V]** — проверено, прочитано в первоисточнике в этом исследовании. **[V-вендор]** — написано в первоисточнике, но это маркетинг вендора, цифры никто не проверял. **[I]** — вывод или гипотеза автора, в источниках прямо не сказано.

---

## TL;DR

1. **Без дообучения стабильности в индустрии почти никто не добивается.** Rovio, InnoGames, Playkot и сами вакансии Playrix опираются на fine-tune/LoRA на своём арте и на ручную доводку в Photoshop [V]. Вариант «без LoRA» держится на трёх вещах: **референс-картинки во входе** (style reference / reskin), **жёсткий шаблон** и **отбор с исправлением**. Цель — «пусть годные кандидаты будут, и их можно дёшево отобрать», а не «каждая генерация годная» [I].
2. **Главный рычаг против «глянцевого пластика» — edit от эталонной карточки вместо text-to-image.** Эталонная карточка в стиле Playrix идёт входом №1 с ролью «стиль, свет, фактура, ракурс», и меняется только объект. Это прямо рекомендуют OpenAI (Image 1/2 с ролями, «change only X», «preserve…»), Google/Scenario для Gemini (стиль-референсы картинками, порядок важен) и Scenario reskin [V]. Текстовое описание стиля сползает к дефолтной эстетике модели, а это и есть «3D-пластик» [I].
3. **Против гибридных объектов нужны разделение ролей и проверка «вслепую».** Объект описывать родовым каноническим именем. Опционально давать фото/иконку реального объекта отдельным входом с ролью «только форма». После генерации VLM вслепую называет объект, и название сверяется с заказом [I, частично V: роли входов есть у OpenAI/Google].
4. **Судья должен быть попарным и относительным, а не баллы 0–10.** GenArena показала, что попарное сравнение лучше согласуется с людьми [V, из прошлого отчёта]. Сырые эмбеддинги стиля (CSD/CLIP/DINO) как абсолютная метрика ненадёжны: на 23 из 91 художника они не отличают «своё» от «чужого» [V, arXiv 2605.09030]. Эмбеддинги годятся как дешёвый пред-фильтр и для ранжирования относительно своих эталонов, не как вердикт.
5. **Approval gates у всех ручные.** Rovio: «pretty good is not good enough», художник на каждом этапе [V]. Для тестового нужен автоматический прогон, но с двумя точками, где человек тратит по минуте: утвердить «якорь сета» и выбрать финальный вариант [I].

---

## 1. Что известно о Playrix и конкурентах

### Playrix [V, по вакансиям]
- **AI Producer (Art Development)** — та самая роль. Отвечает за стратегию внедрения AI в арт-процессы и оптимизацию пайплайнов для команды из 400+ художников. Обязанности: настраивать Stable Diffusion, черновики и референсы в Midjourney, доводить картинки до продакшен-качества (изометрия, **иконки**, иллюстрации, персонажи, фоны), **собирать датасеты для LoRA под стиль проекта**, визуализировать процессы. Инструменты: Photoshop, Midjourney, SD, Blender. ([outscal](https://outscal.com/job/ai-producer-art-development-at-playrix-in-cyprus-1))
  - Вывод [I]: внутри Playrix стиль держат через LoRA. Свои LoRA Playrix для тестового не даёт, значит проверяют, умеет ли кандидат добиться стабильности **процессом**: референсы, шаблоны, отбор, гейты. Это стоит сказать в защите прямо.
- **AI Artist:** генерирует 2D (фоны, персонажи, **Match-3 элементы**, UI) в основном на **FLUX**, строит воркфлоу в **ComfyUI/Forge**, ретуширует в Photoshop. LoRA/DreamBooth в разделе nice-to-have. ([hitmarker](https://hitmarker.net/jobs/playrix-ai-artist-1520915))
- **Creatives AI Artist (2D/3D):** FLUX, **ChatGPT, Google AI Studio**, SD, ComfyUI, Blender для поз и света, Photoshop. Нужен опыт casual-стиля. Для 3D — Rodin, Hunyuan 3D. ([hitmarker](https://hitmarker.net/jobs/playrix-creatives-ai-artist-2d-3d-1588125))
  - Вывод [I]: GPT Image и Gemini через AI Studio для Playrix «свои» инструменты, особенно в креативах. Наш стек выглядит естественно.
- Подкаст *2.5 Gamers* (11.06.2026): Playrix «пошли all-in на AI-креативы» в своих флагманах, разобрано 100 AI-объявлений. ([brapodd](https://brapodd.se/podd/two-a-half-gamers/avsnitt/playrix-just-went-all-in-on-ai-creatives-100-ai-ads-reviewed)) [V — описание эпизода, сам эпизод не слушали]
- Публичных докладов Playrix о стабильности иконок или карточек **не нашёл**.

### Rovio [V]
- GDC 2026: «Angry Birds Meets GenAI», кейс Dream Blast на SageMaker и Bedrock. Цель — «сохранить art direction и brand consistency». Методы на странице сессии не раскрыты. ([GDC](https://schedule.gdconf.com/session/angry-birds-meets-genai-transforming-rovios-asset-creation-with-aws-presented-by-amazon-web-services/917278))
- Разбор от ZenML (по материалам AWS/Rovio):
  - fine-tune диффузии на своём арте, отдельный trigger word на модель;
  - **20–30 тщательно отобранных картинок** в датасете;
  - художники собирают и подписывают датасет и **выбирают чекпойнт** (поздние переобучаются);
  - лучше всего работает на фонах, хуже на главных брендовых персонажах;
  - три интерфейса: Slackbot, Pro Studio, Studio на Bedrock с Claude в роли prompt-assistant;
  - фоны season pass: **20 → 4 дня**;
  - позиция: «pretty good is not good enough». ([ZenML](https://www.zenml.io/llmops-database/accelerating-game-asset-creation-with-fine-tuned-diffusion-models))
  - Для нас [I]: LLM как помощник по промптам поверх жёсткого стиль-механизма — тот же паттерн, что у нас. У Rovio стиль держит модель, у нас его должны держать референсы и шаблон.

### King [V]
- По открытым данным AI используется в **дизайне уровней** Candy Crush: черновики новых и переработка старых. Про арт ничего публичного нет. ([Fortune/AP, 12.05.2025](https://fortune.com/article/candy-crush-gaming-ai-technology-art-jobs-puzzles/))

### Supercell, Zynga, Moon Active
- Конкретики об арт-пайплайнах с AI в открытых источниках **не нашёл**.

### Ubisoft [V]
- AI-плейсхолдер «проскочил» в релиз Anno 117. ([PC Gamer](https://www.pcgamer.com/games/city-builder/ubisoft-touches-up-ai-art-placeholder-that-slipped-into-anno-117-but-fans-are-not-happy-it-was-there-to-begin-with-of-all-the-video-games-not-anno))
- Мораль для пайплайна [I]: финальный human gate и метка статуса ассета (draft / approved) обязательны.

### Tencent / NetEase
- Tencent VISVISE: «дни → минуты», заявление компании. [V-вендор] ([gamedeveloper index](https://www.gamedeveloper.com/art/ai-game-art-pipelines))
- NetEase, GDC 2026, «LifeAfter: AIGC Paradigm Change in Mobile Game Art Production»: AI-тулчейны, human-AI воркфлоу, **фреймворки оценки AI-инициатив**, заявлено $6M экономии и +50% эффективности. ([GDC](https://schedule.gdconf.com/session/lifeafter-aigc-paradigm-change-in-mobile-game-art-production/915039)) [V — аннотация]

### Другие студии [V]
- **InnoGames + Scenario:** кастомные модели на своём арте (портреты Elvenar). Для **иконок Sunrise Village** — reference-режимы и платформенные модели против оригинальных визуалов. AI canvas для точечных правок. До −50% времени. ([InnoGames blog](https://blog.innogames.com/innogames-x-scenario-streamlining-our-game-production/))
- **Playkot (pocketgamer.biz):**
  - модели на своём арте;
  - ControlNet для замены мелких деталей («ворона → чайка») и для поз по 3D-сцене;
  - **40 иконок за 40 минут → фильтр → 5 концептов на A/B**;
  - перспективные концепты перерисовывают больше чем наполовину;
  - экономия 30–50%. ([pocketgamer.biz](https://www.pocketgamer.biz/ai-everywhere-using-neural-networks-for-asset-creation-marketing-and-more))
  - Для нас [I]: «много дешёвых кандидатов → жёсткий фильтр → мало финалистов» — индустриальная норма.
- **Mighty Bear:** модель на своём арте, финал за людьми, «the human mind and hands are still king». ([Medium](https://medium.com/mighty-bear-games/how-the-use-of-ai-evolved-our-art-production-pipelines-a335c8a257ce))
- **Cosmic Lounge (Puzzle Engine):** дизайнер выбирает use case (game cells), стиль (cute), описывает объект и **выбирает из вариантов**. Методов консистентности не раскрыли. ([Business Finland PDF](https://www.aka.fi/contentassets/9154663e9d6e48c99af0735226db0c74/11.-cosmic-lounge_-tooling-for-game-art-generation-with-ai---business-finland-rrf.pdf)) Это ближайший аналог нашего UX.

### Вендоры [V-вендор]
- **Layer.ai IP-consistency guide** ранжирует подходы так:
  - prompt engineering — «Unreliable at scale»;
  - LoRA — «improves style anchoring, but does not solve workflow governance»;
  - best practice — шаблоны, библиотеки, **controlled generation parameters**, цепочки пайплайнов, версии и аудит. ([Layer](https://layer.ai/blog/ip-consistency-ai-generation-guide-game-studios))
- **Scenario reskin:**
  - одна модель на весь батч;
  - одинаковые influence-настройки на серию;
  - явные «keep»-клаузы для дрейфующих деталей;
  - ControlNet Structure + Style Reference для перевода целого сета в новую тему. ([Scenario blog](https://www.scenario.com/blog/reskin-game-assets-ai-isometric-art))
- **Scenario о Gemini:**
  - лимит референсов: 6 у 2.5 Flash Image, **14 у Gemini 3 Pro Image / 3.1**;
  - «include images of the target look instead of describing it»;
  - ссылаться на картинки по позиции, «keep everything else the same»;
  - выход шага подавать как референс следующего;
  - итерировать на дешёвой модели, финал прогонять на сильной. ([Scenario help](https://help.scenario.com/articles/7568607761-gemini-image-models-nano-banana-family))

---

## 2. Каталог техник

Колонки: что это; почему помогает; стоимость (время/деньги/сложность); применимость к нашему стеку (LLM → промпты → GPT Image / Gemini → судья, без LoRA).

| # | Техника | Почему помогает | Стоимость | Применимость к нам | Статус |
|---|---|---|---|---|---|
| T1 | **Reskin эталона (edit-from-template):** реальная карточка в нужном стиле идёт входом №1, «замени только объект на X» | Модель копирует свет, фактуру, ракурс и масштаб из пикселей, а не из текста. Главное средство против пластика | Низкая: тот же вызов edit вместо generate | **Высокая. Делать первым.** OpenAI: «Image 1: … Image 2: …», «change only X», «Preserve the exact layout, proportions, and perspective». Первый вход сохраняется точнее всего при `input_fidelity=high` | [V] OpenAI guide + cookbook, Scenario |
| T2 | **Фиксированный reference board в каждом вызове:** 2–4 эталона стиля плюс один шаблон композиции | Стиль задаётся одним и тем же набором пикселей → меньше дисперсия между вызовами | Растут input-токены. В GPT Image богато детализируется только 1-й вход, остальные — «references» | Высокая. В Gemini 3 Pro до 14 входов. Порядок и роли фиксированы в шаблоне | [V] OpenAI, Scenario/Gemini |
| T3 | **Склейка эталонов в один коллаж** | OpenAI для нескольких лиц советует объединять их в один composite, чтобы всё было в «первом» изображении | Ноль | Средняя: сетка 2×2 эталонных карточек как вход №1. Риск: модель повторит сетку. Нужен тест | [V] совет для лиц; для стиля [I] |
| T4 | **Якорь сета:** первую одобренную карточку подавать входом остальным 9 | Сет держится вместе, а не только «похож на Playrix» | +1 гейт (человек или судья) | Высокая. Гейт №1 в пайплайне | [V] Scenario/Gemini «use each output as the reference», OpenAI «character anchor»; прошлый отчёт |
| T5 | **Замороженный шаблон промпта:** стиль-блок дословный, меняется только слот объекта; одна модель и параметры на батч | Убирает дисперсию от LLM-переформулировок | Ноль | **Высокая. Обязательно.** LLM пишет только слот объекта и keep-лист, стиль не пишет | [V] Scenario, Layer, OpenAI «repeat the preserve list» |
| T6 | **Низкая «креативность»:** `complexity=low` для точечных правок; `quality` фиксирован; в Gemini — фиксированный thinking level | Меньше переосмысления и дрейфа композиции | Ноль | Высокая. По текущему гайду OpenAI `complexity` по умолчанию `high`, для targeted edits советуют `low` | [V] OpenAI image-prompting guide |
| T7 | **Seed** | Повторяемость | — | **Низкая.** GPT Image seed не принимает. Повторяемость даёт только T1/T5 | [I]; seed в ref-доке OpenAI не найден |
| T8 | **Фиксированная композиция → замена объекта:** шаблон карточки (рамка, фон, тень, размер в кадре) + edit/inpaint объекта | Фон, рамка и масштаб идентичны по построению | Низкая | Высокая. Фон и рамку лучше вообще **собирать кодом**, а генерировать только объект на прозрачном фоне (T9) | [V] Scenario reskin, Playkot ControlNet; сборка кодом [I] |
| T9 | **Объект отдельно + прозрачный фон + сборка карточки кодом** | Модель отвечает только за объект. Фон, рамка, тень и подпись детерминированы | Низкая. `background="transparent"` в GPT Image (PNG/WebP, проверять alpha: «a drawn checkerboard is not transparency») | **Высокая.** Убирает половину дрейфа. Резерв — BiRefNet/rembg; на стилизованном арте BiRefNet даёт 95% pixel acc, fine-tune ToonOut — 99.5% | [V] OpenAI guide, arXiv 2509.06839 |
| T10 | **Палитра: lock + постобработка** — эталонная палитра 8–16 цветов; в промпте/референсе; после генерации мягкий color transfer (LAB) к палитре эталона | Снимает разброс по насыщенности и «неоновость», частично убирает глянец | Низкая (numpy/PIL), бесплатно | Средняя. Для casual лучше мягкий перенос гистограммы/LAB-статистики, а не жёсткая квантизация (она для пиксель-арта) | [V] playgama (для пиксель-арта); мягкий вариант [I] |
| T11 | **Ограничение блика и спекуляра:** негатив-лист в keep-клаузах («matte painted surfaces, soft diffuse light, no glossy highlights, no plastic/vinyl toy look, no 3D render»), плюс эталон с матовой фактурой входом №1 | Пластик — дефолт модели для слова «cute 3D». Текст помогает слабо, пиксели эталона — сильно | Ноль | Высокая, но только **вместе с T1**. Отдельно ненадёжно | [I]; жалобы на «plastic look» на форуме OpenAI [V] |
| T12 | **Канонический объект + проверка вслепую** (против гибридов): LLM-композитор выдаёт родовое имя и 3–5 визуальных признаков, без смешения двух объектов в одном слоте. После генерации VLM без подсказки отвечает «что это?», ответ сверяется с заказом | Гибрид появляется, когда в промпте смешаны два концепта или модель «дофантазировала». Слепое называние ловит это дёшево | 1 дешёвый VLM-вызов на картинку | **Высокая.** Опционально фото реального предмета входом с ролью «только форма/силуэт, стиль не брать» | [I]; роли входов [V] |
| T13 | **Чинить, а не перегенерировать:** судья называет дефект и область → edit «измени только это», `complexity=low` | Сохраняет удачное, сходится быстрее | 1 edit-вызов | Высокая | [V] OpenAI «Refine one thing at a time»; Scenario/InnoGames canvas |
| T14 | **Over-generate → filter:** N кандидатов на слот, отбор | Индустриальная норма (Playkot 40 → 5) | ×N генераций | Высокая. N=2–3 на слот укладывается в бюджет | [V] Playkot, Cosmic Lounge |
| T15 | **Эмбеддинг-предфильтр** (CSD / DINOv2 / CLIP), расстояние до эталонов | Дешёвый автоматический отсев явных выбросов по стилю | Бесплатно локально (CPU ок) | Средняя. **Только относительно:** ранжировать кандидатов слота между собой и отсекать хвост. Не порог «≥0.8 = стиль ок». Сырой косинус CSD не калиброван, CSLS улучшает | [V] arXiv 2404.01292, 2605.09030 |
| T16 | **VLM-judge, попарный:** кандидат A vs B против эталона, оба порядка, без «ничьей»; плюс чек-лист бинарных вопросов (матовость? один объект? читаем на 128 px? совпадает с заказом?) | Попарно ближе к людям, бинарные вопросы стабильнее баллов | 2 вызова на пару | Высокая | [V] GenArena, PairBench (прошлый отчёт) |
| T17 | **Проверка сета целиком** (контактный лист 10 карточек → «какая выбивается?») | Ловит то, что поштучный судья не видит: масштаб, яркость, ракурс | 1 вызов на вариант | Высокая | [I] |
| T18 | **IP-Adapter / Style reference (SD/FLUX)**, ControlNet (structure/canny/depth) | Стандарт в ComfyUI: стиль из картинки без обучения, структура из скетча | Нужен GPU или хостинг (платно) | **Низкая в рамках ограничений.** Упомянуть в защите как «прод-путь Playrix (FLUX + ComfyUI, по вакансиям)». Функционально мы эмулируем это через edit с референсами | [V] вакансии Playrix, Scenario; IP-Adapter — общеизвестно |
| T19 | **LoRA / fine-tune** | Самый надёжный якорь стиля (Rovio: 20–30 картинок) | — | **Своих LoRA Playrix не даёт; обучение своей отложили (сначала пайплайн).** Назвать как следующий шаг после тестового | [V] Rovio, Playrix вакансия |
| T20 | **Human gates + статусы ассетов** | Финальное качество у всех за человеком; кейс Anno 117 | Минуты человека | Высокая: 2 гейта (см. §3) | [V] Rovio, Mighty Bear, Ubisoft |
| T21 | **Дешёвая модель на итерации, сильная на финал** | Экономия | — | Средняя: черновики на low quality / Flash, финалисты на high / Pro | [V] Scenario/Gemini, OpenAI «start with quality low» |

---

## 3. Рекомендуемый пайплайн (без LoRA)

```
[0] Style kit (один раз на игру/стиль)
    - 3–6 эталонных карточек Playrix-стиля (матовые, casual) + 1 «чистый объект» эталон
    - палитра (LAB-статистика / 12 swatch) + шаблон карточки (фон, рамка, тень) — кодом
    - замороженный стиль-блок + keep-лист + негатив-лист (glossy/plastic/vinyl/3D render)
        │
[1] Композитор (LLM): тема + пожелания → 3–5 концепций × 10 объектов
    - каждый объект: родовое имя, 3–5 визуальных признаков, «запрещённые смешения»
    - LLM-проверка: нет гибридов, нет франшиз, объекты различимы по силуэту
        │
  ▶ GATE A (опционально, ~1 мин человека): утвердить списки объектов
        │
[2] Якорь: для каждой концепции генерировать 2–3 кандидата объекта №1
    edit(вход1 = эталонная карточка/объект, вход2..k = эталоны стиля, промпт = шаблон + слот)
    background=transparent, complexity=low, quality фикс.
        │
  ▶ GATE B (~1 мин человека или авто-попарный судья): выбрать якорь сета
        │
[3] Остальные 9 объектов: тот же вызов + якорь сета как доп. вход, N=2 на слот
        │
[4] Авто-QA на каждый кандидат:
    a) alpha-проверка, размер объекта в кадре (bbox), силуэт на 128 px
    b) слепое называние VLM → совпадает с заказом? (анти-гибрид)
    c) эмбеддинг-ранг относительно эталонов (CSD/DINO) → отсечь хвост
    d) попарный VLM-judge среди кандидатов слота (оба порядка) + бинарный чек-лист
    → брак: точечный edit «измени только X» (≤2 попытки), иначе перегенерация
        │
[5] Сборка: палитра (мягкий LAB-перенос) → композит в шаблон карточки кодом
        │
[6] Проверка сета: контактный лист 10 карточек → VLM «какая выбивается?» → фикс
        │
  ▶ GATE C (человек, ~1 мин на вариант): выбрать/одобрить 1 из 3–5 вариантов; статус approved
```

**Почему именно так [I]:**
- Стиль задают пиксели (T1, T2, T4), а не текст. Это главный ответ на «пластик».
- Сборка фона и рамки кодом (T8, T9) делает идентичным всё, что не объект.
- Гибриды режутся дважды: на входе (канонический объект) и на выходе (слепое называние).
- Судья ранжирует, а не выставляет абсолютные баллы. Это согласуется и с GenArena, и с критикой CSD.
- Гейты A–C стоят человеку суммарно ~3–5 минут на запуск. В индустрии гейты у всех ручные (Rovio, InnoGames, Mighty Bear).

**Бюджет [I]:**
- 5 вариантов × (3 якоря + 9×2) ≈ 105 генераций плюс ~20% на исправления.
- Если дорого: 3 варианта и N=1 с исправлением вместо N=2.

**Что сказать на защите [I]:**
- Внутри Playrix стиль держат LoRA и FLUX/ComfyUI (по вакансиям AI Producer и AI Artist).
- Без LoRA мы заменяем это «референсным якорем + шаблоном + отбором».
- Следующий шаг в проде: LoRA на 20–30 эталонах (как у Rovio) подставляется в тот же пайплайн вместо шага [2]. Гейты и QA не меняются.

---

## 4. Что проверено, а что нет

- Цифры эффекта (−50%, 20 → 4 дня, 3x, 8x) — заявления компаний и вендоров. Долю брака в открытых источниках не публикует никто.
- Что техники T3, T10 (мягкий вариант), T11, T12, T17 работают именно на нашем стиле, не проверено. Это гипотезы, нужен A/B на 10–20 генерациях.
- Параметры OpenAI (`complexity`, уровни `quality`, `input_fidelity`, `background=transparent`) взяты из текущего гайда и архивного cookbook. Перед использованием сверить с API-референсом выбранной модели.
- Конкретики по Supercell, Zynga и Moon Active не найдено. По King — только уровни.

---

## 5. Источники

**Playrix**
- AI Producer (Art Development): https://outscal.com/job/ai-producer-art-development-at-playrix-in-cyprus-1
- AI Artist: https://hitmarker.net/jobs/playrix-ai-artist-1520915
- Creatives AI Artist (2D/3D): https://hitmarker.net/jobs/playrix-creatives-ai-artist-2d-3d-1588125
- Подкаст 2.5 Gamers о Playrix AI-креативах: https://brapodd.se/podd/two-a-half-gamers/avsnitt/playrix-just-went-all-in-on-ai-creatives-100-ai-ads-reviewed

**Студии**
- Rovio, GDC 2026: https://schedule.gdconf.com/session/angry-birds-meets-genai-transforming-rovios-asset-creation-with-aws-presented-by-amazon-web-services/917278
- Rovio, разбор ZenML: https://www.zenml.io/llmops-database/accelerating-game-asset-creation-with-fine-tuned-diffusion-models
- NetEase LifeAfter, GDC 2026: https://schedule.gdconf.com/session/lifeafter-aigc-paradigm-change-in-mobile-game-art-production/915039
- King (AP/Fortune): https://fortune.com/article/candy-crush-gaming-ai-technology-art-jobs-puzzles/
- InnoGames × Scenario: https://blog.innogames.com/innogames-x-scenario-streamlining-our-game-production/
- Playkot: https://www.pocketgamer.biz/ai-everywhere-using-neural-networks-for-asset-creation-marketing-and-more
- Mighty Bear: https://medium.com/mighty-bear-games/how-the-use-of-ai-evolved-our-art-production-pipelines-a335c8a257ce
- Cosmic Lounge: https://www.aka.fi/contentassets/9154663e9d6e48c99af0735226db0c74/11.-cosmic-lounge_-tooling-for-game-art-generation-with-ai---business-finland-rrf.pdf
- Ubisoft, Anno 117: https://www.pcgamer.com/games/city-builder/ubisoft-touches-up-ai-art-placeholder-that-slipped-into-anno-117-but-fans-are-not-happy-it-was-there-to-begin-with-of-all-the-video-games-not-anno
- Tencent VISVISE (индекс): https://www.gamedeveloper.com/art/ai-game-art-pipelines

**Вендоры и модели**
- Layer, IP consistency: https://layer.ai/blog/ip-consistency-ai-generation-guide-game-studios
- Scenario reskin: https://www.scenario.com/blog/reskin-game-assets-ai-isometric-art
- Scenario о Gemini (лимиты референсов, советы): https://help.scenario.com/articles/7568607761-gemini-image-models-nano-banana-family
- OpenAI image prompting guide: https://developers.openai.com/api/docs/guides/image-prompting
- OpenAI cookbook, input fidelity: https://developers.openai.com/cookbook/examples/generate_images_with_high_input_fidelity
- OpenAI cookbook, gpt-image-1.5 prompting: https://developers.openai.com/cookbook/examples/multimodal/image-gen-1.5-prompting_guide
- Gemini 2.5 Flash Image: https://developers.googleblog.com/en/introducing-gemini-2-5-flash-image/

**Метрики, судьи, постобработка**
- CSD: https://arxiv.org/abs/2404.01292
- Критика сырого CSD-косинуса: https://arxiv.org/pdf/2605.09030
- GenArena: https://arxiv.org/pdf/2602.06013
- PairBench: https://arxiv.org/pdf/2502.15210
- BiRefNet / ToonOut (удаление фона на стилизованном арте): https://arxiv.org/html/2509.06839v1
- Палитра: https://playgama.com/blog/business-faqs/how-to-enforce-a-unified-color-palette-across-ai-generated-g/

**Не найдено:** публичные доклады Playrix, Supercell, Zynga и Moon Active с конкретикой по консистентности иконок; открытые цифры по доле брака.
