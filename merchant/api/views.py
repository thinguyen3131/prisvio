from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from merchant.models import Merchant
from .serializers import MerchantSerializer
from rest_framework.permissions import IsAuthenticated
from prisvio.permissions import IsAdminUserOrReadOnly, IsBusinessAdminOrAdmin, CanDeleteMerchant

class MerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [IsAuthenticated, IsBusinessAdminOrAdmin]

    def perform_create(self, serializer):
        # Check if the user already has a merchant
        user = self.request.user
        if user.merchants.exists():
            # Return a 400 Bad Request response if the user already has a merchant
            return Response({'detail': 'You already have a merchant.'}, status=status.HTTP_400_BAD_REQUEST)

        # Continue with the default creation process if the user doesn't have a merchant
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        # Check if the user already has a merchant
        user = self.request.user
        if not user.merchants.exists():
            return Response({'detail': 'You do not have a merchant to update.'}, status=status.HTTP_400_BAD_REQUEST)

        # update merchant
        serializer.save()
    
    @action(detail=True, methods=['DELETE'])
    @permission_classes([CanDeleteMerchant])  # Use custom permission for delete action
    def delete_merchant(self, request, pk=None):
        merchant = self.get_object()
        merchant.delete()
        return Response({'detail': 'Merchant deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)