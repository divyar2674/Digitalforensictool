from django.urls import path
from .views import get_timeline_data, start_investigation
from .views import export_csv
from .views import export_pdf
from .views import get_summary
from .views import export_summary_pdf

urlpatterns = [
    path('start-investigation/',start_investigation,name='start_investigation'),
    path('timeline/', get_timeline_data, name='get_timeline_data'),
    path('export_csv/', export_csv, name='export_csv'),
    path('export_pdf/', export_pdf, name='export_pdf'),
    path('summary/', get_summary, name='get_summary'),
     path('export_summary_pdf/', export_summary_pdf, name='export_summary_pdf'),
    ]