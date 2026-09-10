# 🏦 Check All Brokers

**Незалежний інформаційно-аналітичний проект з перевірки брокерів та надання юридичних консультацій**

## 🌟 Основні функції

### 📊 Аналіз брокерів
- Незалежна оцінка брокерських компаній
- Детальні відгуки та рейтинги
- Аналіз ризиків та надійності

### 💼 Юридичні консультації
- Безкоштовні консультації для жертв шахрайства
- Професійна юридична підтримка
- Допомога у відновленні коштів

### 💬 Інтерактивний форум
- Обговорення питань брокерів
- Модерація контенту
- Система сповіщень
- Пошук по форуму

### 📱 Сучасний інтерфейс
- Адаптивний дизайн
- Мобільне меню
- Плаваючі кнопки Telegram та чату
- Інтерактивний чат-віджет

## 🛠 Технології

- **Backend**: Django 4.2 + Wagtail CMS
- **Frontend**: HTML5, CSS3, JavaScript
- **База даних**: PostgreSQL (продакшн) / SQLite (розробка)
- **Стилі**: Bootstrap 5
- **Email**: Resend API / SMTP

## 🚀 Встановлення

1. **Клонування репозиторію**
   ```bash
   git clone https://github.com/your-username/check-all-brokers.git
   cd check-all-brokers
   ```

2. **Створення віртуального середовища**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # або
   venv\Scripts\activate     # Windows
   ```

3. **Встановлення залежностей**
   ```bash
   pip install -r requirements.txt
   ```

4. **Налаштування змінних оточення**

   Створіть файл `.env` у корені проекту (див. `.env.example`):
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=checkallbrokers.com,www.checkallbrokers.com
   DB_NAME=broker_control
   DB_USER=broker_user
   DB_PASSWORD=your-db-password
   DB_HOST=localhost
   DB_PORT=5432
   EMAIL_HOST_PASSWORD=your-email-password
   RESEND_API_KEY=your-resend-api-key
   WAGTAILADMIN_BASE_URL=https://checkallbrokers.com
   ```

5. **Налаштування бази даних**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Створення суперкористувача**
   ```bash
   python manage.py createsuperuser
   ```

7. **Створення тестових даних**
   ```bash
   python manage.py create_forum_data
   python manage.py create_demo_topics
   ```

8. **Запуск сервера**
   ```bash
   python manage.py runserver
   ```

## 📁 Структура проекту

```
CheckAllBrokers/
├── broker_control/          # Налаштування проекту
├── content/                 # Головний контент
├── blog/                    # Блог
├── consultations/           # Консультації
├── forum/                   # Форум
├── legal/                   # Юридичний розділ
├── templates/                # Шаблони
│   ├── includes/            # Включені шаблони
│   ├── forum/               # Шаблони форуму
│   └── ...
├── static/                   # Статичні файли (включно з robots.txt)
└── media/                    # Завантажені файли
```

## 🎯 Основні сторінки

### 🏠 Головна сторінка
- Інформація про проект
- Останні новини
- Форма заявки на консультацію

### 📝 Блог
- Статті про брокерів
- Аналітика ринку
- Корисні поради

### 💬 Форум
- **Категорії**: Загальні питання, Відгуки про брокерів, Технічна підтримка
- **Створення тем** з модерацією
- **Коментування** з модерацією
- **Пошук** по форуму
- **Сповіщення** для користувачів

### ⚖️ Консультації
- Форма заявки
- Онлайн чат
- Історія консультацій

## 🔧 Адміністрація

Адмін-панель на базі Wagtail CMS доступна за адресою `/admin/`.

### Модерація форуму
- Одобрення/відхилення постів
- Управління темами
- Логи модерації

### Управління контентом
- Редагування сторінок
- Управління блогом
- SEO-налаштування (title, description для кожної сторінки)

## 🔍 SEO

- `robots.txt` — віддається статично через nginx
- `sitemap.xml` — генерується автоматично на основі дерева сторінок Wagtail
- Canonical URL та meta-теги налаштовані для кожної сторінки
- Google Search Console підключено для моніторингу індексації

## 📱 Мобільна версія

Проект повністю адаптивний і працює на всіх пристроях:
- 📱 Смартфони
- 📱 Планшети
- 💻 Десктопи

## 🔒 Безпека

- Модерація всіх постів форуму
- Захист від спаму
- HTTPS обов'язковий на продакшні (SSL/HSTS)
- Секрети зберігаються у змінних оточення, не в коді
- Валідація даних

## 📞 Контакти

- **Telegram**: [@checkallbrokers](https://t.me/checkallbrokers)
- **Email**: info@checkallbrokers.com
- **Сайт**: https://checkallbrokers.com

## 🤝 Внесок

1. Форк репозиторію
2. Створення гілки для нової функції
3. Внесення змін
4. Створення Pull Request

## 📄 Ліцензія

Цей проект розповсюджується під ліцензією MIT.

---

**Check All Brokers** — ваш надійний партнер у світі фінансів! 💪