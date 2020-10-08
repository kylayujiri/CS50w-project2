from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("create", views.create_listing, name="create-listing"),
    path("user/<str:username>", views.profile, name="profile"),
    path("user/<str:username>/watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>", views.listing, name="listing")
]
