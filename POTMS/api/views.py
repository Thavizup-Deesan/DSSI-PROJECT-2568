from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import MasterItems, Projects, Vendors
from .serializers import MasterItemSerializer, ProjectSerializer, VendorSerializer
import pandas as pd

def project_page_view(request):
    return render(request, 'S08_Master_Data.html')

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'project_code'
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    @action(detail=False, methods=['post'], url_path='import-excel')
    def import_excel(self, request, *args, **kwargs):
        file = request.FILES.get('importFile') 
        
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)
            
            required_columns = ['project_code', 'project_name', 'budget_total', 'status']
            if not all(col in df.columns for col in required_columns):
                return Response(
                    {'error': 'Missing required columns in Excel file'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            projects_to_update = []
            projects_to_create = []

            for index, row in df.iterrows():
                project_code = row['project_code']
                data = {
                    'project_name': row['project_name'],
                    'budget_total': row['budget_total'],
                    'status': row['status']
                }
                
                project = Projects.objects.filter(project_code=project_code).first()
                
                if project:
                    serializer = self.get_serializer(project, data=data, partial=True)
                else:
                    data['project_code'] = project_code
                    serializer = self.get_serializer(data=data)
                
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(
                        {'error': f'Error at row {index + 2}: {serializer.errors}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {'message': f'Successfully imported/updated {len(df)} projects.'}, 
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class VendorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Vendors.
    """
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer

class MasterItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Master Items.
    """
    queryset = MasterItems.objects.all()
    serializer_class = MasterItemSerializer
    lookup_field = 'item_code' 