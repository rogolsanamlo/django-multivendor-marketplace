from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.accounts.models import CustomUser
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


class CommentModelTests(BaseAccountTest):

    def setUp(self):
        super().setUp()

        self.user2 = CustomUser.objects.create_user(
            mobile_number="09120000001",
            password="123456",
            name="Sara",
        )

        self.user2.is_active = True
        self.user2.save()

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
        )

    def test_create_comment(self):
        comment = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="عالی بود",
        )

        self.assertEqual(
            comment.comment_text,
            "عالی بود",
        )

        self.assertEqual(
            comment.store_product,
            self.store_product,
        )

        self.assertEqual(
            comment.commenting_user,
            self.user,
        )

    def test_comment_is_inactive_by_default(self):
        comment = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="عالی بود",
        )

        self.assertFalse(
            comment.is_active
        )

    def test_comment_reply(self):
        parent = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="نظر اصلی",
        )

        child = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user2,
            comment_text="پاسخ",
            comment_parent=parent,
        )

        self.assertEqual(
            child.comment_parent,
            parent,
        )

        self.assertIn(
            child,
            parent.comments_child.all(),
        )

    def test_comment_str(self):
        comment = Comment.objects.create(
            store_product=self.store_product,
            commenting_user=self.user,
            comment_text="عالی بود",
        )

        self.assertEqual(
            str(comment),
            f"{self.store_product}\t{self.user}",
        )


class ScoringModelTests(CommentModelTests):

    def test_create_score(self):
        score = Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.user,
            score=5,
        )

        self.assertEqual(
            score.score,
            5,
        )

        self.assertEqual(
            score.store_product,
            self.store_product,
        )

        self.assertEqual(
            score.scoring_user,
            self.user,
        )

    def test_score_must_be_between_1_and_5(self):
        for invalid in (0, 6):
            with self.assertRaises(ValidationError):
                Scoring(
                    store_product=self.store_product,
                    scoring_user=self.user,
                    score=invalid,
                ).full_clean()

        for valid in (1, 5):
            Scoring(
                store_product=self.store_product,
                scoring_user=self.user,
                score=valid,
            ).full_clean()

    def test_unique_score(self):
        Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.user,
            score=4,
        )

        with self.assertRaises(IntegrityError):
            Scoring.objects.create(
                store_product=self.store_product,
                scoring_user=self.user,
                score=3,
            )

    def test_score_str(self):
        score = Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.user,
            score=5,
        )

        self.assertEqual(
            str(score),
            f"{self.store_product} - {self.user}",
        )


class FavoriteModelTests(CommentModelTests):

    def test_add_favorite(self):
        favorite = Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        self.assertEqual(
            favorite.store_product,
            self.store_product,
        )

        self.assertEqual(
            favorite.favorite_user,
            self.user,
        )

    def test_unique_favorite(self):
        Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        with self.assertRaises(IntegrityError):
            Favorite.objects.create(
                store_product=self.store_product,
                favorite_user=self.user,
            )

    def test_favorite_str(self):
        favorite = Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        self.assertEqual(
            str(favorite),
            f"{self.store_product} - {self.user}",
        )