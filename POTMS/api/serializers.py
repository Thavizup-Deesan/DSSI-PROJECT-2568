from rest_framework import serializers
from .models import MasterItems, Projects, Vendors

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__' 

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors
        fields = '__all__'

class MasterItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterItems
        fields = '__all__'