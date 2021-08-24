import telegram


class TelegramNotification:
    __MESSAGE_TEMPLATE = """<b>Syncharr - Sync Finished</b>
{time_consumed}

<b>Success:</b> <code>{success}</code>
<b>for ref language:</b> <code>{language}</code>
<b>and media:</b>
<code>{media}</code>
    """

    def __init__(self, telegram_user_token, telegram_chat_id, logger):
        self.telegram_user_token = telegram_user_token
        self.telegram_chat_id = telegram_chat_id
        self.logger = logger

        if telegram_user_token and telegram_chat_id:
            self.logger.info("Going to initialize telegram bot with provided telegram user token and chat id")
            self.telegram_bot = telegram.Bot(token=telegram_user_token)
        elif not telegram_user_token and not telegram_chat_id:
            self.telegram_bot = None
            self.logger.warning("Telegram bot not initialized. Telegram user token and chat id not provided")
        elif not telegram_user_token:
            self.telegram_bot = None
            self.logger.warning("Telegram bot not initialized. Telegram user token not provided")
        elif not telegram_chat_id:
            self.telegram_bot = None
            self.logger.warning("Telegram bot not initialized. Telegram chat id not provided")

    def notify(self, sync_result):
        if self.telegram_bot is None:
            self.logger.warning("Notification to telegram not triggered. Telegram bot is none.")
            return

        msg = self.__build_message(sync_result)
        self.telegram_bot.sendMessage(chat_id=self.telegram_chat_id, text=msg, parse_mode=telegram.ParseMode.HTML)
        self.logger.info("Telegram notification sent to user:\n{}".format(msg))

    def __build_message(self, sync_result):
        ref_lang = sync_result.sub_language()
        if ref_lang is None:
            ref_lang = sync_result.original_sub_file_path()

        return self.__MESSAGE_TEMPLATE.format(time_consumed=str(sync_result.time_consumed),
                                              success=str(sync_result.success),
                                              language=ref_lang,
                                              media=sync_result.media_file_path())
