import ssl

from django.core.mail.backends.smtp import EmailBackend


class BrevoSMTPBackend(EmailBackend):
    """SMTP backend compatible with Brevo relay cert mismatch on Render.

    Some deployments (including Render behind certain proxies) fail hostname
    validation during STARTTLS even when the Brevo endpoint is correct. This
    backend disables hostname/certificate verification for the SMTP connection so
    the registration security code is actually delivered instead of failing at the
    TLS handshake.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
