from django.core.management.base import BaseCommand
from products.models import Categories

CATEGORY_DATA = {
    "FMCG": {
        "commission": 6,
        "groups": {
            "Bath & Body": ["Soap", "Body Wash", "Body Lotion", "Talcum Powder", "Scrubber", "Deodorant", "Perfume"],
            "Hair Care": ["Shampoo", "Hair Oil", "Hair Colour"],
            "Oral Care": ["Tooth Paste", "Tooth Brush"],
            "Skin Care": ["Face Wash", "Face Cream", "Face Serum", "Cosmetics"],
            "Baby Care": ["Diaper", "Baby Care"],
            "Feminine Hygiene": ["Sanitary Pad"],
            "Health & Nutrition": ["Medical Items", "Nutrition Items"],
            "Shaving": ["Shaving Items", "Blade"],
            "Laundry Care": ["Detergent Powder", "Liquid Detergent", "Fabric Items"],
            "Home Cleaning": ["Hand Wash", "Cleaning Items", "Dish Wash Bar", "Dish Wash Liquid"],
            "Home Care": ["Coil", "All Out", "Room Freshener", "Agarbatti"],
            "Other": ["Battery/Cell", "Gift Items"],
        },
    },
    "Groceries": {
        "commission": 2,
        "groups": {
            "Snacks & Namkeen": ["Biscuits", "Namkeen", "Papad", "Chips", "Wafers", "Cookies"],
            "Sweets & Spreads": ["Toffee", "Candy", "Jam", "Honey"],
            "Breakfast & Cereals": ["Corn Flakes", "Muesli", "Oats", "Cereal", "Poha"],
            "Noodles, Pasta & Ready-to-Cook": ["Noodles", "Pasta", "Custard Powder", "Soup"],
            "Beverages": ["Coffee", "Tea/Chai-Pati", "Beverages", "Energy Drink", "Juices", "Cold Drink"],
            "Atta & Staples": ["Flour", "Suji", "Besan/Salt", "Dry Fruit"],
            "Sauces, Pickles & Masale": ["Pickles", "Ketchup", "Chilli Sauces", "Mayonnaise", "Masale"],
            "Dairy": ["Milk Product"],
        },
    },
    "Electronics": {
        "commission": 4,
        "groups": {
            "Large Appliances": ["LED TV", "Air Conditioner", "Refrigerator", "Cooler", "Geyser", "Water RO", "Home Theatre"],
            "Kitchen Appliances": ["Gas Stove", "Chimney", "Microwave Oven", "Mixer Grinder", "Juicer Mixer Grinder", "Hand Blender", "Sandwich & Grill Toaster", "Air Fryer"],
            "Personal Care & Others": ["Personal Groomer", "Iron", "Stabilizer"],
        },
    },
    "Electrical": {
        "commission": 5,
        "groups": {
            "Fans & Ventilation": ["Table Fan", "Ceiling Fan", "Exhaust Fan (PVC & Metal)"],
            "Pumps": ["Monobloc Pump"],
            "Lighting": ["Jhoomar (Chandelier)", "Wall Light", "Gate Light", "Mirror Light", "POP Light"],
        },
    },
}


class Command(BaseCommand):
    help = "Loads Titanic's 3-level category structure: Department > Group > Item"

    def handle(self, *args, **kwargs):
        for dept_name, dept_data in CATEGORY_DATA.items():
            dept, _ = Categories.objects.get_or_create(
                name=dept_name,
                parent=None,
                defaults={"commission_percent": dept_data["commission"]},
            )
            self.stdout.write(f"Department: {dept_name}")

            for group_name, items in dept_data["groups"].items():
                group, _ = Categories.objects.get_or_create(
                    name=group_name,
                    parent=dept,
                    defaults={"commission_percent": dept_data["commission"]},
                )
                self.stdout.write(f"  Group: {group_name}")

                for item_name in items:
                    item, item_created = Categories.objects.get_or_create(
                        name=item_name,
                        parent=group,
                        defaults={"commission_percent": dept_data["commission"]},
                    )
                    if item_created:
                        self.stdout.write(f"    + {item_name}")

        self.stdout.write(self.style.SUCCESS("Done loading 3-level categories."))