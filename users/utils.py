import threading
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class EmailThread(threading.Thread):
    def __init__(self, subject, content, sender, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.content = content
        self.sender = sender
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            self.content,
            self.sender,
            self.recipient_list,
            fail_silently=False,
        )


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.id)
            + six.text_type(timestamp)
            + six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()
