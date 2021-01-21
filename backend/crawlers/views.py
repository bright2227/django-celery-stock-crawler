from django.shortcuts import render
from rest_framework import views, status
from rest_framework.response import Response
from crawlers.serializers import ManyMonthSerializer
from crawlers.crawl_rev import request_month_revenue
from celery import shared_task


class CrawlMonthRevenueView(views.APIView):

    def post(self, request):
        
        serializers = ManyMonthSerializer(data = request.data)
        serializers.is_valid(raise_exception=True)
        month_dates = serializers.validated_data.pop('months', None)

        for mon_date in month_dates:
            request_month_revenue.delay(mon_date['year'], mon_date['month'], 'sii')
            request_month_revenue.delay(mon_date['year'], mon_date['month'], 'otc')


        return Response({'task': 'Crawl order is sent, please wait.'}, status=status.HTTP_202_ACCEPTED)
