# 04. Генераторы со style-reference и API: сравнение (состояние на 20.11.2026)

**Задача:** автономная генерация карточек для casual mobile игры (одиночные объекты, стабильный стилизованный "painted 3D-ish" стиль уровня флагманов Playrix), соответствие ~20 референсам. **Ограничения:** свои LoRA Playrix не даёт, обучение своей отложено; бюджет ~$400; текущий генератор GPT Image, уже тестировались Nano Banana / Nano Banana Pro.

**Метод:** только desk research (веб-поиск и чтение документации/прайсов). Платные API не вызывались, нигде не регистрировался, тестовых генераций не делал.

**Маркировка:**
- **[V]**: проверено по первоисточнику или профильному агрегатору, ссылка и дата чтения 2026-11-20 (в скобках дата самого источника, если она указана).
- **[I]**: вывод или знание по памяти, по первоисточнику не проверено. Перед бенчем это нужно проверить.
- **[?]**: не нашёл.

> Важно: рынок сильно сдвинулся. В brief указаны gpt-image-2, Flux 2/Kontext, Ideogram 3.0, Imagen 4, но на ноябрь 2026 уже вышли **GPT Image 2.5 (08.09.2026) и 2.6 (04.11.2026)**, **FLUX 3 Image (01.10.2026)**, **Nano Banana 2.1**, **Ideogram 4.0/4.5**, **Recraft V4 Styles (08.2026)**, **Seedream 5.5**, **Midjourney V8.2**, **Krea 2**. Imagen 4 снят с Gemini API 24.06.2026. Снапшот `gpt-image-2-2026-04-21` помечен как deprecated.

> Лимит веб-запросов (100 fetch/час) закончился до конца сессии. Поэтому часть полей по Leonardo, Scenario, Layer, Stability, Replicate осталась [I] или [?].

---

## 1. Сводная таблица

Цены указаны за 1 изображение около 1K, если не оговорено иное. "Реф." означает максимум входных изображений-референсов за запрос.

| Генератор / модель | Реф. | Style-ref отдельно от content-ref | Strength | Прозрачный фон | Разрешение | Цена/изобр. | API / Python | Лимиты | ToS / ограничение "без LoRA" |
|---|---|---|---|---|---|---|---|---|---|
| **Recraft V4 Styles** (`recraftv4_styles`, `_pro`, `_vector`) | **1–10** стилевых реф. [V] | **Да**: отдельный механизм `style_reference_urls` / `style_id` [V] | `image_weights` (вес каждого рефа), `match: flexible/precise` [V] | Нативной альфы нет. Есть `background_color`, PNG, Remove background за $0.01 [V] | 1K (base), 2K (Pro), SVG. Aspect или WxH [V] | **$0.035** (1K), $0.10 (Pro 2K), $0.05/0.12 SVG. Создание style $0.005 один раз [V] | REST + **OpenAI Python SDK** (`base_url=external.api.recraft.ai/v1`, `extra_body`) [V] | [?] | **Серая зона**: создаётся сохраняемый `style_id`, но документация прямо пишет "nothing needs training or fine-tuning" [V]. Можно не создавать style, а передавать `style_reference_urls` в каждом запросе |
| **Recraft V3 / V4** (обычные) | V3: custom style через `/styles`, до 5 изобр. [I] | V3: да [I] | [?] | Remove bg $0.01 [V] | до 2K (V4 Pro) [V] | V3/V4 $0.04, V4 Pro $0.25 [V] | как выше [V] | [?] | Для стиля по референсам V4 Styles новее и дешевле |
| **FLUX 3 Image** (BFL, 01.10.2026) | **до 10** [V] | **Нет**: общий `referenceImages`, стиль задаётся промптом ("in the style of image 1–N") [V/I] | нет явного [I] | Альфа не документирована [V] | 0.75K / 1K / 1.5K / 2K / 4K, AR от 21:9 до 9:21 [V] | **$0.048** (1K), $0.10 (2K). **Рефы бесплатны** [V] | BFL REST (async polling), Runware, fal, Comfy [V] | [?] | Веса закрыты (только enterprise-контракт) [V]. Без LoRA |
| **FLUX 3 Klein** | [I] как у FLUX 3 | нет [I] | – | – | до 4K [V] | **$0.009** (1K) [V] | BFL [V] | [?] | Дешёвый черновой вариант |
| **FLUX.2 [pro] / [max] / [flex]** | **до 8 по API** (10 в playground) [V] | нет (multi-reference editing) [V] | нет [I] | нет [I] | до 4MP [V] | pro: $0.03 за 1-й MP + $0.015/MP за реф → с 8 рефами по 1MP около **$0.15**. max: $0.07 + $0.03/MP реф [V] | BFL REST, Python `requests` [V] | [?] | OK |
| **FLUX.1 Kontext pro / max** | 1 (по API; multi через склейку) [I] | нет | нет | нет | ~1MP [I] | $0.04 / $0.08 [V] | BFL, fal, Replicate [V] | [?] | Устарел относительно FLUX.2/3 |
| **FLUX Redux** | 1 [I] | image-variation (смешивает стиль и контент) [I] | через ComfyUI / strength [I] | – | ~1MP | дёшево на fal [I] | fal / ComfyUI [I] | – | Устарел |
| **Ideogram 3.0** | **до 10 `style_reference_images`** (≤25MB) [V] | **Да**: style refs заменяют style preset [V]. Character ref отдельный | Явного strength нет [V] | **Да, нативно**: эндпоинт 3.0 Transparent $0.04–0.10 [V] | 1K–2K [I] | Turbo $0.03, Default $0.06, **Quality $0.09**. С character ref $0.10–0.20 [V] | REST (multipart), Python `requests`. Также fal / Replicate [V] | **10 in-flight** по умолчанию [V] | OK. "Custom models" за $40 = обучение, **нельзя** [V] |
| **Ideogram 4.0 / 4.5** | 4.5: до 5 source/ref изобр. (как edit-входы) [V] | **Нет style ref**: картинки трактуются как вход для edit [V] | – | 4.0 Transparent $0.03–0.10 (1K/2K) [V] | 1K/2K (до 8K у 4.0) [V] | 4.5: $0.03/0.06/0.10, с ref $0.22 (High) [V] | REST, Krea, fal [V] | 10 in-flight [V] | Для style-transfer хуже, чем 3.0 |
| **Midjourney V8.2 / V7 / Niji 7** | `--sref`: несколько URL, без явного максимума [V]; Edit model V8 до 4 реф. [V] | Да: `--sref` (стиль), `--oref` только V7 [V]. Moodboards и personalization `--p` | `--sw` 0–1000, `--ow` 0–1000 [V] | нет [I] | до 2K (upscale) [I] | подписка $10–120/мес [V] | **Официального API нет** (на 30.09.2026) [V] | – | **ToS запрещает автоматизацию**: "You may not use automated tools…" (ToS от 27.05.2026) [V]. Неофициальные прокси нарушают ToS. **Пропустить** |
| **Leonardo** (Phoenix, Lucid Origin + хостинг сторонних: Seedream 5.5, NB 2.1, GPT Image 2.6, FLUX.2 Pro, Ideogram 4.5) | Style Reference через controlnets, до ~4 рефов [I] | Да: Style Ref / Content Ref / Character Ref как разные preprocessor [I] | `strengthType` Low/Mid/High/Max [I] | Remove bg (отдельный эндпоинт) [V]. Transparency у Phoenix [I] | ~1.5K [I] | кредиты, PAYG в $ [V]. Точные $ не нашёл [?] | REST v1/v2 [V] | [?] | OK. Свои Phoenix/Lucid по качеству для casual 3D-ish скорее средние [I]. Ценность Leonardo в основном агрегаторская |
| **Scenario** | img2img по asset ID, плюс сторонние модели (Gemini 3.1 Flash, BFL, OpenAI) [V] | Ключевая фича "style models" = **LoRA-обучение** (FLUX.2, Qwen, Z-Image) [V] | – | Remove bg (Photoroom, Pixa) [V] | – | CU. Обучение 450 CU на 20 изобр., ~5 CU/изобр. Flux Dev [V]. Курс CU→$ [?] | REST, `dryRun=true` для оценки цены [V] | [?] | Главная ценность (обученные style models) **требует обучения своей LoRA (отложено)**. Остальное есть у первоисточников дешевле |
| **Layer.ai** | [?] | "Custom style training" на ассетах студии [V] | – | [?] | – | CU по $0.08, подписка от $10 / 300 CU [V] | REST v1/v2, OpenAPI, MCP [V] | [?] | Стиль через **обучение**, нельзя. Пропустить |
| **Krea 2** (Medium / Large) | `image_style_references` (максимум не указан), moodboard 1/запрос [V] | **Да**: style refs отдельно от "styles" (= LoRA) [V] | "tunable strength" [V] | [?] | **только 1K**, 8 AR [V] | Medium $0.030, **с style refs $0.035**, moodboard $0.040. Large $0.060–0.070 [V] | REST [V] | [?] | `styles` = обученные LoRA, **не использовать**. `image_style_references` без обучения OK. Medium "strongest on illustration, painting" [V] |
| **Runway** (gen4_image + хостинг Seedream / NB / GPT) | gen4_image: до 3 references [I] | content/character-ориентирован [I] | – | нет [I] | 720p / 1080p [V] | gen4_image $0.05/0.08, turbo $0.02 [V] | REST, `runwayml` SDK [I] | [?] | Для стилевого переноса предметки не профильный [I] |
| **Stability** (SD 3.5, Stable Image, Control Style / Style Guide) | 1 style image [I] | Style Guide / Control Style: да [I] | `fidelity` / `style_strength` [I] | Remove bg (отдельно) [I] | до 1.5MP [I] | SD3.5 Large $0.065, Core $0.03, Ultra $0.08 [V] (agg., 08.11.2026). Style-эндпоинты [?] | REST [V] | [?] | Качество ниже frontier, отстаёт [I] |
| **Seedream 5.5** (ByteDance, BytePlus ModelArk / Runway / Leonardo) | несколько `input_images` (примеры 1–2, максимум не указан) [V]. У Seedream 4.x до 10–14 [I] | нет (multi-ref edit) [I] | нет [I] | layer decomposition (отдельные слои) [V], альфа [?] | 1K / 1.5K / 2K, до ~4.6MP, AR до 16:1 [V] | **$0.020** (1K), $0.035 (2K) **+ $0.008/реф** [V] | BytePlus REST (OpenAI-подобный), fal / Runway [V/I] | [?] | Китайский провайдер: проверить ToS по коммерческому использованию и данным [I] |
| **Qwen-Image-2 Pro Edit / Qwen-Image-Edit-2511** (Alibaba) | 2 Pro: **1–3** [V]. 2511: список, максимум не указан [V] | нет | нет (guidance_scale) [V] | PNG без альфы на входе [V] | до 2048² [V] | 2 Pro: **$0.075** (fal). 2511: $0.03/MP [V] | fal-client, DashScope [V] | [?] | Open weights (2511), можно локально через ComfyUI [I] |
| **HunyuanImage 3.0** (Tencent) | T2I: **нет рефов** [V]. Instruct/edit-вариант [I] | – | – | нет | auto / 1K [V] | ~$0.09/MP (fal) [V] | fal [V] | [?] | Для задачи "match 20 refs" не подходит |
| **Imagen 4** | – | – | – | – | – | – | **Снят с Gemini API 24.06.2026** [V] | – | **Пропустить** |
| **GPT Image 2.6** (Sunburst / Flare, 04.11.2026) *(текущий)* | multi-image edit, для 2.6 максимум не опубликован [V]. У семейства gpt-image исторически до 16 [I] | нет отдельного style-ref (всё через промпт + изображения) [I] | `input_fidelity` (было у gpt-image-1.x/2) [I] | у 2.5 **да** (`background: transparent`, PNG/WebP) [V]. У 2.6 [?] | 1024², 1536×1024 и др. [I] | токены: вывод $30/M, image-input $8/M [V]. ~**$0.027–0.035** medium 1024² [V]. Плюс рефы (input-токены) | `openai` Python SDK [V] | gpt-image-2: Build 20 IPM, Launch 150, Grow 250 [V]. У 2.6 таблицы нет [V] | OK. Batch для 2.6 **нет**, у 2.5 есть (−50%) [V] |
| **GPT Image 2.5** | как выше | – | – | **да** [V] | – | ~$0.013 (medium) / $0.053 (high) 1024², без учёта input [V] | SDK, Batch −50% [V] | 20/150/250 IPM [V] | Дешёвый baseline с прозрачностью |
| **Nano Banana 2.1** (`gemini-nano-banana-2.1`, stable) *(тестировался)* | **14** (10 object + 4 character) [V] | нет отдельного style-слота [V] | нет | не упомянут → нет [V] | 1K / 2K / 4K [V] | **$0.0336** (1K), $0.0504 (2K). Batch −50% [V] | `google-genai`, Batch API [V] | [?] | OK |
| **Nano Banana Pro** (`gemini-3-pro-image`) *(тестировался)* | 14 = 6 object + 5 character + **3 style** [V] | **Да, 3 style-слота** [V] | нет | нет [V] | 1K / 2K / 4K [V] | $0.134 (1K/2K), $0.24 (4K). Batch $0.067 [V] (agg., 23.10.2026) | `google-genai` [V] | [?] | OK |
| **fal.ai** (агрегатор) | зависит от модели | – | – | – | – | цены близки к вендорским (Qwen 2511 $0.03/MP, Qwen 2 Pro $0.075, Hunyuan $0.09/MP) [V] | `fal-client` (Python, async queue) [I] | [?] | Удобен как единый ключ для FLUX 3, Seedream, Qwen, Ideogram, GPT [V/I] |
| **Replicate** | зависит от модели | – | – | – | – | per-image / per-second [I] | `replicate` Python SDK [I] | [?] | Альтернатива fal. Разницы для задачи нет [I] |
| **ComfyUI + IP-Adapter / style transfer** (локально или RunComfy / ComfyDeploy) | любое (IP-Adapter, Redux, multi-ref Qwen / FLUX.2 dev) [I] | **Да, лучший контроль**: IPAdapter style-only / composition-only, StyleAligned [I] | вес IP-Adapter 0–1+, по блокам [I] | через RMBG / BiRefNet ноды [I] | любое | RunComfy: L40S $2.99/ч (PAYG), A100 $4.99/ч, посекундно, cold start оплачивается [V] | RunComfy serverless API (REST) [V] | – | Без LoRA OK. Но много инженерии и сопровождения; SDXL/IP-Adapter по качеству ниже frontier [I] |

---

## 2. Ключевые наблюдения

1. **Отдельный style-reference как механизм (а не "картинка в контексте")** на ноябрь 2026 есть у: **Recraft V4 Styles** (до 10, веса по рефам) [V], **Ideogram 3.0** (до 10) [V], **Krea 2** (`image_style_references`) [V], **Nano Banana Pro** (3 style-слота) [V], **Midjourney --sref** (без API) [V], Leonardo Style Reference [I], Stability Style Guide [I], ComfyUI IP-Adapter [I]. Остальные (FLUX 3/2, Seedream, Qwen, GPT Image, NB 2.1) работают как multi-reference editing: стиль надо формулировать промптом, а контент рефов "протекает" в результат [I].
2. **Протекание контента** (копирование объектов с рефов вместо переноса стиля) — главный риск multi-ref моделей для задачи "один новый объект в стиле 20 рефов" [I]. Модели со специальным style-механизмом (Recraft, Ideogram 3.0, Krea 2) теоретически устойчивее к нему. Это и нужно проверить в бенче.
3. **Прозрачный фон нативно** проверен только у **Ideogram 3.0/4.0 Transparent** и **GPT Image 2.5** [V]. У остальных схема "сплошной фон → remove-bg": Recraft $0.01 [V], Scenario/Leonardo [V], BiRefNet локально [I].
4. **Цены у претендентов низкие** ($0.02–0.10/изобр.). При бюджете $400 бенч обходится в десятки долларов, ограничением будет время на оценку, а не деньги.
5. **Grey zone "стиль без LoRA":**
   - Recraft `POST /styles` возвращает сохраняемый `style_id`. Вендор утверждает, что обучения нет [V]. Безопасная альтернатива: передавать `style_reference_urls` в каждом запросе, тогда объекта-стиля нет совсем [V].
   - Krea `styles`, Ideogram Custom Models, Scenario style models, Layer style training — это **явное обучение** своей LoRA, его отложили [V].
   - Midjourney moodboards/personalization — профиль вкуса без классического обучения [I], но API нет, и вопрос всё равно отпадает.

## 3. Репутация качества для stylized casual game assets

Независимых бенчмарков именно по "Playrix-like painted 3D casual props" я не нашёл [?]. Ниже мнение, а не измерение:
- **Recraft**: сильная сторона — иллюстрация, иконки, стабильность стиля по серии; изначально заточен на "brand style consistency". Для painted 3D-ish ожидаемо хорош в иконочном плане, слабее в объёмной светотени [I].
- **Ideogram 3.0 + style refs**: хорошее соответствие палитре и рендеру референсов, бывают артефакты на сложных объектах [I].
- **FLUX 3 / FLUX.2**: высокое качество и детализация, лучший prompt adherence. Стиль по 10 рефам держит хорошо, но склонен к фотореалистичному рендеру без жёсткого промпта [I]. Скорость FLUX 3: ~59 с на запрос через Runware, разброс 40 с – 6 мин [V].
- **Nano Banana Pro / 2.1 и GPT Image 2.x** (уже тестировались): сильный контроль композиции, но стиль "дрейфует" к собственной эстетике модели (у GPT характерная "гладкость" и тёплый тон) [I].
- **Krea 2 Medium**: вендор позиционирует как "strongest on illustration, anime, painting" [V]. Только 1K [V].
- **Seedream 5.5**: дешёвый, сильный в стилизации по отзывам [I].
- **Midjourney Niji 7 / V8 + sref**: по визуалу, вероятно, лучший для stylized [I], но без API и с запретом автоматизации в ToS.
- Исследование Room 8 (Creative Bloq, 08.04.2025) ставило SDXL и Flux.1 Dev в топ для game art, но с обучением LoRA [V]. Это устарело и требует обучения LoRA.

---

## 4. Рекомендация

### Топ-3 для бенча (плюс 2 контрольные модели, которые уже есть)

1. **Recraft V4 Styles** (+ Styles Pro). Единственный вендор, у которого style-from-refs — основной продукт: 10 рефов, веса рефов, `precise/flexible`, $0.035 за изображение, OpenAI-совместимый SDK, remove-bg $0.01. Grey zone: в отчёте явно задокументировать, что используем `style_reference_urls` per-request (или `style_id` по заявлению вендора "без обучения").
2. **Ideogram 3.0 со `style_reference_images`** (до 10) + **3.0 Transparent**. Отдельный style-механизм плюс нативная альфа, что сразу закрывает требование карточного ассета. $0.06–0.10.
3. **FLUX 3 Image** (запасной вариант в той же обвязке: **FLUX.2 [pro]**). Frontier-качество, 10 рефов, рефы бесплатны, $0.048 за 1K. Нужен как "сильный multi-ref" против style-ref подхода. Доступ через BFL API или fal.

**Контроль (baseline):** GPT Image 2.6 (текущий; или 2.5 ради `background: transparent` и Batch) и Nano Banana Pro со всеми **3 style-слотами** + 11 content-слотами. Если в прошлых тестах не использовались явные style-слоты, это бесплатный быстрый выигрыш.

**Резерв, если топ-3 не дотянет:** Krea 2 Medium (`image_style_references`, $0.035, без LoRA-`styles`) и Seedream 5.5 ($0.02 + $0.008/реф).

### Пропустить
- **Midjourney**: нет официального API, ToS прямо запрещает автоматизацию [V].
- **Scenario, Layer.ai**: их ценность в обученных style models (LoRA), обучение своей отложено [V]. Остальное — перепродажа тех же моделей.
- **Imagen 4**: снят с API 24.06.2026 [V].
- **HunyuanImage 3.0**: T2I без референсов [V].
- **FLUX.1 Kontext / Redux**: вытеснены FLUX.2/3 [I].
- **Stability SD 3.5 / Style Guide**: ниже frontier [I].
- **Runway gen4_image**: заточен на character/content [I].
- **Leonardo**: своих моделей уровня frontier нет, сторонние доступнее напрямую [I]. Его Style Reference со `strengthType` — только если понадобится явный strength.
- **ComfyUI + IP-Adapter**: лучший контроль style vs content, но много инженерии и инфраструктуры. Возвращаться, только если ни один вендор не даст стабильности. Инфраструктура RunComfy L40S ~$3/ч [V].

### План бенча

**Фиксировано для всех моделей:**
- **6 промптов**: одиночные объекты разной сложности, например (1) деревянный сундук с золотом, (2) корзина фруктов, (3) садовая лейка, (4) торт со свечами, (5) маленький домик-пекарня (архитектура), (6) кот-персонаж в позе (органика, проверка протекания).
- Шаблон промпта общий, плюс короткий style-суффикс из style bible.
- **Наборы рефов**: A = 10 лучших из 20 (лимит Recraft, Ideogram и FLUX 3); B = 5 рефов; для Nano Banana Pro: 3 style + 11 content.
- Seed фиксировать там, где он поддерживается. **4 изображения на промпт** = 24 на конфигурацию.
- **Метрики**: style-score из `style-metrics/` (CLIP/DINO/CSD-сходство с центроидом 20 рефов), слепая оценка "matches set Y/N" и дефекты, протекание контента (сходство с ближайшим рефом выше порога = копия), прозрачность или качество вырезки, $ и секунды на принятый ассет.

**Конфигурации и стоимость** (оценка по ценам из таблицы):

| Модель | Конфигурации | Изобр. | $/изобр. | Итого |
|---|---|---|---|---|
| Recraft V4 Styles | A-precise, A-flexible, B-precise | 72 | 0.035 (+0.01 remove-bg) | ~$3.3 |
| Recraft V4 Styles Pro | A-precise | 24 | 0.10 (+0.01) | ~$2.6 |
| Ideogram 3.0 Quality + style refs | A, B | 48 | 0.09 [I: цена style ref = базовой] | ~$4.3 |
| Ideogram 3.0 Transparent Quality + style refs | A | 24 | 0.10 | ~$2.4 |
| FLUX 3 Image 1K | A, B | 48 | 0.048 | ~$2.3 |
| FLUX.2 [pro] 1MP + 8 рефов | A(8) | 24 | ~0.15 | ~$3.6 |
| GPT Image 2.6 medium + 10 рефов (baseline) | A | 24 | ~0.035 + ~0.10 input [I] | ~$3.5 |
| Nano Banana Pro 1K, 3 style + 11 content (baseline) | A | 24 | 0.134 | ~$3.2 |
| **Итого первый проход** | | **312** | | **~$25** |

С повторами на настройку промптов (×3) и финальным прогоном лучшей пары на 20 новых объектах (~100 изобр. × ~$0.1) выйдет **~$85–100**. Это около 25% бюджета, остаток идёт на продакшн-прогон и резервных кандидатов (Krea 2 и Seedream 5.5 вместе добавят ~$5).

**Порядок:**
1. Ключи Recraft, Ideogram, BFL (или единый fal).
2. Общий Python-адаптер `generate(model, prompt, refs, n, seed) → png + meta.json`.
3. Прогон по одной модели с ранней остановкой, если style-score явно ниже baseline.
4. Таблица результатов и выбор 1–2 моделей.

**Что проверить перед бенчем (сейчас [I] / [?]):**
- лимиты RPM у Recraft и BFL;
- максимум input-изображений у GPT Image 2.6 и поддержка `background: transparent` у 2.6;
- цена Ideogram 3.0 со style refs (сверить с `developer.ideogram.ai` generate-v3);
- `style_strength` у Krea 2;
- ToS Recraft (Developer Terms) по правам на выход и использованию загруженных рефов.

---

## 5. Источники (прочитаны 2026-11-20)

- Recraft V4 Styles, модель (выпуск 08.2026, "no training"): https://www.recraft.ai/docs/recraft-models/recraft-v4-styles.md
- Recraft API, V4 Styles (`/v1/styles`, 1–10 рефов, `image_weights`, `match`, цены): https://www.recraft.ai/docs/api-reference/models/recraft-v4-styles
- Recraft API pricing: https://www.recraft.ai/docs/api-reference/pricing.md
- Recraft usage / OpenAI SDK: https://www.recraft.ai/docs/api-reference/usage
- BFL pricing (FLUX 3, FLUX 3 Klein, FLUX.2, Kontext): https://bfl.ai/pricing?category=flux+tools ; https://docs.bfl.ai/quick_start/pricing.md
- FLUX.2 image editing (до 8 рефов по API, 4MP): https://docs.bfl.ai/flux_2/flux2_image_editing
- FLUX 3 Image на Runware (01.10.2026, 10 рефов, ~59 с): https://runware.ai/docs/models/bfl-flux-3-image
- FLUX 3, обзор (03.10.2026, закрытые веса): https://xenospectrum.com/en/flux-three-image-editing-control/
- Ideogram API pricing (на 20.11.2026, 10 in-flight): https://ideogram.ai/features/api-pricing
- Ideogram style reference (до 10, только 3.0): https://docs.ideogram.ai/using-ideogram/features-and-tools/reference-features/style-reference
- Ideogram 4.5 на Krea: https://www.krea.ai/docs/api-reference/image/ideogram-45.md
- OpenAI image generation guide (2.5 / 2.6): https://developers.openai.com/docs/guides/image-generation
- OpenAI gpt-image-2 (deprecated, rate limits): https://developers.openai.com/api/docs/models/gpt-image-2
- GPT Image 2.5 (08.09.2026, transparent, токены): https://grida.co/docs/models/gpt-image-2.5
- GPT Image 2.6 (04.11.2026, без Batch): https://www.datastudios.org/post/openai-gpt-image-2-6-sunburst-flare-api-pricing-no-batch-gifs-svg ; https://kie.ai/blog/gpt-image-2-6-pricing (06.11.2026)
- Gemini Nano Banana 2.1 (14 рефов, обновлено 10.2026): https://ai.google.dev/gemini-api/docs/models/gemini-nano-banana-2.1.md.txt
- Gemini image models (NB Pro: 6 object + 5 character + 3 style): https://ai.google.dev/gemini-api/docs/nanobanana
- Gemini pricing: https://ai.google.dev/pricing
- Nano Banana Pro pricing (23.10.2026, агрегатор): https://usagebox.com/articles/nano-banana-pro-api-pricing-cost-per-image-2026
- Imagen 4 retirement 24.06.2026: https://dev.to/flarecanary/google-retires-every-imagen-model-on-june-24-and-the-gemini-image-migration-fails-silently-in-4-paf
- Midjourney: нет API, ToS (30.09.2026): https://www.aifreeapi.com/en/posts/midjourney-api-guide.md ; Style Reference: https://docs.midjourney.com/docs/style-reference ; гайд V8.x (27.10.2026): https://blakecrosley.com/en/guides/midjourney
- Leonardo docs index (модели и инструменты API): https://docs.leonardo.ai/llms.txt
- Scenario API pricing: https://docs.scenario.com/page/api-pricing ; capabilities: https://docs.scenario.com/docs/key-capabilities-at-a-glance ; model costs: https://help.scenario.com/articles/8811829644-model-costs-for-asset-generation
- Layer: https://layer.ai/agent.md ; https://www.layer.ai/pricing/calculator
- Krea 2 API (style refs, цены): https://www.krea.ai/docs/developers/krea-2/overview.md
- Runway API pricing: https://docs.dev.runwayml.com/guides/pricing/
- Stability pricing (агрегатор, 08.11.2026): https://www.activepieces.com/blog/stability-ai-api-pricing-in-2026-and-cost-per-image.md
- Seedream 5.5 pricing (APIYI, тесты от 13.11.2026): https://docs.apiyi.com/en/api-capabilities/seedream-image/seedream-5-5-pricing.md
- Qwen Image 2 Pro Edit (fal): https://fal.ai/models/fal-ai/qwen-image-2/pro/edit/llms.txt ; Qwen-Image-Edit-2511: https://fal.ai/models/fal-ai/qwen-image-edit-2511/llms.txt
- HunyuanImage 3.0 (fal): https://fal.ai/models/fal-ai/hunyuan-image/v3/instruct/text-to-image/llms.txt
- RunComfy billing: https://docs.runcomfy.com/serverless/about-billing.md
- Creative Bloq / Room 8 (08.04.2025): https://www.creativebloq.com/3d/video-game-design/these-are-the-4-best-ai-generators-for-game-art-according-to-pros
