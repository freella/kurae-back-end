from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .serializers import LeadSerializer
from .services import LeadService


class LeadCreateView(APIView):
    """
    POST /api/leads/ → Captura um lead enviado pelo formulário da landing page.

    Endpoint público (AllowAny) — não requer autenticação.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LeadSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error_details = {}
            for field, err_list in e.detail.items():
                if isinstance(err_list, list) and len(err_list) > 0:
                    error_details[field] = str(err_list[0])
                else:
                    error_details[field] = str(err_list)
                    
            return Response(
                {
                    "error": "Dados inválidos",
                    "details": error_details
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        lead = LeadService.create_lead(serializer.validated_data)
        return Response({"message": "Lead registrado com sucesso"}, status=status.HTTP_201_CREATED)
