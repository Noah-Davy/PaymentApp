from rest_framework.views import APIView
from rest_framework.response import Response
from convert.serializers import CurrencySerializer

conversion_rates = {
    'EUR': {'USD': 1.2, 'GBP': 0.9},
    'USD': {'EUR': 0.8, 'GBP': 0.75},
    'GBP': {'EUR': 1.1, 'USD': 1.33}
}


class CurrencyConverter(APIView):
    def get(self, request, currency1, currency2, amount):
        data = {'currency1': currency1, 'currency2': currency2, 'amount': amount}
        serializer = CurrencySerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        validated_data = serializer.validated_data

        if 'currency1' not in validated_data or 'currency2' not in validated_data:
            return Response({'error': 'Invalid currency, please change!'}, status=400)

        currency1 = validated_data['currency1']
        currency2 = validated_data['currency2']

        if currency1 not in conversion_rates or currency2 not in conversion_rates[currency1]:
            return Response({'error': 'Incorrect Conversion Rate!'}, status=404)

        conversion_rate = conversion_rates[validated_data['currency1']][validated_data['currency2']]
        converted_amount = float(validated_data['amount']) * conversion_rate

        return Response({'converted_amount': converted_amount})


"""
404 - Incorrect Conversion Rate
400 - Invalid Currency
200 - Accepted Currency
"""
