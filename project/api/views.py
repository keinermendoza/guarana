from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.utils import timezone as tz

from core.models import (
    Producto,
    # Produccion,
    Ralada,
    Venta,

)

from .serializers import (
    ProduccionSerializer
)

from .utils import (
    get_start_and_end_dates_from_year_and_month
)

class ProductionApiView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):

        year = self.request.query_params.get('year', tz.now().year)
        month = self.request.query_params.get('month', tz.now().month)
        
        procesamiento = Ralada.objects.peso_y_cantidades_procesadas_kpi(year=year, month=month)
        productos_elaborados = Producto.objects.produccion_al_mes_progress_chart(year=year, month=month)
        response = {
                "title":"Produtos Produzidos No Mes",
                "total_by_category": procesamiento,
                "total_by_product": productos_elaborados,
            }
    
        return Response(response, status=status.HTTP_200_OK)
    

    
class SalesApiView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):

        year = self.request.query_params.get('year', tz.now().year)
        month = self.request.query_params.get('month', tz.now().month)

        start, end = get_start_and_end_dates_from_year_and_month(year=int(year), month=int(month))

        kpi = Venta.objects.kpi_totales_por_metodo(start=start, end=end)
        total_quantity_monthly = Venta.get_proxied_cantidad_vendida_progress_chart(start=start, end=end)
        venta_mensual_productos = Venta.get_proxied_grafico_bar_montos_productos_vendidos_mensual(start=start, end=end)
        total_product_daily = Venta.objects.grafico_bar_metodos_de_pago_diario(start=start, end=end)

        # procesamiento = Ralada.objects.peso_y_cantidades_procesadas_kpi(year=year, month=month)
        # productos_elaborados = Producto.objects.produccion_al_mes_progress_chart(year=year, month=month)
        response = {
                # "table_context":produccion_serializer.data,
                # "main_graphic_bar_title": "Vendas Diarias Segum Metodo de Pago",
                "title":"Produtos Vendidos No Mes",
                "total_by_method": kpi,
                "total_product_monthly": venta_mensual_productos,
                "total_product_daily": total_product_daily,
                "total_quantity_monthly":total_quantity_monthly,
                # "sale_list":
            }
    
        return Response(response, status=status.HTTP_200_OK)


    # year = tz.now().year
    # month = tz.now().month
    
    # # this is like pagination
    # periodos = Periodo.objects.all() 
    # start, end = get_current_periodo_rango(request=request)
    # ventas = Venta.objects.filter(fecha_venta__range=[start, end])
    
    # # data para graficos
    # ventas_diaria_metodos = Venta.objects.grafico_bar_metodos_de_pago_diario(start=start, end=end)
    # fechas_venta_diaria = ventas_diaria_metodos.pop()
    # kpi = Venta.objects.kpi_totales_por_metodo(start=start, end=end)
    # producto_vendido = Producto.objects.cantidad_vendida_progress_chart(start=start, end=end)
    # venta_mensual_productos = VentaItem.objects.grafico_bar_montos_productos_vendidos_mensual(start=start, end=end)
    
    # navegation = get_home_navegation(request)
    
    # context = kwargs['context']
    # custom_template = kwargs['custom_template']

    # context.update(
    #     {
    #         "periodos":periodos,
    #         "current_periodo":start.strftime("%Y-%m-%d"),
    #         "table_template": table_template,
    #         "table_context":ventas,
    #         "navigation": navegation,
    #         "main_graphic_bar_title": "Monto de Ventas Diarias Segum Metodo de Pago",
    #         "kpi":kpi,
    #         "progress_section_title":"Produtos Vendidos por Quantidades",
    #         "progress": producto_vendido,
    #         "chart_diario": json.dumps(
    #             {
    #                 "labels": [*fechas_venta_diaria],
    #                 "datasets": ventas_diaria_metodos,
                    
    #             }
    #         ),
    #         "chart_mensual_title": f"Monto Vendido por Produto no mes",
    #         "chart_mensual": json.dumps(
    #             {
    #                 "labels": [f"Mes {month}"],
    #                 "datasets": venta_mensual_productos,
    #             }
    #         )
            
    #     },
    # )

class AvailableYearsApiView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):
        
        return Response({'years':Venta.get_available_years()}, status=status.HTTP_200_OK)
    

class AvailableMonthsApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        if year := self.request.query_params.get('year'):
            return Response({'months':Venta.get_available_months(year)}, status=status.HTTP_200_OK)
        return Response({'error':'there is no data associated to this month'}, status=status.HTTP_404_NOT_FOUND)