from decimal import Decimal
from .models import Apiary, Hive, HiveComponent
from rest_framework import serializers


class ApiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Apiary
        fields = ['id', 'name', 'latitude', 'longitude', 'description', 'owner']

    # products_count = serializers.IntegerField(read_only=True)

class HiveComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiveComponent
        fields = ['type']


class HiveSerializer(serializers.ModelSerializer):
    components = serializers.SerializerMethodField(method_name='get_components')

    component_types = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Hive
        fields = ['id', 'name', 'description', 'components', 'component_types']

    #### REMEMBER!!! when sending an object to the server you must use "component_types"!!!!!
    
    def get_components(self, obj):
        return [component.type for component in obj.components.all()]
    
    def create(self, validated_data):
        component_types = validated_data.pop('component_types', [])
        apiary_id = self.context['apiary_id']
        print(f'apiary id =  {apiary_id}')

        hive = Hive.objects.create(apiary_id=apiary_id, **validated_data)
        
        for component_type in component_types:
            try:
                component = HiveComponent.objects.get(type=component_type)
                hive.components.add(component)
            except HiveComponent.DoesNotExist:
                raise serializers.ValidationError(f"Invalid component type: {component_type}")
                    
        return hive

    def update(self, instance, validated_data):
    # Pop the components list from validated_data
        component_types = validated_data.pop('component_types', [])

        print(component_types)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Clear the existing components for the hive
        instance.components.clear()

        # Add the new components based on their textual representation
        for component_type in component_types:
            try:
                component = HiveComponent.objects.get(type=component_type)
                instance.components.add(component)
            except HiveComponent.DoesNotExist:
                raise serializers.ValidationError(f"Invalid component type: {component_type}")
                pass

        return instance






