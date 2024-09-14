from .serializers import BookSerializer
from rest_framework import viewsets
from .models import Book

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
