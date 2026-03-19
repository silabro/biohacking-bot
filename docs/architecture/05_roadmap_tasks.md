## 5. Пошаговый план разработки (Atomic AI-Ready Roadmap)

План должен быть выполнен ИИ-разработчиком строго последовательно (TDD).

### Phase 1: Infrastructure, DB & Seed Data
*   **Task 1.1: CI/CD & Env.**
    *   *Context:* Настройка базовой структуры репозитория, Docker и GitHub Actions.
    *   *Scope & Constraints:* Включить `redis:alpine` и `postgres` в `docker-compose.yml`. Использовать строгую типизацию Python 3.12+. **Обязательно** добавить в Dockerfile установку системных зависимостей библиотеки `WeasyPrint` для рендера PDF.
    *   *DoD & Tests:* Создан `.env.example`, пайплайн `pytest` активен. Docker-билд успешно устанавливает зависимости WeasyPrint.
*   **Task 1.2: DB Engine & Alembic.**
    *   *Context:* Первоначальная настройка БД.
    *   *Scope & Constraints:* Настроить `AsyncpgEngine` со стандартным пулом соединений (`pool_size=20, max_overflow=10`). Отказ от `NullPool` для приложения. Инициализировать Alembic.
*   **Task 1.3: SQLAlchemy Models & Pydantic JSONB.**
    *   *Context:* Определение полной схемы данных (Data Schema).
    *   *Scope & Constraints:* Реализовать таблицы из Раздела 4, включая `substance_interactions`. **Timezone Nightmare Rule:** все даты/время сохраняются исключительно в `UTC (TIMESTAMP WITH TIME ZONE)`. **JSONB Schema Drift Rule:** все колонки JSONB мапятся через строгие `Pydantic` DTO классы.
*   **Task 1.4: RuPharma Architecture (ЕСКЛП Парсинг & Seed Data).**
    *   *Context:* Инициализация детерминированной базы фармакологии СНГ.
    *   *Scope & Constraints:* Создать Python CLI-скрипт (`scripts/parse_esklp.py`), который парсит офлайн Excel-архив Минздрава (ЕСКЛП) и наполняет `ru_drugs_registry` (Торговое название -> МНН -> АТХ код). **MVP Seed:** Для холодного старта создать `core_interactions_seed.json` со 100 главными правилами конфликтов (статины, НПВС, КОК, антибиотики) для предзаполнения таблицы `substance_interactions` по кодам АТХ.

### Phase 2: Data Access & Dependency Injection
*   **Task 2.1: Repositories & CRUD (Atomic Unit of Work).**
    *   *Context:* Создание слоя DAO на базе SQLAlchemy.
    *   *Scope & Constraints:* **Strict DoD:** Использование паттерна Unit of Work (`async with session.begin():`) для массовой вставки (балкиннг). **Graceful Overdraft:** Списание ингредиентов (`UPDATE fridge_items SET quantity = GREATEST(quantity - X, 0)`). **NLP Refund TTL:** Возврат продуктов обновляет запись `UPDATE`, а не через `INSERT`, чтобы сохранить `created_at`.
*   **Task 2.2: DI Container & Redis UX-Locks.**
    *   *Context:* Настройка IoC и механизмов идемпотентности.
    *   *Scope & Constraints:* `AsyncEngine` -> `Scope.APP`. Защита от двойного списания/гонок через замок на 60 секунд (`SET lock:{action} 1 EX 60 NX`). В блоке `finally` замок удаляется.

### Phase 3: The Brain (Core AI & APIs)
*   **Task 3.1: External API Clients & Caching.**
    *   *Context:* Интеграция USDA и Open Food Facts API с кэшированием 7 дней. Sanitization.
*   **Task 3.2: Обработка отказов LLM (Gemini Core).**
    *   *Context:* Базовый клиент с оберткой `tenacity` (Rate Limits fallback).
*   **Task 3.3: Гибридный Gatekeeper (Intent Router).**
    *   *Context:* Входной классификатор сообщений пользователя (Gatekeeper).
    *   *Scope & Constraints:* Запрещено использовать LLM для первичной маршрутизации команд! Первый слой — дешевый Regex/FastText/FSM. LLM вызывается для определения интента ТОЛЬКО как fallback, если регулярки не справились (защита бюджета и скорости).
*   **Task 3.4: Vision OCR, Batch Media, CGM & Unit Normalization Engine.**
    *   *Context:* Извлечение чеков, анализов, графиков CGM.
    *   *Scope & Constraints:* **Унификация OCR & UnitConverter:** Gemini извлекает сырые данные (например `1.5` и `кг`). Сервис `UnitConverter` прогоняет их через словарь множителей, возвращая строго `1500` и `g` (или `ml`). **Reference Weights (Проблема Банана):** При отсутствии веса используется словарь `STANDARD_WEIGHTS`. 
    *   **Smart Shopping Session (Dry Run):** Парсер делает сопоставление (Reconciliation) и сохраняет превью в буфер `draft_receipt:{user_id}`, а итоговая запись происходит после ручного `[✅ Да, всё точно]`.
    *   **LLM Retry Loop (Fallback):** Если агент/Vision возвращает сломанный JSON, код делает 1-2 автоматических ретрая с промптом об ошибке валидации. При финальном сбое парсинга чека бот выдает fallback-черновик с кнопками `[Подтвердить / Редактировать текстом / Отменить]`.

### Phase 4: Telegram Layer & State (The SPA Front)
*   **Task 4.1: Bot Initialization, Routing & Lifespan.**
    *   Подключение `dishka.integrations.aiogram`. Защита бюджета Gemini через `ThrottlingMiddleware`.
*   **Task 4.2: FSM Onboarding, Wearables API & NLP UX.**
    *   Строгий русский UI. Вилка Калибровки. Умный Travel Mode. Wearables MVP. **Shadow Mode Калибровки:** 7 дней бот выдает рационы по формуле Mifflin-St Jeor и микро-задания, пока собирает базлайн-метрики (пульс, сон). **Application-Level Encryption:** Хранить OAuth-токены `wearable_tokens` в БД в открытом виде строго запрещено. Перед записью они симметрично шифруются (**обязательно `MultiFernet`**) и расшифровываются только в памяти для поддержки безопасной ротации ключей.
*   **Task 4.3: Клининг UI/UX Дашборда, Контейнеры & Избранное.**
    *   *Scope:* **Клининг UI/UX Дашборда:** На главном экране жестко закрепить 3 кулинарных вектора: 1) `[🍽 Мой рацион]` — План на день (выполняется через `[✅ Съел по плану]`). 2) `[📝 Я сорвался / Съел другое]` — Логирование постфактум (Вилка: Ресторан / Из холодильника). 3) `[🆘 Хочу перекусить]` — Just-in-Time генерация из остатков. Если активен виджет `🔴 Голодание`, кнопка 3 краснеет: `[🆘 Срываюсь с голода]` (выдает воду с солью и психологический саппорт).
    *   **Магия Контейнеров & Smart Pantry:** `Dish Type` (SOUP, ROASTED). Python применяет зашитый константный множитель к весу сырых ингредиентов для создания Виртуального контейнера (`🍱 Готовое блюдо`). Колонка `is_staple` используется как **Smart Pantry** для бакалеи (не списывается из БД).
    *   **Smart Cheat Meal & Emergency Coach:** Вилка читмила (Без списания / С полным списанием запасов). Экстренный коуч голодания выдает саппорт перед досрочным прерыванием "пищевого окна".
    *   **NLP Refund TTL & Atomic Commit Shopping:** Списание из `active_shopping_list` и перенос из `draft_receipt` в БД происходит атомарно. Возврат объедков (`refund_ingredients`) обновляет старую запись в `fridge_items` (сохраняя срок годности). Вычет идет через `GREATEST(quantity - X, 0)`.
    *   **Идемпотентность & UX Locks:** Выдача Telegram Toast *"⏳ Обрабатываю запрос..."* при 60-сек замке. `SELECT` проверка статуса Съедено.

### Phase 5: Multi-Agent Orchestration (Health Advisory Board)
*   **Task 5.1: The Consilium Pipeline (Consilium StateGraph, Blackboard Pattern).**
    *   **Consilium StateGraph & Blackboard Pattern:** Отказ от передачи сырого текста между агентами. Внедрен паттерн **Blackboard (`ConsiliumState`)**. Агенты генерируют в `ConsiliumState` строго типизированные JSON-ограничения (Constraints: `banned_ingredients`, `target_calories`). Оркестратор физически фильтрует БД по этим Constraints ДО вызова Шеф-повара.
    *   **Contraindication Engine (Python-префильтр Врача):** ПЕРЕД вызовом LLM Диагноста, Python анализирует `diseases` и пишет хардкодированные Constraints в `ConsiliumState` из `app/core/clinical/contraindication_rules.json`. LLM НЕ МОЖЕТ переопределить эти ограничения (например, `max_fasting_hours: 12` для гастрита). Виджет голодания подменяется на `🟢 Режим покоя ЖКТ`.
    *   **Proactive Checkup Generator:** Врач возвращает массив ярлыков чекап-блоков (`["base_minimum", "gastritis_block"]`). Python склеивает модули из `app/core/clinical/checkup_protocols.json`, дедуплицирует и сохраняет в `biomarker_logs` со статусом "Ожидает сдачи".
    *   **Двухрежимный Шеф-повар & Магия Дельты:** Режим "Выживание" JIT (фильтрация `fridge_items` по Constraints Врача) и Режим "Творчество" (генерация идеального меню со скрытым холодильником, затем вычет "Дельты" недостающих ингредиентов для `🛒 Списка покупок`).
    *   **Bioavailability Engine & Nutrient Pairing:** Оркестратор сверяет теги `food_matrix_json` ингредиентов с `diseases` юзера по матрице `app/core/clinical/nutrient_synergy.json` и передает Повару корректирующие Constraints (например, *"Добавь кальций для нейтрализации оксалатов при МКБ"*).
    *   **Умное Избранное, Macro-Fillers & Pre-filtering:** При планировании предлагать `[🌟 Собрать из Избранного]`. Python проверяет `user_recipes` на соответствие медицинским Constraints Врача. Поддержка **Graceful Fallback** (извинение и выдача альтернативы при блокировке любимого рецепта) и **Macro-Fillers** (добор КБЖУ к Избранному без его изменения).
    *   **The Ramp-Up Protocol (Zero-to-One):** Для `activity_level` = `low`/`sedentary` тренировки блокируются. NEAT логируется в `lifestyle_logs.movement_minutes`. Геймификация: Нед1-2 прогулки → Нед3 изометрия → Нед4 "Выпускной" (повышение `activity_level` и открытие полного модуля ACWR).
    *   **Стриминг статусов & Saga Pattern (Атомарность Консилиума):** Амортизировать ожидание вызовов LLM со статусами. Механизм `[🛑 Отменить генерацию]` обрывает In-Memory Context без сохранения мусора в БД/Redis.
    *   **Решение "Проблемы Половины Банана", Эволюция Glycogen Shift & Smart Timeout Тренера:** `Culinary Agent` возвращает JSON с `weight_g` и `visual_measure`. Автосдвиг тренировки через `APScheduler` (при 2-часовом таймауте ответа юзера). Защита Глубокого сна блокирует объем порций вечером.
*   **Task 5.2: The Auditor (RuPharma, ATC Conflict Matrix & Защита Варианта Б).**
    *   **Escape FSM (Persistent Keyboard):** К КАЖДОМУ ответу бота в дискуссии крепится инлайн-клавиатура `[✅ Утвердить это меню]` и `[❌ Отменить всё]`. Лимит токенов: макс. 5 сообщений.
    *   **RuPharma Architecture (ATC Conflict Matrix):** LLM выступает ТОЛЬКО переводчиком Торговое название -> МНН -> Код АТХ. Взаимодействия препаратов проверяются через детерминированный запрос к `substance_interactions` по **Кодам АТХ**, исключая галлюцинации.
    *   **Защита Варианта Б:** Если Аудитор переходит к базовому рецепту из остатков холодильника, Повар обязан проверить **Nutrient Density** остатков. Если это не сочетаемые ингредиенты (сахар, масло), принудительно переводить в Вариант А (Посылать в магазин).
    *   **State Tracking Аудитора:** Флаг *"Прошлый вариант забракован, создай принципиально другое"*.
*   **Task 5.3: Redis Draft State (OOM Protection) & Hybrid UI.**
*   **Task 5.4: Synergy Checker (Мгновенное уведомление).**
*   **Task 5.5: Event-Driven Schedulers (Master Cron) & Амнезия ИИ.**
    *   **Отказоустойчивый Cron (Redis JobStore), Anomaly Detection & Защита от спящих (Dormancy Check):** Управление таймзонами через `APScheduler` с `RedisJobStore`. **Dormancy Check:** Если юзер не взаимодействовал с ботом более 3 дней (`last_active_at`), фоновые LLM-задачи замораживаются до его активности. При отправке дайджеста в 08:00, Cron запрашивает умные часы. Если юзер активен уже несколько часов (смещение offset), бот проактивно спрашивает: *"Кажется, ты сменил часовой пояс. Обновить настройки?"*. Это избавляет PostgreSQL от ежеминутного поллинга и гарантирует выживание расписания (Server Restart Resilience).
    *   **Интерактивная Гистаминная Безопасность:** TTL блюд. Проактивно повар ставит в план. Реактивно пуш от Аудитора с "Histamine Watch" (24ч).
    *   **Амнезия ИИ:** Защита от Context Exhaustion. Старые логи `symptom_logs` сбрасываются в `diseases` и не передаются в Консилиум.
*   **Task 5.6: Clinical PDF Generator (Статические шаблоны & WeasyPrint).**
    *   *Context:* Отказ от Playwright для снижения веса и сложности Docker.
    *   *Scope & Constraints:* ИИ (Врач) генерирует ТОЛЬКО текст Executive Summary. Python-код собирает цифры из БД, подставляет их вместе с текстом в статический `HTML/CSS` шаблон через библиотеку `Jinja2`. Готовый HTML рендерится в PDF через библиотеку `WeasyPrint` внутри `await asyncio.to_thread()`. **Защита от Thread Starvation (Изолированный ThreadPool):** Для `WeasyPrint` должен быть создан ВЫДЕЛЕННЫЙ изолированный пул потоков на 3 воркера, чтобы рендер не заблокировал выполнение других фоновых задач. Генерация СТРОГО в io.BytesIO без сохранения на диск.
