from rest_framework import routers

from . import views as views_api


router = routers.DefaultRouter()
router.register('products', views_api.ProductViewSet)
router.register('tasks', views_api.TaskViewSet, basename='tasks')
router.register('supplier_accounts', views_api.SupplierAccountsViewSet)
router.register('order', views_api.OrderViewSet, basename='order')
router.register('users', views_api.UserViewSet)
router.register('groups', views_api.GroupViewSet)
router.register('orderstatus', views_api.StatusViewSet, basename='orderstatus')

app_name = 'api'
