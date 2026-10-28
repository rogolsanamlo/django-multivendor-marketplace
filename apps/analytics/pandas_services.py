import pandas as pd

from apps.orders.models import OrderDetails


def sales_dataframe(store):

    queryset = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "price",
            "qty",
            "order__register_date",
            "store_product__product__product_name",
        )
    )

    df = pd.DataFrame(
        list(queryset)
    )

    if df.empty:
        return {
            "dataframe": df,
            "total_sales": 0,
            "average_sales": 0,
            "max_sale": 0,
            "min_sale": 0,
        }

    df["total_price"] = (
        df["price"] * df["qty"]
    )

    total_sales = df["total_price"].sum()
    average_sales = df["total_price"].mean()
    max_sale = df["total_price"].max()
    min_sale = df["total_price"].min()

    return {
        "dataframe": df,
        "total_sales": total_sales,
        "average_sales": average_sales,
        "max_sale": max_sale,
        "min_sale": min_sale,
    }


def sales_by_product(store):

    queryset = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "store_product__product__product_name",
            "price",
            "qty",
        )
    )

    df = pd.DataFrame(
        list(queryset)
    )

    if df.empty:
        return df

    df["total_price"] = (
        df["price"] * df["qty"]
    )

    result = (
        df
        .groupby(
            "store_product__product__product_name"
        )["total_price"]
        .sum()
        .reset_index()
        .sort_values(
            by="total_price",
            ascending=False,
        )
    )

    return result


def sales_pivot_table(store):

    queryset = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "store_product__product__product_name",
            "order__register_date",
            "price",
            "qty",
        )
    )

    df = pd.DataFrame(
        list(queryset)
    )

    if df.empty:
        return []

    df["total_price"] = (
        df["price"] * df["qty"]
    )

    df["month"] = pd.to_datetime(
        df["order__register_date"]
    ).dt.to_period("M")

    pivot = pd.pivot_table(
        df,
        index="store_product__product__product_name",
        columns="month",
        values="total_price",
        aggfunc="sum",
        fill_value=0,
    )

    pivot = pivot.reset_index()

    return pivot.to_dict(
        "records"
    )


def monthly_trend_dataframe(store):

    queryset = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "order__register_date",
            "price",
            "qty",
        )
    )

    df = pd.DataFrame(
        list(queryset)
    )

    if df.empty:
        return []

    df["total_price"] = (
        df["price"] * df["qty"]
    )

    df["month"] = pd.to_datetime(
        df["order__register_date"]
    ).dt.to_period("M")

    result = (
        df
        .groupby("month")["total_price"]
        .sum()
        .reset_index()
        .sort_values("month")
    )

    result["month"] = (
        result["month"].astype(str)
    )

    return result.to_dict(
        "records"
    )


def abc_analysis(store):

    queryset = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "store_product__product__product_name",
            "price",
            "qty",
        )
    )

    df = pd.DataFrame(
        list(queryset)
    )

    if df.empty:
        return []

    df["total_price"] = (
        df["price"] * df["qty"]
    )

    result = (
        df
        .groupby(
            "store_product__product__product_name"
        )["total_price"]
        .sum()
        .reset_index()
        .sort_values(
            by="total_price",
            ascending=False,
        )
    )

    total = result["total_price"].sum()

    if total == 0:
        return []

    result["percent"] = (
        result["total_price"] / total
    ) * 100

    result["cumulative"] = (
        result["percent"].cumsum()
    )

    def category(value):

        if value <= 80:
            return "A"

        elif value <= 95:
            return "B"

        return "C"

    result["class"] = (
        result["cumulative"].apply(category)
    )

    return result.to_dict(
        "records"
    )


def customer_segmentation(store):

    queryset = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "order__customer__user__name",
            "order__customer__user__family",
            "order_id",
            "price",
            "qty",
        )
    )

    df = pd.DataFrame(
        list(queryset)
    )

    if df.empty:
        return []

    df["total_price"] = (
        df["price"] * df["qty"]
    )

    result = (
        df
        .groupby(
            [
                "order__customer__user__name",
                "order__customer__user__family",
            ]
        )
        .agg(
            total_orders=(
                "order_id",
                "nunique",
            ),
            total_purchase=(
                "total_price",
                "sum",
            ),
            average_purchase=(
                "total_price",
                "mean",
            ),
        )
        .reset_index()
        .sort_values(
            by="total_purchase",
            ascending=False,
        )
    )

    result = result.rename(
        columns={
            "order__customer__user__name": "name",
            "order__customer__user__family": "family",
        }
    )

    return result.to_dict(
        "records"
    )


def weekday_sales_analysis(store):

    queryset = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "order__register_date",
            "price",
            "qty",
        )
    )

    df = pd.DataFrame(
        list(queryset)
    )

    if df.empty:
        return []

    df["total_price"] = (
        df["price"] * df["qty"]
    )

    df["weekday"] = pd.to_datetime(
        df["order__register_date"]
    ).dt.weekday

    week_days = {
        0: "دوشنبه",
        1: "سه‌شنبه",
        2: "چهارشنبه",
        3: "پنجشنبه",
        4: "جمعه",
        5: "شنبه",
        6: "یکشنبه",
    }

    df["weekday"] = (
        df["weekday"].map(week_days)
    )

    result = (
        df
        .groupby("weekday")["total_price"]
        .sum()
        .reset_index()
    )

    return result.to_dict(
        "records"
    )


def sales_growth_analysis(store):

    queryset = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "order__register_date",
            "price",
            "qty",
        )
    )

    df = pd.DataFrame(
        list(queryset)
    )

    if df.empty:
        return []

    df["total_price"] = (
        df["price"] * df["qty"]
    )

    df["month"] = pd.to_datetime(
        df["order__register_date"]
    ).dt.to_period("M")

    result = (
        df
        .groupby("month")["total_price"]
        .sum()
        .reset_index()
        .sort_values("month")
    )

    previous = result["total_price"].shift(1)

    result["growth_percent"] = 0.0

    valid = (
        previous.notna()
        & (previous != 0)
    )

    result.loc[valid, "growth_percent"] = (
        (
            result.loc[valid, "total_price"]
            - previous.loc[valid]
        )
        / previous.loc[valid]
        * 100
    )

    result["growth_percent"] = (
        result["growth_percent"].round(2)
    )

    result["month"] = (
        result["month"].astype(str)
    )

    return result.to_dict(
        "records"
    )


def sales_forecast(store):

    queryset = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "order__register_date",
            "price",
            "qty",
        )
    )

    df = pd.DataFrame(
        list(queryset)
    )

    if df.empty:
        return {
            "forecast": 0
        }

    df["total_price"] = (
        df["price"] * df["qty"]
    )

    daily = (
        df
        .groupby(
            "order__register_date"
        )["total_price"]
        .sum()
        .reset_index()
    )

    forecast = daily["total_price"].mean()

    return {
        "forecast": round(forecast)
    }