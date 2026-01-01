import random
import string

def generate_test_emails(include_unicode=False):
    """
    Генерирует список тестовых email: позитивные и негативные.
    Каждый email в паре с описанием (для QA).
    
    Args:
        include_unicode (bool): Включить Unicode в тесты (по RFC 6531).
    
    Returns:
        list of tuples: [(email, description, is_valid)]
    """
    test_cases = []
    
    # Допустимые символы по RFC 5322
    local_allowed = string.ascii_letters + string.digits + "!#$%&'*+-/=?^_`{|}~"
    domain_allowed = string.ascii_letters + string.digits + "-"
    
    # Позитивные кейсы
    # 1. Минимальный: короткий валидный
    min_email = "a@a.ru"
    test_cases.append((min_email, "Позитив: минимальная длина (валидный короткий email)", True))
    
    # 2. Средний: типичный
    mid_email = "user.example+tag@subdomain.domain.com"
    test_cases.append((mid_email, "Позитив: средняя длина с поддоменом и тегом", True))
    
    # 3. Граничный max: 64 в local, 63 в label, всего ~254
    local_max = ''.join(random.choice(local_allowed) for _ in range(64))  # 64 символа
    # Убедимся, что local не начинается/заканчивается '.', нет '..'
    while local_max.startswith('.') or local_max.endswith('.') or '..' in local_max:
        local_max = ''.join(random.choice(local_allowed) for _ in range(64))
    
    label_max = ''.join(random.choice(domain_allowed) for _ in range(63))  # 63 в лейбле
    # Дефис не в начале/конце
    while label_max.startswith('-') or label_max.endswith('-'):
        label_max = ''.join(random.choice(domain_allowed) for _ in range(63))
    
    domain_max = label_max + '.' + "com"  # Чтобы уложиться в общую длину
    max_email = local_max + '@' + domain_max
    # Обрезаем, если >254 (но в этом случае должно быть ок: 64 + 1 + 63 + 1 + 3 = 132, но можно удлинить domain
    # Для точного 254: подкорректируем domain
    needed_domain_len = 254 - len(local_max) - 1  # -1 for @
    labels = []
    while needed_domain_len > 0:
        label_len = min(63, needed_domain_len - 1)  # -1 for '.'
        label = ''.join(random.choice(domain_allowed) for _ in range(label_len))
        while label.startswith('-') or label.endswith('-'):
            label = ''.join(random.choice(domain_allowed) for _ in range(label_len))
        labels.append(label)
        needed_domain_len -= label_len + 1
    domain_max = '.'.join(labels)
    if needed_domain_len < 0:  # Корректировка
        domain_max = domain_max[:254 - len(local_max) - 1]
    max_email = local_max + '@' + domain_max
    test_cases.append((max_email, "Позитив: максимальная длина (64 local, 63 label, ~254 total)", True))
    
    # Негативные кейсы
    # 1. Без @
    no_at = "user.example.com"
    test_cases.append((no_at, "Негатив: без @", False))
    
    # 2. Более одного @
    multi_at = "user@domain@com"
    test_cases.append((multi_at, "Негатив: более одного @", False))
    
    # 3. Точка в начале local
    dot_start = ".user@domain.com"
    test_cases.append((dot_start, "Негатив: точка в начале local-part", False))
    
    # 4. Точка в конце local
    dot_end = "user.@domain.com"
    test_cases.append((dot_end, "Негатив: точка в конце local-part", False))
    
    # 5. Две точки подряд в local
    double_dot = "user..name@domain.com"
    test_cases.append((double_dot, "Негатив: две точки подряд в local-part", False))
    
    # 6. Дефис в начале домена
    hyphen_start = "user@-domain.com"
    test_cases.append((hyphen_start, "Негатив: дефис в начале доменного лейбла", False))
    
    # 7. 65 символов в local
    local_over = ''.join(random.choice(local_allowed) for _ in range(65))
    over_local = local_over + "@domain.com"
    test_cases.append((over_local, "Негатив: 65 символов в local-part (превышение 64)", False))
    
    # 8. 64 символа в лейбле домена
    label_over = ''.join(random.choice(domain_allowed) for _ in range(64))
    over_label = "user@" + label_over + ".com"
    test_cases.append((over_label, "Негатив: 64 символа в доменном лейбле (превышение 63)", False))
    
    # 9. Пустое поле
    empty = ""
    test_cases.append((empty, "Негатив: пустое поле", False))
    
    # 10. Пробелы
    spaces = " user@domain.com "
    test_cases.append((spaces, "Негатив: пробелы вокруг (или внутри, но здесь вокруг)", False))
    
    # 11. Недопустимый спецсимвол (например, / в domain, но / allowed в local)
    invalid_char = "user@domain/com"
    test_cases.append((invalid_char, "Негатив: недопустимый символ в domain (/)", False))
    
    # Unicode (опционально)
    if include_unicode:
        unicode_email = "пользователь@домен.рф"
        test_cases.append((unicode_email, "Позитив/Негатив: Unicode (RFC 6531, зависит от поддержки)", True))  # Может быть валидным или нет
    
    return test_cases

if __name__ == "__main__":
    emails = generate_test_emails(include_unicode=True)  # Включи Unicode для полноты
    for i, (email, desc, is_valid) in enumerate(emails, 1):
        validity = "Валидный" if is_valid else "Инвалидный"
        print(f"{i}. {email}\n   {desc} ({validity})\n")
