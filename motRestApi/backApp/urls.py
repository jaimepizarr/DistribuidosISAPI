from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LocalKmViewSet, LocalLoginView, LocalRegistrationView, MotToAssignView, MotorizadoUserView, MotorizadoView, OperadorRetrieveView, OrderCommentsView, SuperUser, UserRetrieveView, UserSignUp,OrderRetrieveView

from .views import UserSignUp, get_models
from backApp import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("mot_user",MotorizadoUserView)
router.register("orders",OrderRetrieveView)
router.register("mot_to_assign",MotToAssignView)
router.register("user",UserRetrieveView)
router.register("operadores",OperadorRetrieveView)
router.register("order/comments",OrderCommentsView)
router.register(r"local/precios/porKm",LocalKmViewSet)



urlpatterns = [
    path('user_exists',views.user_exists),
    path('user/register',UserSignUp.as_view()),
    path('user/<int:id>',UserSignUp.as_view()),
    path('user_admin/reg',SuperUser.as_view()),
    path('motorizado',MotorizadoView.as_view()),
    path('motorizado/<int:id>',views.upd_mot),
    path('user/login',TokenObtainPairView.as_view()),
    path('user/refresh',TokenRefreshView.as_view()),
    path('vehicle',views.getvehiclesbymot),
    path('vehicle/colors', views.get_colors),
    path('vehicle/type', views.get_type),
    path('vehicle/models', views.get_models),
    #path('motorizado/all', views.get_motorizados),
    # path('motorizado/update', views.update_motorizado),
    path('local',LocalRegistrationView.as_view()),
    path('local/<int:id>',LocalRegistrationView.as_view()),
    path('local/login',LocalLoginView.as_view()),
    #path('order/all', views.get_orders),
    path('',include(router.urls)),
    path('order/create/',views.post_order),
    path('order/assign/<int:id>',views.assign_order),
    path('order/motorizado', views.get_motorizado_order),
    path('order/statechange/<int:id>',views.change_data_order),
    path('order/change/<int:id>',views.change_data_order),
    path('order/revoke/<int:id>',views.revoke_order),
    path('order/state',views.get_order_state),
    path('order_by_mot/active/<int:id>',views.get_mot_orders_active),
    path('order_by_mot/assigned/<int:id>',views.get_mot_orders_assigned),
    path('order_by_mot/finished/<int:id>',views.get_mot_orders_finished),
    path("order_hist_by_mot/<int:id>",views.get_mot_orders),
    path('order/accept/<int:id>',views.accept_order),
    path('order/reject/<int:id>',views.reject_order),
    path('order/count_by_mot/<int:id>',views.count_by_mot),
    path('orders_by_date', views.orders_by_dates),
    path('order/location/<int:id>',views.get_mot_location),
    path('motdevice/register', views.register_motdevice),
    path('local/precios/porSectores', views.MapView.as_view()),
    path('local/precios/porSectores/<str:id>', views.getSectorByLocal),
    path('local/precios/porKm', views.postLocalKm),
    path('local/precios/porKm/<str:id>', views.updateLocalKm),
    path('local/sector', views.deleteSector),
    #path('getDistance', views.get_distance)
    path('user/data/comments/<int:id>', views.UserComments.as_view()),
    path('motorizado/unactivate/<int:id>', views.unactivate_mot),
    path('motorizado/activate/<int:id>', views.activate_mot),
]
