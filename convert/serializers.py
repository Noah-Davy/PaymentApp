from rest_framework import serializers


class CurrencySerializer(serializers.Serializer):
    currency1 = serializers.ChoiceField(choices=('EUR', 'USD', 'GBP'))
    currency2 = serializers.ChoiceField(choices=('EUR', 'USD', 'GBP'))
    amount = serializers.FloatField()
