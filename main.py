import logging

from telegram import Update
from telegram.ext import *

import db
from commands import *
from config import token
from gpt import user_prompt

logger = logging.getLogger(__name__)


def get_start_message(user):
    return rf"Привет @{user.username}! Я бот Тамерлана. Я отправляю все сообщения Тамерлану, а он своими руками печает ответы."


async def communicate(update: Update, context):
    try:
        ans = await user_prompt(update.effective_user.id, update.message.text)
        await update.message.reply_text(ans.content)
    except BaseException as ex:
        await update.message.reply_text(f'Произошла ошибка:{str(ex)}, попробуйте поменять провайдера')


async def logger_msg_handler(update, context):
    logfile = open('log.txt', 'a+', encoding='utf-8')
    logfile.write(f'{update.effective_message}\n')
    logfile.close()


def main():
    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters.ALL, logger_msg_handler), 1)
    application.add_handler(
        ConversationHandler(entry_points=[CommandHandler("dice", dice_command)],
                            states={0: [go_back_handler, MessageHandler(filters.ALL, dice_handler)]},
                            fallbacks=[]))
    application.add_handler(
        ConversationHandler(entry_points=[CommandHandler("timer", timer_command)],
                            states={0: [go_back_handler, MessageHandler(filters.ALL, timer_handler)]},
                            fallbacks=[]))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("date", date_command))
    application.add_handler(CommandHandler("set_timer", set_timer_command))
    application.add_handler(CommandHandler("unset_timer", unset_timer_command))
    application.add_handler(CommandHandler("new_dialog", new_dialog_command))
    application.add_handler(CommandHandler("set_provider", set_provider_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, communicate))
    application.run_polling()


if __name__ == '__main__':
    main()
