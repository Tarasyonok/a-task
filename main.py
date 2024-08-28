from telegram.ext import Application, CommandHandler
from telegram import ReplyKeyboardRemove

from CMC_functions import get_crypto_name, get_crypto_price, get_cryptos_list

BOT_TOKEN = "6710941179:AAGdWRyFdmwGU7uoKNv_s1JZsDmke2RJRVQ"

RTL = 60  # частота опроса 60 секунд


async def start(update, context):
    await update.message.reply_text(
        "Я бот для отслеживания торгового значения криптовалют\n"
        "\n"
        "Для установки отслеживания введите такую команду:\n/tracker <cлаг криптовалюты> <min торг. знач.> <max торг. знач.>\n"
        "Пример: /tracker bitcoin 63350.35 63350.87\n"
        "\n"
        "Вы можете получить список криптовалют с их слагами с помощью команды /cryptos_list")


async def help_info(update, context):
    await update.message.reply_text(
        "Для установки отслеживания введите такую команду:\n/tracker <cлаг криптовалюты> <min торг. знач.> <max торг. знач.>\n"
        "Пример: /tracker bitcoin 63350.35 63350.87\n"
        "\n"
        "Вы можете получить список криптовалют с их слагами с помощью команды /cryptos_list")


async def cryptos_list(update, context):
    text = "Название | Слаг | Текущая стоимость($)\n\n"
    for c in get_cryptos_list():
        text += f"{c[0]} | {c[1]} | {c[2]}\n"
    await update.message.reply_text(
        text
    )


async def task(context):
    """Выводит сообщение"""
    crypto_slug = context.job.data[0]
    min_price = context.job.data[1]
    max_price = context.job.data[2]
    price = get_crypto_price(crypto_slug)
    if price <= min_price or price >= max_price:
        if price <= min_price:
            word = 'МИНИМАЛЬНОГО'
        else:
            word = 'МАКСИМАЛЬНОГО'
        await context.bot.send_message(context.job.chat_id, text=f'BEEP. Криптовалюта {get_crypto_name(crypto_slug)} достигла {word} торгового значения. Стоимость: {price}')
        remove_job_if_exists(crypto_slug, context)


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id

    if context.args:
        try:
            crypto_slug = context.args[0]
            min_price = float(context.args[1].replace(',', '.'))
            max_price = float(context.args[2].replace(',', '.'))
            if max_price <= min_price:
                await update.effective_message.reply_text('Минимальное торговое значение должно быть меньше, чем максимальное')
                return
            # Проверяем, что можно узнать стоимость этой криптовалюты
            get_crypto_price(crypto_slug)
        except IndexError:
            text = 'Укажите слаг криптовалюты, минимальное и максимальное торговые значения после /'
        except ValueError:
            text = 'Минимальное и максимальное торговые значения должны быть числами с плавающей запятой'
        except Exception as e:
            text = str(e)
        else:
            context.job_queue.run_repeating(task, RTL, chat_id=chat_id, name=crypto_slug, data=[crypto_slug, min_price, max_price])
            text = f'Начал следить за валютой: {get_crypto_name(crypto_slug)}'
    else:
        text = 'Укажите слаг криптовалюты, минимальное и максимальное торговые значения после /'

    await update.effective_message.reply_text(text)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_info))
    application.add_handler(CommandHandler("cryptos_list", cryptos_list))
    application.add_handler(CommandHandler("tracker", set_timer))
    application.run_polling()


if __name__ == '__main__':
    main()
