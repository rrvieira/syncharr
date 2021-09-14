import telegram


class TelegramNotification:
    __MESSAGE_TITLE = """<b>Syncharr - Sync {sync_result}</b>
Media: <code>{media}</code>
Sub: <code>{sub}</code>"""

    __MESSAGE_RESULT_TEMPLATE = """

Sync by: <code>{tool_name}</code>
Reference: <code>{reference}</code>
Time taken: <code>{time_consumed}s</code>
Success: <code>{success}</code>"""

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

    def notify(self, sync_executor_result):
        if self.telegram_bot is None:
            self.logger.warning("Notification to telegram not triggered. Telegram bot is none.")
            return

        msg = self.__build_message(sync_executor_result)
        self.telegram_bot.sendMessage(chat_id=self.telegram_chat_id, text=msg, parse_mode=telegram.ParseMode.HTML)
        self.logger.info("Telegram notification sent to user:\n{}".format(msg))

    def __build_message(self, sync_executor_result):
        sub_lang = sync_executor_result.sub_language()
        if sub_lang is None:
            sub_lang = sync_executor_result.original_sub_file_path()

        message = self.__MESSAGE_TITLE.format(
            sync_result=self.__get_sync_executor_result_text(sync_executor_result.was_success()),
            media=sync_executor_result.media_file_path(),
            sub=sub_lang)

        for sync_result in sync_executor_result.sync_result_list:
            message += self.__MESSAGE_RESULT_TEMPLATE.format(
                tool_name=sync_result.sync_by_name,
                reference=sync_result.reference(),
                time_consumed=str(sync_result.time_consumed),
                success=str(self.__get_sync_result_emoji(sync_result.was_success())))

        return message

    @staticmethod
    def __get_sync_executor_result_text(was_success):
        if was_success:
            return "Success 🟢"
        else:
            return "Failed 🔴"

    @staticmethod
    def __get_sync_result_emoji(was_success):
        if was_success:
            return "✅"
        else:
            return "❌"
