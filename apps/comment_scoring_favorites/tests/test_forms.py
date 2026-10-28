from django.test import TestCase

from apps.comment_scoring_favorites.forms import CommentForm


class CommentFormTests(TestCase):

    def test_valid_form(self):

        form = CommentForm(
            data={
                "store_product_id": "1",
                "comment_id": "",
                "comment_text": "This is a test comment"
            }
        )

        self.assertTrue(form.is_valid())


    def test_comment_text_required(self):

        form = CommentForm(
            data={
                "store_product_id": "1",
                "comment_id": "",
                "comment_text": ""
            }
        )

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors["comment_text"],
            ["این فیلد نمی تواند خالی باشد"]
        )


    def test_hidden_fields_exist(self):

        form = CommentForm()

        self.assertEqual(
            form.fields["store_product_id"].widget.__class__.__name__,
            "HiddenInput"
        )

        self.assertEqual(
            form.fields["comment_id"].widget.__class__.__name__,
            "HiddenInput"
        )


    def test_comment_text_widget(self):

        form = CommentForm()

        field = form.fields["comment_text"]

        self.assertEqual(
            field.widget.attrs["placeholder"],
            "متن نظر"
        )

        self.assertEqual(
            field.widget.attrs["rows"],
            "4"
        )

        self.assertEqual(
            field.widget.attrs["class"],
            "form-control"
        )