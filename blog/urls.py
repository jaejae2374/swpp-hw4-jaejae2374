from django.urls import path
from blog import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('article/', views.ArticleCreateListView.as_view(), name='article_create_list'),
    path('article/<int:id>/', views.ArticleRetUptDelView.as_view(), name='article_retrieve_update_delete'),
    path('article/<int:id>/comment/', views.CommentCreateListView.as_view(), name='comment_create_list'),
    path('comment/<int:id>/', views.CommentRetUptDelView.as_view(), name='comment_retrieve_update_delete'),
    path('token/', views.token, name='token'),
]
