import uuid
from django.db import models
from apps.core.models import BaseModel


class Lead(BaseModel):
    """
    Modelo para armazenar leads capturados pela landing page.
    Herda created_at e updated_at de BaseModel.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    class Meta:
        db_table = 'leads'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"
