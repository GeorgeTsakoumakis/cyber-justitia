from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Session(models.Model):
    """
    Session model to store chatbot sessions. Each session is associated with a user.
    Each session can contain multiple messages.
    """

    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        db_table = "sessions"

    session_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        return self.user.username + "_" + str(self.session_id)


class Message(models.Model):
    """
    Message model to store chatbot messages. Each message is associated with a session.
    A message can be from a user, the chatbot, or a system message.
    """

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        db_table = "messages"

    class Role(models.TextChoices):
        BOT = "bot", _("Bot")
        USER = "user", _("User")
        SYSTEM = "system", _("System")

    message_id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    text = models.TextField(_("message text"), max_length=1024)
    role = models.CharField(
        _("role"),
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role.capitalize()}: {self.text}"

    def clean(self):
        if self.role == self.Role.SYSTEM:
            raise ValidationError("System messages cannot be created directly.")
        if self.text.strip() == "":
            raise ValidationError("Message text cannot be empty or whitespace only.")
        if len(self.text) > 1024:
            raise ValidationError("Message text cannot exceed 1024 characters.")
        if self.role not in [choice[0] for choice in self.Role.choices]:
            raise ValidationError("Invalid message role.")
        if not self.session:
            raise ValidationError("Message must be associated with a session.")
