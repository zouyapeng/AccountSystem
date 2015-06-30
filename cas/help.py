# -*- coding: UTF-8 -*-
from django.conf import settings
from html2text import html2text
from django.core.mail import EmailMultiAlternatives
import pexpect

def send_mail(subject, message_body, message_html, from_email, to_email, custom_headers={}, attachments={}):
    if not message_body and not message_html:
        raise ValueError("邮件内容不能为空")

    if not message_body:
        message_body = html2text(message_html)
    message = {"subject": subject, "body": message_body, "from_email": from_email, "to": to_email}
    if attachments:
        message['attachments'] = attachments
    if custom_headers:
        message['headers'] = custom_headers
    msg = EmailMultiAlternatives(**message)
    if message_html:
        msg.attach_alternative(message_html, "text/html")
    msg.send()

