// Bazarak front-end helpers.
// Endpoint URLs come from window.BAZARAK_URLS (see templates/partials/scripts.html),
// so they always match urls.py.

$(document).ready(function () {
    var urlParams = new URLSearchParams(window.location.search);

    if (urlParams.toString() === "") {
        localStorage.clear();
        $("#filter_state").css("display", "none");
    } else {
        $("#filter_state").css("display", "inline-block");
    }

    $('input:checkbox').on('click', function () {
        var favs = [];

        $('input:checkbox').each(function () {
            favs.push({ id: $(this).attr('id'), value: $(this).prop('checked') });
        });

        localStorage.setItem("filter_checkboxes", JSON.stringify(favs));
    });

    var saved = JSON.parse(localStorage.getItem("filter_checkboxes") || "[]");

    for (var i = 0; i < saved.length; i++) {
        if (saved[i].id) {
            $('#' + saved[i].id).prop('checked', saved[i].value);
        }
    }

    status_of_shop_cart();
});

function ajaxErrorMessage(xhr) {
    if (xhr.status === 401) {
        return "برای انجام این کار ابتدا وارد حساب کاربری خود شوید";
    }

    return xhr.responseText || "خطایی رخ داد";
}

// ---------------------------------------------------------------- filters

function showVal(x) {
    x = x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    document.getElementById('sel_price').innerText = x;
}

function removeURLParameter(url, parameter) {
    var urlparts = url.split("?");

    if (urlparts.length >= 2) {
        var prefix = encodeURIComponent(parameter) + "=";
        var pars = urlparts[1].split(/[&;]/g);

        for (var i = pars.length; i-- > 0;) {
            if (pars[i].lastIndexOf(prefix, 0) !== -1) {
                pars.splice(i, 1);
            }
        }

        return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
    }

    return url;
}

function select_sort() {
    var value = $("#select_sort").val();
    var url = removeURLParameter(window.location.href, "sort_type");
    var separator = url.includes("?") ? "&" : "?";

    window.location = url + separator + "sort_type=" + value;
}

function update_product_numbers() {
    var value = $('#product_numbers').val();
    var url = removeURLParameter(window.location.href, "product_numbers");
    var separator = url.includes('?') ? '&' : '?';

    window.location.href = url + separator + "product_numbers=" + value;
}

// -------------------------------------------------------------- shop cart

function status_of_shop_cart() {
    if (!$("#indicator__value").length) {
        return;
    }

    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.statusOfShopCart,
        success: function (res) {
            $("#indicator__value").text(res);
        }
    });
}

function add_to_shop_cart(storeProductId, quantity) {
    quantity = parseInt(quantity, 10);

    if (!quantity) {
        quantity = parseInt($("#product-qty").val(), 10) || 1;
    }

    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.addToShopCart,
        data: {
            product_id: storeProductId,
            qty: quantity
        },
        success: function () {
            alert("کالای مورد نظر به سبد خرید شما اضافه شد");
            status_of_shop_cart();
        },
        error: function (xhr) {
            alert(ajaxErrorMessage(xhr));
        }
    });
}

function delete_from_shop_cart(storeProductId) {
    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.deleteFromShopCart,
        data: { product_id: storeProductId },
        success: function (res) {
            alert("کالای مورد نظر از سبد شما حذف شد");
            $("#shop_cart_list").html(res);
            status_of_shop_cart();
        }
    });
}

function update_shop_cart() {
    var product_id_list = [];
    var qty_list = [];

    $("input[id^='qty_']").each(function () {
        product_id_list.push($(this).attr('id').slice(4));
        qty_list.push($(this).val());
    });

    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.updateShopCart,
        data: {
            product_id_list: product_id_list,
            qty_list: qty_list
        },
        success: function (res) {
            alert("تعداد کالاها بروزرسانی شد");
            $("#shop_cart_list").html(res);
            status_of_shop_cart();
        }
    });
}

// ---------------------------------------------------------------- comments

function showCreateCommentForm(storeProductId, commentId, slug) {
    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.createComment.replace("SLUG", slug),
        data: {
            storeProductId: storeProductId,
            commentId: commentId
        },
        success: function (res) {
            $("#btn_" + commentId).hide();

            $("#comment_form_" + commentId).html(
                '<div style="position: relative;">' +
                '<button type="button" onclick="hideCommentForm(' + commentId + ')" class="close-button">×</button>' +
                res +
                '</div>'
            );
        },
        error: function (xhr) {
            alert(ajaxErrorMessage(xhr));
        }
    });
}

function hideCommentForm(commentId) {
    $("#comment_form_" + commentId).empty();
    $("#btn_" + commentId).show();
}

// ------------------------------------------------------------------ scores

function addScore(score, storeProductId) {
    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.addScore,
        data: {
            storeProductId: storeProductId,
            score: score
        },
        dataType: "json",
        success: function (res) {
            $(".fa-star").removeClass("checked");

            for (var i = 1; i <= score; i++) {
                $("#star_" + i).addClass("checked");
            }

            $("#average-score").text(res.average);
            alert(res.message);
        },
        error: function (xhr) {
            alert(ajaxErrorMessage(xhr));
        }
    });
}

function star_score_percent(productId, avgScore) {
    var percent = (avgScore / 5) * 100;
    var star = document.getElementById("star_fill_" + productId);

    if (star) {
        star.style.width = percent + "%";
    }
}

// --------------------------------------------------------------- favorites

function addTofavorites(storeProductId) {
    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.addToFavorite,
        data: { storeProductId: storeProductId },
        success: function (res) {
            alert(res);
            $("#favorite-btn-" + storeProductId + " i")
                .removeClass("far")
                .addClass("fas fa-heart");
        },
        error: function (xhr) {
            alert(ajaxErrorMessage(xhr));
        }
    });
}


function delete_from_favorite(storeProductId) {
    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.deleteFromFavorite,
        data: { storeProductId: storeProductId },
        success: function (res) {
            alert(res);
            location.reload();
        },
        error: function (xhr) {
            alert(ajaxErrorMessage(xhr));
        }
    });
}

// ----------------------------------------------------------------- compare

function addToCompareList(storeProductId) {
    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.addToCompare,
        data: { storeProductId: storeProductId },
        success: function (res) {
            alert(res);
        },
        error: function (xhr) {
            alert(ajaxErrorMessage(xhr));
        }
    });
}

function deleteFromCompareList(storeProductId) {
    $.ajax({
        type: "GET",
        url: BAZARAK_URLS.deleteFromCompare,
        data: { storeProductId: storeProductId },
        success: function (res) {
            alert("حذف با موفقیت انجام شد");
            $("#compare_list").html(res);
        }
    });
}
