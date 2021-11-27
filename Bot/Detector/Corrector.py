import datetime

from aiogram.types import ChatPermissions


class Corrector:
    def __init__(self, connection, bot, chat_id):
        """
        Class for implementing punishment on violation

        :param connection: connection to db
        :param bot: connection to bot
        :param chat_id: chat where will be implemented punishment

        Methods:
        --------
        react_to_violation(self, user_id: int = None,
                                 messages: [] = None,
                                 time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(minutes=1),
                                 kick_user: bool = False,
                                 mute_user: bool = False,
                                 ban_sending_media: bool = False,
                                 ban_sending_stickers: bool = False,
                                 ban_creating_polls: bool = False,
                                 ban_adding_chat_members: bool = False,
                                 delete_messages: bool = False) -> None:
        Compare different actions to violation

        """
        self.connection = connection
        self.bot = bot
        self.chat_id = chat_id

    async def _mute_user(self, user_id: int,
                         time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(minutes=1)) -> None:
        """Block opportunity to send messages for time interval to chat"""
        new_permissions = ChatPermissions(can_send_messages=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)

    async def _kick_user(self, user_id: int) -> None:
        """Kick user from chat and add him to black list"""
        await self.bot.kick_chat_member(user_id)

    async def _delete_messages(self, message_ids: []) -> None:
        """Delete messages from chat"""
        for message_id in message_ids:
            await self.bot.delete_message(self.chat_id, message_id)

    async def _ban_sending_media(self, user_id: int,
                                 time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(minutes=1)) -> None:
        """Block opportunity to send media to chat"""
        new_permissions = ChatPermissions(can_send_media_messages=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)

    async def _ban_sending_stickers(self, user_id: int,
                                    time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(minutes=1)) -> None:
        """Block opportunity to send stickers to chat"""
        new_permissions = ChatPermissions(can_send_other_messages=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)

    async def _ban_creating_polls(self, user_id: int,
                                  time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(minutes=1)) -> None:
        """Block opportunity to create polls to chat"""
        new_permissions = ChatPermissions(can_send_polls=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)

    async def _ban_adding_chat_members(self, user_id: int,
                                       time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(minutes=1)) -> None:
        """Block opportunity to add new members to chat"""
        new_permissions = ChatPermissions(can_invite_users=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)

    async def react_to_violation(self, user_id: int = None,
                                 messages: [] = None,
                                 time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(minutes=1),
                                 kick_user: bool = False,
                                 mute_user: bool = False,
                                 ban_sending_media: bool = False,
                                 ban_sending_stickers: bool = False,
                                 ban_creating_polls: bool = False,
                                 ban_adding_chat_members: bool = False,
                                 delete_messages: bool = False) -> None:
        """
        Method for multi reaction on violation.

        :param user_id: user to which implement punishment
        :param messages: messages ids which need to be deleted
        :param time_before_restrictions_lift: timedelta after which punishment will be removed
        :param kick_user: indicator is user need be kicked from chat
        :param mute_user: indicator is user need be muted at chat
        :param ban_sending_media: indicator is user need be muted for sending messages with media
        :param ban_sending_stickers: indicator is user need be muted for sending stickers
        :param ban_creating_polls: indicator is user need not be able to create polls
        :param ban_adding_chat_members: indicator is user need not be able to add members
        :param delete_messages: indicator is messages need be deleted
        :return: None
        """
        if messages is not None and delete_messages:
            self._delete_messages(message_ids=messages)
        if user_id is not None:
            if kick_user:
                self._kick_user(user_id=user_id)
            if mute_user:
                self._mute_user(user_id=user_id, time_before_restrictions_lift=time_before_restrictions_lift)
            if ban_sending_media:
                self._ban_sending_media(user_id=user_id, time_before_restrictions_lift=time_before_restrictions_lift)
            if ban_sending_stickers:
                self._ban_sending_stickers(user_id=user_id, time_before_restrictions_lift=time_before_restrictions_lift)
            if ban_creating_polls:
                self._ban_creating_polls(user_id=user_id, time_before_restrictions_lift=time_before_restrictions_lift)
            if ban_adding_chat_members:
                self._ban_adding_chat_members(user_id=user_id, time_before_restrictions_lift=time_before_restrictions_lift)
