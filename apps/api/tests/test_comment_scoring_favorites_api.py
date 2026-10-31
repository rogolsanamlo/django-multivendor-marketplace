from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser, Store
from apps.comment_scoring_favorites.models import (
    Comment,
    Favorite,
    Scoring,
)
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)


class CommentScoringFavoriteAPITest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09121111111",
            email="user@example.com",
            name="Test",
            family="User",
            password="test123",
        )

        self.other_user = CustomUser.objects.create_user(
            mobile_number="09122222222",
            email="other@example.com",
            name="Other",
            family="User",
            password="test123",
        )

        self.brand = Brand.objects.create(
            brand_title="Apple",
            slug="apple",
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile",
        )

        self.product = Product.objects.create(
            product_name="iPhone 15",
            brand=self.brand,
            slug="iphone-15",
            image_name="products/test.jpg",
            is_active=True,
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="Test Store",
            store_phone="09123333333",
            slug="test-store",
            is_active=True,
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=50000000,
            is_active=True,
        )

        self.comment_list_url = reverse(
            "api:comment-list"
        )

        self.score_list_url = reverse(
            "api:scoring-list"
        )

        self.favorite_list_url = reverse(
            "api:favorite-list"
        )

    def test_unauthenticated_cannot_create_comment(self):
        response = self.client.post(
            self.comment_list_url,
            {
                "store_product": self.store_product.id,
                "comment_text": "Great product",
            },
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_unauthenticated_cannot_create_score(self):
        response = self.client.post(
            self.score_list_url,
            {
                "store_product": self.store_product.id,
                "score": 5,
            },
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_unauthenticated_cannot_create_favorite(self):
        response = self.client.post(
            self.favorite_list_url,
            {
                "store_product": self.store_product.id,
            },
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_authenticated_user_can_create_comment(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.comment_list_url,
            {
                "store_product": self.store_product.id,
                "comment_text": "Great product",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["commenting_user"],
            self.user.id,
        )

    def test_comment_user_cannot_be_forged(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.comment_list_url,
            {
                "store_product": self.store_product.id,
                "commenting_user": self.other_user.id,
                "comment_text": "Fake user",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        comment = Comment.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            comment.commenting_user,
            self.user,
        )

    def test_empty_comment_is_rejected(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.comment_list_url,
            {
                "store_product": self.store_product.id,
                "comment_text": "   ",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_comment_can_be_read_by_authenticated_user(self):
        self.client.force_authenticate(
            user=self.user
        )

        comment = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="Good",
            is_active=True,
        )

        response = self.client.get(
            reverse(
                "api:comment-detail",
                kwargs={"pk": comment.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_inactive_comment_returns_404(self):
        self.client.force_authenticate(
            user=self.user
        )

        comment = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="Hidden",
            is_active=False,
        )

        response = self.client.get(
            reverse(
                "api:comment-detail",
                kwargs={"pk": comment.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_edit_other_users_comment(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        comment = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="Original",
            is_active=True,
        )

        response = self.client.patch(
            reverse(
                "api:comment-detail",
                kwargs={"pk": comment.pk},
            ),
            {
                "comment_text": "Hacked",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_cannot_delete_other_users_comment(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        comment = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="Original",
            is_active=True,
        )

        response = self.client.delete(
            reverse(
                "api:comment-detail",
                kwargs={"pk": comment.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_can_create_score(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.score_list_url,
            {
                "store_product": self.store_product.id,
                "score": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["scoring_user"],
            self.user.id,
        )

    def test_scoring_user_cannot_be_forged(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.score_list_url,
            {
                "store_product": self.store_product.id,
                "scoring_user": self.other_user.id,
                "score": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        score = Scoring.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            score.scoring_user,
            self.user,
        )

    def test_score_below_zero_is_rejected(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.score_list_url,
            {
                "store_product": self.store_product.id,
                "score": -1,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_score_above_five_is_rejected(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.score_list_url,
            {
                "store_product": self.store_product.id,
                "score": 6,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_can_update_own_score(self):
        self.client.force_authenticate(
            user=self.user
        )

        scoring = Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.user,
            score=3,
        )

        response = self.client.patch(
            reverse(
                "api:scoring-detail",
                kwargs={"pk": scoring.pk},
            ),
            {
                "score": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        scoring.refresh_from_db()

        self.assertEqual(
            scoring.score,
            5,
        )

    def test_user_cannot_update_other_users_score(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        scoring = Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.user,
            score=3,
        )

        response = self.client.patch(
            reverse(
                "api:scoring-detail",
                kwargs={"pk": scoring.pk},
            ),
            {
                "score": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_cannot_change_scoring_user(self):
        self.client.force_authenticate(
            user=self.user
        )

        scoring = Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.user,
            score=3,
        )

        response = self.client.patch(
            reverse(
                "api:scoring-detail",
                kwargs={"pk": scoring.pk},
            ),
            {
                "scoring_user": self.other_user.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        scoring.refresh_from_db()

        self.assertEqual(
            scoring.scoring_user,
            self.user,
        )

    def test_authenticated_user_can_create_favorite(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.favorite_list_url,
            {
                "store_product": self.store_product.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["favorite_user"],
            self.user.id,
        )

    def test_favorite_user_cannot_be_forged(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.favorite_list_url,
            {
                "store_product": self.store_product.id,
                "favorite_user": self.other_user.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        favorite = Favorite.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            favorite.favorite_user,
            self.user,
        )

    def test_duplicate_favorite_is_not_created(self):
        self.client.force_authenticate(
            user=self.user
        )

        Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        response = self.client.post(
            self.favorite_list_url,
            {
                "store_product": self.store_product.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            Favorite.objects.filter(
                store_product=self.store_product,
                favorite_user=self.user,
            ).count(),
            1,
        )

    def test_user_can_delete_own_favorite(self):
        self.client.force_authenticate(
            user=self.user
        )

        favorite = Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        response = self.client.delete(
            reverse(
                "api:favorite-detail",
                kwargs={"pk": favorite.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Favorite.objects.filter(
                pk=favorite.pk
            ).exists()
        )

    def test_user_cannot_delete_other_users_favorite(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        favorite = Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        response = self.client.delete(
            reverse(
                "api:favorite-detail",
                kwargs={"pk": favorite.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_score_zero_is_rejected(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.score_list_url,
            {
                "store_product": self.store_product.id,
                "score": 0,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_score_list_only_shows_own_scores(self):
        Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.user,
            score=4,
        )

        Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.other_user,
            score=2,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.score_list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["scoring_user"],
            self.user.id,
        )

    def test_user_cannot_read_other_users_score(self):
        scoring = Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.other_user,
            score=2,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            reverse(
                "api:scoring-detail",
                kwargs={"pk": scoring.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_editing_comment_text_resets_approval(self):
        self.client.force_authenticate(
            user=self.user
        )

        comment = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="Original",
            is_active=True,
        )

        response = self.client.patch(
            reverse(
                "api:comment-detail",
                kwargs={"pk": comment.pk},
            ),
            {
                "comment_text": "Changed text",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        comment.refresh_from_db()

        self.assertEqual(
            comment.comment_text,
            "Changed text",
        )

        self.assertFalse(comment.is_active)
        self.assertIsNone(comment.approving_user)

    def test_comment_list_can_filter_by_store_product(self):
        other_product = Product.objects.create(
            product_name="Galaxy",
            brand=self.brand,
            slug="galaxy",
            image_name="products/test2.jpg",
            is_active=True,
        )

        other_store_product = StoreProduct.objects.create(
            store=self.store,
            product=other_product,
            price=1000,
            is_active=True,
        )

        Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="A",
            is_active=True,
        )

        Comment.objects.create(
            store_product=other_store_product,
            commenting_user=self.user,
            comment_text="B",
            is_active=True,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.comment_list_url,
            {"store_product": self.store_product.id},
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["comment_text"],
            "A",
        )
