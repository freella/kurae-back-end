from .models import Lead


class LeadService:
    """
    Serviço com regras de negócio para o domínio de leads.
    """

    @staticmethod
    def create_lead(validated_data: dict) -> Lead:
        """
        Cria e retorna um novo lead com os dados validados.
        """
        return Lead.objects.create(**validated_data)
