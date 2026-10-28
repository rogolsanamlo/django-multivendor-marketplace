from django.urls import reverse

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
from apps.tests.base import BaseAccountTest
from apps.accounts.models import CustomUser

class BaseCSFViewTest(BaseAccountTest):

    def setUp(self):
        super().setUp()

        self.user.is_active = True
        self.user.save()

        self.store.is_active = True
        self.store.save()

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            slug="samsung",
            image_name=self.create_test_image(),
        )

        self.group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile",
            image_name=self.create_test_image(),
        )

        self.product = Product.objects.create(
            product_name="Galaxy S25",
            brand=self.brand,
            slug="galaxy-s25",
            image_name=self.create_test_image(),
        )

        self.product.product_group.add(
            self.group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=20000000,
            is_active=True,
        )

        self.client.force_login(
            self.user
        )


class CommentViewTests(BaseCSFViewTest):

    def test_comment_view_get(self):
        response = self.client.get(
            reverse(
                "csf:create_comment",
                kwargs={
                    "slug": self.product.slug,
                },
            ),
            {
                "storeProductId": self.store_product.id,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "csf_app/partials/create_comment.html",
        )

        self.assertIn(
            "form",
            response.context,
        )

    def test_create_comment(self):
        response = self.client.post(
            reverse(
                "csf:create_comment",
                kwargs={
                    "slug": self.product.slug,
                },
            ),
            {
                "store_product_id": self.store_product.id,
                "comment_id": "",
                "comment_text": "محصول خوبی بود",
            },
        )

        self.assertEqual(
            Comment.objects.count(),
            1,
        )

        comment = Comment.objects.first()

        self.assertEqual(
            comment.comment_text,
            "محصول خوبی بود",
        )

        self.assertEqual(
            comment.commenting_user,
            self.user,
        )

        self.assertEqual(
            comment.store_product,
            self.store_product,
        )

        self.assertIsNone(
            comment.comment_parent
        )

        self.assertRedirects(
            response,
            reverse(
                "products:product_details",
                kwargs={
                    "pk": self.store_product.id,
                },
            ),
        )

    def test_create_reply_comment(self):
        parent = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="نظر اصلی",
        )

        response = self.client.post(
            reverse(
                "csf:create_comment",
                kwargs={
                    "slug": self.product.slug,
                },
            ),
            {
                "store_product_id": self.store_product.id,
                "comment_id": parent.id,
                "comment_text": "پاسخ من",
            },
        )

        self.assertEqual(
            Comment.objects.count(),
            2,
        )

        child = Comment.objects.exclude(
            id=parent.id
        ).first()

        self.assertEqual(
            child.comment_parent,
            parent,
        )

        self.assertEqual(
            child.comment_text,
            "پاسخ من",
        )

        self.assertRedirects(
            response,
            reverse(
                "products:product_details",
                kwargs={
                    "pk": self.store_product.id,
                },
            ),
        )


class ScoreViewTests(BaseCSFViewTest):

    def test_add_score(self):
        response = self.client.get(
            reverse(
                "csf:add_score"
            ),
            {
                "storeProductId": self.store_product.id,
                "score": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Scoring.objects.count(),
            1,
        )

        score = Scoring.objects.first()

        self.assertEqual(
            score.score,
            5,
        )

        self.assertEqual(
            score.scoring_user,
            self.user,
        )

        self.assertEqual(
            score.store_product,
            self.store_product,
        )

    def test_add_score_returns_new_average(self):
        response = self.client.get(
            reverse(
                "csf:add_score"
            ),
            {
                "storeProductId": self.store_product.id,
                "score": 4,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["average"],
            4.0,
        )

    def test_user_can_update_existing_score(self):
        Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.user,
            score=3,
        )

        response = self.client.get(
            reverse(
                "csf:add_score"
            ),
            {
                "storeProductId": self.store_product.id,
                "score": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Scoring.objects.count(),
            1,
        )

        score = Scoring.objects.first()

        self.assertEqual(
            score.score,
            5,
        )


class FavoriteViewTests(BaseCSFViewTest):

    def test_add_to_favorite(self):
        response = self.client.get(
            reverse(
                "csf:add_to_favorite"
            ),
            {
                "storeProductId": self.store_product.id,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Favorite.objects.count(),
            1,
        )

        favorite = Favorite.objects.first()

        self.assertEqual(
            favorite.favorite_user,
            self.user,
        )

        self.assertEqual(
            favorite.store_product,
            self.store_product,
        )

    def test_duplicate_favorite(self):
        Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        response = self.client.get(
            reverse(
                "csf:add_to_favorite"
            ),
            {
                "storeProductId": self.store_product.id,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Favorite.objects.count(),
            1,
        )

    def test_delete_from_favorite(self):
        Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        response = self.client.get(
            reverse(
                "csf:delete_from_favorite"
            ),
            {
                "storeProductId": self.store_product.id,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Favorite.objects.count(),
            0,
        )

    def test_delete_from_favorite_requires_login(self):
        Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        self.client.logout()

        response = self.client.get(
            reverse(
                "csf:delete_from_favorite"
            ),
            {
                "storeProductId": self.store_product.id,
            },
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            Favorite.objects.count(),
            1,
        )

    def test_delete_missing_favorite_does_not_crash(self):
        response = self.client.get(
            reverse(
                "csf:delete_from_favorite"
            ),
            {
                "storeProductId": self.store_product.id,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Favorite.objects.count(),
            0,
        )

    def test_user_cannot_delete_another_users_favorite(self):
        user2 = CustomUser.objects.create_user(
            mobile_number="09120000001",
            password="123456",
            name="Sara",
        )

        Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=user2,
        )

        self.client.get(
            reverse(
                "csf:delete_from_favorite"
            ),
            {
                "storeProductId": self.store_product.id,
            },
        )

        self.assertEqual(
            Favorite.objects.count(),
            1,
        )


class UserFavoriteViewTests(BaseCSFViewTest):

    def test_user_favorite_list(self):
        Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        response = self.client.get(
            reverse(
                "csf:user_favorite"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "csf_app/user_favorite.html",
        )

        self.assertContains(
            response,
            "Galaxy S25",
        )


class ProductPageCommentFormTests(BaseCSFViewTest):

    def product_url(self):
        return reverse(
            "products:product_details",
            kwargs={
                "pk": self.store_product.id,
            },
        )

    def test_product_page_comment_form_knows_the_product(self):
        response = self.client.get(self.product_url())

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            f'name="store_product_id" value="{self.store_product.id}"',
        )

    def test_comment_without_product_id_does_not_crash(self):
        response = self.client.post(
            reverse(
                "csf:create_comment",
                kwargs={"slug": self.product.slug},
            ),
            {
                "comment_id": "",
                "comment_text": "نظر بدون شناسه کالا",
            },
        )

        self.assertRedirects(
            response,
            reverse("main:index"),
            fetch_redirect_response=False,
        )

        self.assertEqual(Comment.objects.count(), 0)

    def test_empty_comment_text_returns_to_product_page(self):
        response = self.client.post(
            reverse(
                "csf:create_comment",
                kwargs={"slug": self.product.slug},
            ),
            {
                "store_product_id": self.store_product.id,
                "comment_id": "",
                "comment_text": "",
            },
        )

        self.assertRedirects(
            response,
            self.product_url(),
            fetch_redirect_response=False,
        )

        self.assertEqual(Comment.objects.count(), 0)

    def test_product_page_buttons_work_and_are_persian(self):
        response = self.client.get(self.product_url())

        self.assertContains(
            response,
            f"addTofavorites({self.store_product.id})",
        )

        self.assertContains(
            response,
            f"addToCompareList({self.store_product.id})",
        )

        self.assertNotContains(response, 'title="Wishlist"')
        self.assertNotContains(response, 'title="Compare"')

    def test_rating_stars_follow_the_average_score(self):
        self.assertEqual(
            self.store_product.rating_stars,
            [False, False, False, False, False],
        )

        Scoring.objects.create(
            scoring_user=self.user,
            store_product=self.store_product,
            score=3,
        )

        self.assertEqual(
            self.store_product.rating_stars,
            [True, True, True, False, False],
        )

    def test_user_who_already_scored_can_still_change_the_score(self):
        Scoring.objects.create(
            scoring_user=self.user,
            store_product=self.store_product,
            score=3,
        )

        self.client.force_login(self.user)

        html = self.client.get(self.product_url()).content.decode()

        # all five stars stay clickable, the first three are highlighted
        self.assertEqual(html.count('onclick="addScore('), 5)
        self.assertEqual(
            html.count('class="fa fa-star cursor-pointer checked"'),
            3,
        )

    def test_user_without_score_sees_five_clickable_stars(self):
        self.client.force_login(self.user)

        html = self.client.get(self.product_url()).content.decode()

        self.assertEqual(html.count('onclick="addScore('), 5)
        self.assertEqual(html.count('cursor-pointer checked'), 0)

    def test_comments_count_counts_only_approved_comments(self):
        Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="approved",
            is_active=True,
        )

        Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="pending",
            is_active=False,
        )

        self.assertEqual(self.store_product.comments_count, 1)

        response = self.client.get(self.product_url())

        self.assertContains(
            response,
            '<a href="#tab-reviews">1</a>',
        )
