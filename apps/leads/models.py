import uuid
from django.db import models
from apps.core.models import BaseModel


class Lead(BaseModel):
    """
    Modelo para armazenar leads capturados pela landing page com coleta mínima de dados.
    Herda created_at e updated_at de BaseModel.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, default='')
    message = models.TextField(max_length=2000, blank=True, default='')
    privacy_accepted = models.BooleanField(default=False)
    privacy_policy_version = models.CharField(max_length=32, blank=True, default='')

    class Meta:
        db_table = 'leads'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"
