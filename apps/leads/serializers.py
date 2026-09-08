from rest_framework import serializers
from .models import Lead


class LeadSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e leitura de leads.
    id e created_at são gerados automaticamente.
    """

    class Meta:
        model = Lead
        fields = ['id', 'name', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'name': {'min_length': 2}
        }
