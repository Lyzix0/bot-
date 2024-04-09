import datetime

import yaml

with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

dates = {
    '1 день': datetime.timedelta(days=1),
    '1 месяц': datetime.timedelta(days=30),
    '2 месяца': datetime.timedelta(days=61),
    '3 месяца': datetime.timedelta(days=92),
    '1 год': datetime.timedelta(days=365),
    'Пожизненно': datetime.timedelta(days=10000)}


def format_notification(username, period):
    notification_text = (f"\n"
                         f"🎉 Уведомление о подписке 🎉\n"
                         f"\n"
                         f"Поздравляем, {username}!\n"
                         f"\n"
                         f"Вы успешно подписались на наш сервис прогнозов ставок на спорт! 🚀\n"
                         f"\n"
                         f"📆 Срок подписки: {period.lower()}\n"
                         f"\n"
                         f"Что вас ждет в течение подписки:\n"
                         f"\n"
                         f"✅ Ежедневные точные прогнозы на самые горячие события!\n"
                         f"✅ Эксклюзивные аналитические материалы и статистика!\n"
                         f"✅ Поддержка от наших профессиональных аналитиков!\n"
                         f"\n"
                         f"Спасибо за выбор нашего сервиса. Мы гарантируем вам захватывающее путешествие по миру "
                         f"ставок на спорт и надежные прогнозы для вашего успеха! 🏆\n"
                         f"\n"
                         f"Удачи и больших выигрышей! 💵🥇")

    return notification_text
