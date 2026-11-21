from decimal import Decimal
from django.db import transaction
from django.db.models import Q, F, Case, When, DecimalField, ExpressionWrapper
from django.db.models.lookups import GreaterThan
from core.models import Category, Product

# ---------- Sample data (reset on every run) ----------
Product.objects.all().delete()
Category.objects.all().delete()

elec = Category.objects.create(name="Electronics")
gadg = Category.objects.create(name="Gadgets")

def make(name, cat, price, maxp, stock, reorder, promo, status, country):
    return Product.objects.create(
        name=name, category=cat, price=Decimal(price),
        max_allowed_price=Decimal(maxp), stock_quantity=stock,
        reorder_level=reorder, is_promotional=promo,
        status=status, warehouse_country=country)

make("TV", elec, "25000", "30000", 5, 10, False, "NORMAL", "Japan")
make("Phone", elec, "8000", "10000", 50, 10, False, "NORMAL", "Thailand")
make("Headphones", gadg, "1000", "1100", 15, 10, True, "DISCOUNTED", "China")
make("Smartwatch", gadg, "2000", "3000", 25, 10, True, "DISCOUNTED", "Vietnam")
make("Charger", gadg, "500", "800", 8, 10, False, "NORMAL", "China")

# ---------- Challenge 1 ----------
print("\nCHALLENGE 1")
c1 = Product.objects.filter(
    (Q(category__name="Electronics") & Q(price__gt=10000))
    | (Q(status="DISCOUNTED") & ~Q(warehouse_country="China"))
)
print(list(c1))
print(c1.query)

# ---------- Challenge 2 ----------
print("\nCHALLENGE 2")
c2 = Product.objects.filter(
    Q(stock_quantity__lte=F("reorder_level"))
    | Q(is_promotional=True, stock_quantity__lt=F("reorder_level") * 2)
)
print(list(c2))
print(c2.query)

# ---------- Challenge 3 ----------
print("\nCHALLENGE 3")
money = DecimalField(max_digits=10, decimal_places=2)
new_price = ExpressionWrapper(F("price") * Decimal("1.15"), output_field=money)
rows = Product.objects.filter(category__name="Gadgets").update(
    price=Case(
        When(GreaterThan(new_price, F("max_allowed_price")),
             then=F("max_allowed_price")),
        default=new_price,
        output_field=money,
    )
)
print("Rows updated:", rows)
for p in Product.objects.filter(category__name="Gadgets"):
    print(p.name, p.price, "(max", p.max_allowed_price, ")")

# ---------- Challenge 4 ----------
print("\nCHALLENGE 4")

def purchase(product_id, qty):
    with transaction.atomic():
        updated = Product.objects.filter(
            pk=product_id, stock_quantity__gte=qty
        ).update(
            stock_quantity=F("stock_quantity") - qty,
            total_sold=F("total_sold") + qty,
            total_revenue=F("total_revenue") + F("price") * qty,
        )
    return updated == 1

hp = Product.objects.get(name="Headphones")
print("Buy 5:", purchase(hp.pk, 5))
print("Buy 100:", purchase(hp.pk, 100))
hp.refresh_from_db()
print(hp.stock_quantity, hp.total_sold, hp.total_revenue)