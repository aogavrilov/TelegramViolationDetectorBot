import datetime

from aiogram.types import ChatPermissions
from Bot.Infrastructure.DataBase.commands import write_incident, update_message_is_deleted_status


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
                                 delete_messages: bool = False,
                                 restrict_reason: str = "NSFW") -> None:
        Compare different actions to violation

        """
        self.connection = connection
        self.bot = bot
        self.chat_id = chat_id

    async def _mute_user(self, user_id: int,
                         restrict_reason: str,
                         time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(minutes=1),
                         incident_proofs: str = "None") -> None:
        """Block opportunity to send messages for time interval to chat"""
        new_permissions = ChatPermissions(can_send_messages=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)
        write_incident(self.connection,
                       self.chat_id,
                       user_id,
                       applied_action="Mute user",
                       incident_type=restrict_reason,
                       incident_proofs=incident_proofs)  # todo append incident_proofs

    async def _kick_user(self, user_id: int, restrict_reason: str, incident_proofs: str = "None") -> None:
        """Kick user from chat and add him to black list"""
        await self.bot.kick_chat_member(user_id)
        write_incident(self.connection,
                       self.chat_id,
                       user_id,
                       applied_action="Kick",
                       incident_type=restrict_reason,
                       incident_proofs=incident_proofs)  # todo append incident_proofs

    async def _delete_messages(self, message_ids: [], restrict_reason: str, incident_proofs: str = "None") -> None:
        """Delete messages from chat"""
        try:
            for message_id in message_ids:
                await self.bot.delete_message(self.chat_id, message_id)
                update_message_is_deleted_status(connection=self.connection, chat_id=self.chat_id, message_id=message_id, is_deleted=1)
            write_incident(self.connection,
                           self.chat_id,
                           user_id=-1,
                           applied_action="Delete Messages",
                           incident_type=restrict_reason,
                           incident_proofs=incident_proofs)
        except Exception as e:
            write_incident(self.connection,
                           self.chat_id,
                           user_id=-1,
                           applied_action="Try to Delete Message, but got exception: " + str(e),
                           incident_type=restrict_reason,
                           incident_proofs=incident_proofs)


    async def _ban_sending_media(self, user_id: int,
                                 restrict_reason: str,
                                 time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(
                                     minutes=1), incident_proofs: str = "None") -> None:
        """Block opportunity to send media to chat"""
        new_permissions = ChatPermissions(can_send_media_messages=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)
        write_incident(self.connection,
                       self.chat_id,
                       user_id,
                       applied_action="Ban sending media",
                       incident_type=restrict_reason,
                       incident_proofs=incident_proofs)

    async def _ban_sending_stickers(self, user_id: int,
                                    restrict_reason: str,
                                    time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(
                                        minutes=1), incident_proofs: str = "None") -> None:
        """Block opportunity to send stickers to chat"""
        new_permissions = ChatPermissions(can_send_other_messages=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)
        write_incident(self.connection,
                       self.chat_id,
                       user_id,
                       applied_action="Ban sending stickers",
                       incident_type=restrict_reason,
                       incident_proofs=incident_proofs)

    async def _ban_creating_polls(self, user_id: int,
                                  restrict_reason: str,
                                  time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(
                                      minutes=1), incident_proofs: str = "None") -> None:
        """Block opportunity to create polls to chat"""
        new_permissions = ChatPermissions(can_send_polls=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)
        write_incident(self.connection,
                       self.chat_id,
                       user_id,
                       applied_action="Ban creating polls",
                       incident_type=restrict_reason,
                       incident_proofs=incident_proofs)

    async def _ban_adding_chat_members(self, user_id: int,
                                       restrict_reason: str,
                                       time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(
                                           minutes=1), incident_proofs: str = "None") -> None:
        """Block opportunity to add new members to chat"""
        new_permissions = ChatPermissions(can_invite_users=False)
        await self.bot.restrict_chat_member(self.chat_id,
                                            user_id,
                                            permissions=new_permissions,
                                            until_date=time_before_restrictions_lift)
        write_incident(self.connection,
                       self.chat_id,
                       user_id,
                       applied_action="Ban adding new members",
                       incident_type=restrict_reason,
                       incident_proofs=incident_proofs)

    async def react_to_violation(self, user_id: int = None,
                                 messages: [] = None,
                                 time_before_restrictions_lift: datetime.timedelta = datetime.timedelta(minutes=1),
                                 kick_user: bool = False,
                                 mute_user: bool = False,
                                 ban_sending_media: bool = False,
                                 ban_sending_stickers: bool = False,
                                 ban_creating_polls: bool = False,
                                 ban_adding_chat_members: bool = False,
                                 delete_messages: bool = False,
                                 restrict_reason: str = "NSFW") -> None:
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
        :param restrict_reason: why implemented punishment
        :return: None
        """
        if messages is not None and delete_messages:
            await self._delete_messages(message_ids=messages,
                                        restrict_reason=restrict_reason,
                                        incident_proofs=', '.join(str(msg_id) for msg_id in messages))

        if user_id is not None and messages is not None:
            if kick_user:
                await self._kick_user(user_id=user_id,
                                      restrict_reason=restrict_reason,
                                      incident_proofs=', '.join(str(msg_id) for msg_id in messages))
            if mute_user:
                await self._mute_user(user_id=user_id,
                                      restrict_reason=restrict_reason,
                                      time_before_restrictions_lift=time_before_restrictions_lift,
                                      incident_proofs=', '.join(str(msg_id) for msg_id in messages))
            if ban_sending_media:
                await self._ban_sending_media(user_id=user_id,
                                              restrict_reason=restrict_reason,
                                              time_before_restrictions_lift=time_before_restrictions_lift,
                                              incident_proofs=', '.join(str(msg_id) for msg_id in messages))
            if ban_sending_stickers:
                await self._ban_sending_stickers(user_id=user_id,
                                                 restrict_reason=restrict_reason,
                                                 time_before_restrictions_lift=time_before_restrictions_lift,
                                                 incident_proofs=', '.join(str(msg_id) for msg_id in messages))
            if ban_creating_polls:
                await self._ban_creating_polls(user_id=user_id,
                                               restrict_reason=restrict_reason,
                                               time_before_restrictions_lift=time_before_restrictions_lift,
                                               incident_proofs=', '.join(str(msg_id) for msg_id in messages))
            if ban_adding_chat_members:
                await self._ban_adding_chat_members(user_id=user_id,
                                                    restrict_reason=restrict_reason,
                                                    time_before_restrictions_lift=time_before_restrictions_lift,
                                                    incident_proofs=', '.join(str(msg_id) for msg_id in messages))

        elif user_id is not None:
            if kick_user:
                await self._kick_user(user_id=user_id,
                                      restrict_reason=restrict_reason)
            if mute_user:
                await self._mute_user(user_id=user_id,
                                      restrict_reason=restrict_reason,
                                      time_before_restrictions_lift=time_before_restrictions_lift)
            if ban_sending_media:
                await self._ban_sending_media(user_id=user_id,
                                              restrict_reason=restrict_reason,
                                              time_before_restrictions_lift=time_before_restrictions_lift)
            if ban_sending_stickers:
                await self._ban_sending_stickers(user_id=user_id,
                                                 restrict_reason=restrict_reason,
                                                 time_before_restrictions_lift=time_before_restrictions_lift)
            if ban_creating_polls:
                await self._ban_creating_polls(user_id=user_id,
                                               restrict_reason=restrict_reason,
                                               time_before_restrictions_lift=time_before_restrictions_lift)
            if ban_adding_chat_members:
                await self._ban_adding_chat_members(user_id=user_id,
                                                    restrict_reason=restrict_reason,
                                                    time_before_restrictions_lift=time_before_restrictions_lift)