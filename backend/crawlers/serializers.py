from rest_framework import serializers

class MonthSerializer(serializers.Serializer):
    month = serializers.IntegerField(max_value=12, min_value=1)
    year = serializers.IntegerField(max_value=2040, min_value=2000)

class ManyMonthSerializer(serializers.Serializer):
    months = MonthSerializer(many=True)


# {
#     "months": [ {"month": 12 , "year": 2018}, {"month": 11 , "year": 2018},  {"month": 10 , "year": 2018}, {"month": 9 , "year": 2018}, 
#              {"month": 8 , "year": 2018}, {"month": 7 , "year": 2018},  {"month": 6 , "year": 2018}, {"month": 5 , "year": 2018}
#     ]
# }
# {
#     "months": [ {"month": 12 , "year": 2018}, {"month": 11 , "year": 2018},  {"month": 10 , "year": 2018}, {"month": 9 , "year": 2018} ]
# }