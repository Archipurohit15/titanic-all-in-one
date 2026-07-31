from django.core.management import BaseCommand
from products.models import Categories

CATEGORY_DATA = {
    "FMCG": {
        "commission":2,
        "items": [
            "Soap", "Hair Oil", "Perfume", "Face Wash", "Hand Wash", "Diaper",
            "Tooth Paste", "Hair Colour", "Medical Items", "Nutrition Items",
            "Shampoo", "Deodorant", "Body Lotion", "Body Wash", "Sanitary Pad",
            "Talcum Powder", "Tooth Brush", "Face Cream", "Agarbatti",
            "Fabric Items", "Shaving Items", "Detergent Powder", "Cleaning Items",
            "Cosmetics", "Face Serum", "Battery/Cell", "Blade", "Baby Care",
            "Room Freshener", "Liquid Detergent", "Gift Items", "Dish Wash Bar",
            "Dish Wash Liquid", "Coil", "All Out", "Scrubber",
        ],
    },
    "Groceries": {
        "commission":2,
        "items": [
            "Biscuits", "Noodles", "Namkeen", "Papad", "Coffee", "Jam", "Pasta",
            "Milk Product", "Chips", "Toffee", "Wafers", "Candy", "Beverages",
            "Corn Flakes", "Muesli", "Pickles", "Ketchup", "Honey", "Masale",
            "Oats", "Cereal", "Custard Powder", "Tea/Chai-Pati", "Mayonnaise",
            "Dry Fruit", "Besan/Salt", "Energy Drink", "Poha", "Juices",
            "Cookies", "Cold Drink", "Soup", "Chilli Sauces", "Flour", "Suji",
        ],
    },
    "Electronics": {
        "commission":3,
        "items": [
            "LED TV", "Air Conditioner", "Home Theatre", "Chimney", "Gas Stove",
            "Hand Blender", "Iron", "Sandwich & Grill Toaster", "Stabilizer",
            "Electric Kettle", "Personal Groomer", "Geyser", "Water RO",
            "Microwave Oven", "Mixer Grinder", "Juicer Mixer Grinder",
            "Air Fryer", "Cooler", "Refrigerator",
        ],
    },
    "Electrical": {
        "commission":3,
        "items": [
            "Exhaust Fan (PVC & Metal)", "Table Fan", "Ceiling Fan",
            "Monobloc Pump", "Jhoomar (Chandelier)", "Wall Light",
            "Gate Light", "Mirror Light", "POP Light",
        ],
    },
}



class Command(BaseCommand):
    help = "Loads Titanic's initial category + subcategory structure" 


    def handle(self, *args, **kwargs):

        for parent_name, data in CATEGORY_DATA.items():
            parent, created = Categories.objects.get_or_create(
                name=parent_name,
                parent=None,
                defaults={"commission_percent": data["commission"]},
            )
            status = "Created" if created else "Already exists"
            self.stdout.write(f"{status}: {parent_name}")


            for item_name in data["items"]:
                sub, sub_created = Categories.objects.get_or_create(
                    name=item_name,
                    parent=parent,
                    defaults={"commission_percent": data["commission"]},
                )
                if sub_created:
                    self.stdout.write(f"  + {item_name}")

            self.stdout.write(self.style.SUCCESS("Done loading categories."))