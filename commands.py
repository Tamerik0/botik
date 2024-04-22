import datetime
import random

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, MessageHandler, filters

from gpt import clear_history, push_message, get_start_message, set_provider, default_provider

start_markup = ReplyKeyboardMarkup([['/dice', '/timer']], one_time_keyboard=False, resize_keyboard=True)


async def start_command(update, context):
    user_id = update.effective_user.id
    msg = get_start_message(update.effective_user)
    push_message(user_id, 'user', '/start')
    push_message(user_id, 'assistant', msg)
    await update.message.reply_text(
        msg,
        reply_markup=start_markup
    )


async def help_command(update, context):
    await update.message.reply_text("Я просто чат с Тамерланом")


async def time_command(update, context):
    await update.message.reply_text(str(datetime.datetime.now().time()))


async def date_command(update, context):
    await update.message.reply_text(str(datetime.date.today()))


async def timer_task(context):
    await context.bot.send_message(context.job.chat_id, text=f'КУКУ! {context.job.data}c прошли!')


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update, context, timer_time, task):
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, timer_time, chat_id=chat_id, name=str(chat_id), data=timer_time)
    return job_removed


async def set_timer_command(update, context):
    try:
        timer_time = float(context.args[0])
    except:
        timer_time = 5.0
    job_removed = set_timer(update, context, timer_time, timer_task)
    text = f'Вернусь через {timer_time} с!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)


async def unset_timer_command(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


async def dice_command(update, context):
    markup = ReplyKeyboardMarkup([['кинуть один шестигранный кубик', 'кинуть 2 шестигранных кубика одновременно'],
                                  ['кинуть 20-гранный кубик', 'вернуться назад']], one_time_keyboard=False,
                                 resize_keyboard=True)
    await update.message.reply_text('.', reply_markup=markup)
    return 0


async def dice_handler(update, context):
    msg = update.message.text
    if msg == 'кинуть один шестигранный кубик':
        await update.message.reply_dice()
    elif msg == 'кинуть 2 шестигранных кубика одновременно':
        await update.message.reply_dice()
        await update.message.reply_dice()
    elif msg == 'кинуть 20-гранный кубик':
        await update.message.reply_text(str(random.randint(1, 20)))
    return 0


timer_markup = ReplyKeyboardMarkup([['30 секунд', '1 минута'],
                                    ['5 минут', 'вернуться назад']], one_time_keyboard=False,
                                   resize_keyboard=True)


async def timer_command(update, context):
    await update.message.reply_text('.', reply_markup=timer_markup)
    return 0


async def timer_task1(context):
    d = {60: '1 минута истекла', 300: '5 минут истекли'}
    await context.bot.send_message(context.job.chat_id, text=d.get(context.job.data, f'{context.job.data} с истекли'),
                                   reply_markup=timer_markup)


async def timer_handler(update, context):
    msg = update.message.text
    if msg == '30 секунд':
        set_timer(update, context, 30, timer_task1)
        await update.message.reply_text('Засек 30 с',
                                        reply_markup=ReplyKeyboardMarkup([['/close']], resize_keyboard=True)
                                        )
    elif msg == '1 минута':
        set_timer(update, context, 60, timer_task1)
        await update.message.reply_text('Засек 1 минуту',
                                        reply_markup=ReplyKeyboardMarkup([['/close']], resize_keyboard=True)
                                        )
    elif msg == '5 минут':
        set_timer(update, context, 300, timer_task1)
        await update.message.reply_text('Засек 5 минут',
                                        reply_markup=ReplyKeyboardMarkup([['/close']], resize_keyboard=True))
    elif msg == '/close':
        remove_job_if_exists(str(update.message.chat_id), context)
        await update.message.reply_text('.',
                                        reply_markup=timer_markup)
    return 0


async def go_back_handler_func(update, context):
    if update.message.text == 'вернуться назад':
        await update.message.reply_text('вернулись)',
                                        reply_markup=start_markup
                                        )
        return ConversationHandler.END
    return 0


async def new_dialog_command(update, context):
    user_id = update.effective_user.id
    clear_history(user_id)
    msg = get_start_message(update.effective_user)
    push_message(user_id, 'assistant', msg)
    await update.message.reply_text(msg)


async def set_provider_command(update, context):
    user_id = update.effective_user.id
    set_provider(user_id, context.args[0])
    await update.message.reply_text(f'Изменили провайдера на {context.args[0]}, по умолчанию {default_provider}')


go_back_handler = MessageHandler(filters.Text(['вернуться назад']), go_back_handler_func)
