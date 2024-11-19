from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone as tz

from core.models import (
    Producto,
    # Produccion,
    Ralada,
)

from .serializers import (
    ProduccionSerializer
)

class ProductionApiView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):

        year = self.request.query_params.get('year', tz.now().year)
        month = self.request.query_params.get('month', tz.now().month)
        year = 2024
        month = 8

        
        # produccion_query = Produccion.objects.filter(ralada__fecha_ralada__month=month, ralada__fecha_ralada__year=year)
        # produccion_serializer = ProduccionSerializer(produccion_query)
        procesamiento = Ralada.objects.peso_y_cantidades_procesadas_kpi(year=year, month=month)
        productos_elaborados = Producto.objects.produccion_al_mes_progress_chart(year=year, month=month)
        response = {
                # "table_context":produccion_serializer.data,
                # "main_graphic_bar_title": "Vendas Diarias Segum Metodo de Pago",
                "title":"Produtos Produzidos No Mes",
                "total_by_category": procesamiento,
                "total_by_product": productos_elaborados,
            }
    
        return Response(response, status=status.HTTP_200_OK)
