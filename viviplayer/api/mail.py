from typing import Tuple
from django.core import mail
from django.core.mail import send_mail
import re

def sender(meetingName:int, meetingUrl: str, meetingPassword: str, mails: str) -> int:
    """

    Returns:
        int: The return value will be the number of successfully delivered messages (which can be 0 or 1 since it can only send one message).

    https://docs.djangoproject.com/en/3.2/topics/email/#send-mail
    """

    validMailList, invalidMailList = validateMail(mails)
    if invalidMailList:
        raise Exception("Invalide Mail: " + str(invalidMailList) + ".\nKein Mail wurde versand.")

    # TODO maybe use send_mass_mail
    try:
        returnCode = send_mail(
        'ViViPlayer Meeting Einladung',
        'Sie wurden in ein ViViPlayer Meeting  eingeladen.\n' +
        'Klicken Sie auf den Link und geben Sie bei Aufforderung das Passwort ein um beizutreten.\n\n' +
        "Passwort:\t" + meetingPassword + "\n" +
        "Link:\t" + meetingUrl + "\n",
        'djangotestmail@gmx.de',
        validMailList,
        fail_silently=False,
        )
    except Exception as e:
        raise e

def validateMail(mails: str) -> Tuple[list[str], list[str] ]:
    """Create list of emails from one single string of 0-n emails.
    Deletes invalid mails from list

    TODO notify user that some mail lists where ivalid
    """

    mailList = mails.split("\n")
    validMailList = []
    invalidMailList = []
    regexCriteria = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    for m in mailList:
        # append mail to valid list if length of mail adress ok and valid regex
        if len(m) >= 3 and  re.fullmatch(regexCriteria, m):
            validMailList.append(m)
        else:
            invalidMailList.append(m)
        
    return validMailList, invalidMailList
