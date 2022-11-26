from Bot.Detector.NSFW.detection import check_message_to_nsfw
import numpy as np


class ViolationRules:
    def __init__(self, model, reactions: str, violation_name: str):
        self.model = model
        reactions_array = reactions.split(',')
        assert len(reactions_array) == 3
        self.need_delete = bool(int(reactions_array[0]))
        self.need_mute_user = bool(int(reactions_array[1]))
        self.need_ban_user = bool(int(reactions_array[2]))
        self.violation_name = violation_name

    def check_violation(self, message: str) -> tuple:
        if self.model is None:
            return (self.is_all_restricts(),
                    [self.need_delete, self.need_mute_user, self.need_ban_user])
        if self.model.predict(message) == 1:
            return (self.is_all_restricts(),
                    [self.need_delete, self.need_mute_user, self.need_ban_user])
        else:
            return 0, [0, 0, 0]

    def is_check_is_not_needed(self) -> bool:
        return self.need_delete + self.need_ban_user + self.need_mute_user == 0

    def is_all_restricts(self) -> bool:
        return self.need_delete + self.need_ban_user + self.need_mute_user == 3

    def show_settings(self) -> str:
        return self.violation_name + ': ' + ' '.join(str(setting) for setting in [self.need_delete,
                                                                                  self.need_mute_user,
                                                                                  self.need_ban_user])

    def get_str(self):
        return ','.join(str(action) for action in [int(self.need_delete),
                                                   int(self.need_mute_user),
                                                   int(self.need_ban_user)])


class ChatRules:
    def __init__(self, obscenity_model, offense_model, threat_model,
                 on_obscenity: str, on_offense: str, on_threat: str, on_other_violation: str):
        self.on_obscenity = ViolationRules(obscenity_model, on_obscenity, 'Ругательства/Непристойность')
        self.on_offense = ViolationRules(offense_model, on_offense, 'Оскорбления')
        self.on_threat = ViolationRules(threat_model, on_threat, 'Угроза')
        self.on_other_violation = ViolationRules(None, on_other_violation, 'Другие нарушения')

    def check_violation(self, message: str) -> np.ndarray:
        if not check_message_to_nsfw(message):
            return np.array([0, 0, 0])
        reactions = []
        for violation_rule in [self.on_threat, self.on_offense,
                               self.on_obscenity, self.on_other_violation]:
            is_all_restricts, reactions_ = violation_rule.check_violation(message)
            if is_all_restricts:
                return np.array([1, 1, 1])

            reactions.append(reactions_)
        return np.array(reactions).sum(axis=0) > 0

    def show_settings(self) -> str:
        preview_message = 'Текущие настройки бота для чата.\nСлева выведено нарушение, ' \
                          'справа варианты реагирования на нарушение: удаление сообщения, мут на 30 секунд, удаление ' \
                          'из чата.\n' \
                          'True означает, что данное действие применяется, False - что не применяется\n\n'
        return preview_message + '\n'.join(violation.show_settings()
                                           for violation in [self.on_threat, self.on_offense,
                                                             self.on_obscenity,
                                                             self.on_other_violation]) + "\n\n Чтобы установить " \
                                                                                         "настройки введите " \
                                                                                         "\'\'@violation_detect_bot " \
                                                                                         "Установить настройки для " \
                                                                                         "чата\'\' "

    def get_str_dict(self):
        return {'obscenity': self.on_obscenity.get_str(),
                'offense': self.on_offense.get_str(),
                'threat': self.on_threat.get_str(),
                'other': self.on_other_violation.get_str(),
                }

    def from_text(self, text: str):
        try:
            threat = text.split('Угроза:')[1].split('Оскорбления')[0]
            insult = text.split('Оскорбления:')[1].split('Ругательства')[0]
            obscenity = text.split('Ругательства/Непристойность:')[1].split('Другие нарушения')[0]
            other = text.split('Другие нарушения:')[1]
            for violation in [threat, insult, obscenity, other]:
                parameters = violation.strip().split(' ')
                if violation == other:
                    parameters = parameters[:3]
                assert len(parameters) == 3
                parameters_int = []
                for parameter in parameters:
                    if parameter == 'True':
                        parameters_int.append('1')
                    else:
                        parameters_int.append('0')
                result_parameters = ','.join(parameters_int)
                if violation == threat:
                    self.on_threat = ViolationRules(self.on_threat.model, result_parameters, 'Угроза')
                if violation == obscenity:
                    self.on_obscenity = ViolationRules(self.on_obscenity.model, result_parameters, 'Ругательства/Непристойность')
                if violation == insult:
                    self.on_offense = ViolationRules(self.on_offense.model, result_parameters, 'Оскорбления')
                if violation == other:
                    self.on_other_violation = ViolationRules(self.on_other_violation.model, result_parameters, 'Другие нарушения')
            return 1
        except Exception as e:
            print(e)
            return 0
