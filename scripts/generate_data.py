import random
from datetime import datetime, timedelta

# Sample data
PRODUCT_CATEGORIES = [
    "Electronics", "Clothing", "Books", "Home & Kitchen", "Toys", "Sports", "Beauty", "Food",
    "Automotive", "Garden", "Office", "Pet Supplies", "Music", "Art", "Health", "Tools"
]

PRODUCT_NAMES = {
    "Electronics": [
        "Smartphone", "Laptop", "Headphones", "Tablet", "Smart Watch", "Camera", "TV", "Speaker",
        "Gaming Console", "Wireless Earbuds", "Power Bank", "Monitor", "Keyboard", "Mouse", "Printer"
    ],
    "Clothing": [
        "T-Shirt", "Jeans", "Dress", "Jacket", "Sweater", "Socks", "Hat", "Shoes",
        "Hoodie", "Skirt", "Blazer", "Pants", "Shorts", "Coat", "Scarf", "Gloves"
    ],
    "Books": [
        "Fiction Novel", "Biography", "Cookbook", "Self-Help", "History Book", "Science Book",
        "Children's Book", "Poetry", "Mystery", "Fantasy", "Romance", "Business", "Technology",
        "Art Book", "Travel Guide", "Educational"
    ],
    "Home & Kitchen": [
        "Blender", "Coffee Maker", "Toaster", "Microwave", "Vacuum", "Cookware Set", "Knife Set",
        "Bedding", "Air Fryer", "Food Processor", "Stand Mixer", "Pressure Cooker", "Rice Cooker",
        "Dish Set", "Storage Containers", "Bakeware"
    ],
    "Toys": [
        "Action Figure", "Board Game", "Puzzle", "Stuffed Animal", "Building Blocks",
        "Remote Control Car", "Doll", "Educational Toy", "LEGO Set", "Art Kit", "Science Kit",
        "Musical Toy", "Outdoor Toy", "Baby Toy", "Card Game", "Robot"
    ],
    "Sports": [
        "Basketball", "Tennis Racket", "Yoga Mat", "Bicycle", "Weights", "Running Shoes",
        "Football", "Golf Clubs", "Soccer Ball", "Baseball Bat", "Skateboard", "Boxing Gloves",
        "Swimming Goggles", "Camping Tent", "Fishing Rod", "Exercise Bike"
    ],
    "Beauty": [
        "Shampoo", "Perfume", "Makeup Kit", "Face Cream", "Hair Dryer", "Nail Polish", "Razor",
        "Lotion", "Face Mask", "Hair Styling Tool", "Skincare Set", "Lipstick", "Eye Shadow",
        "Face Serum", "Body Wash", "Sunscreen"
    ],
    "Food": [
        "Chocolate", "Coffee", "Pasta", "Snacks", "Cereal", "Canned Goods", "Spices", "Beverages",
        "Tea", "Nuts", "Dried Fruits", "Olive Oil", "Honey", "Protein Bars", "Sauces", "Condiments"
    ],
    "Automotive": [
        "Car Battery", "Motor Oil", "Air Freshener", "Floor Mats", "Car Cover", "Tool Kit",
        "Jump Starter", "Tire Gauge", "Car Charger", "Seat Covers", "Windshield Wipers",
        "Car Wash Kit", "Air Filter", "Brake Pads", "Car Polish", "Emergency Kit"
    ],
    "Garden": [
        "Garden Tools", "Plant Pots", "Seeds", "Fertilizer", "Lawn Mower", "Garden Hose",
        "Pruning Shears", "Bird Feeder", "Outdoor Lights", "Watering Can", "Plant Food",
        "Garden Gloves", "Weed Killer", "Planter Box", "Garden Decor", "Insect Control"
    ],
    "Office": [
        "Desk Chair", "File Cabinet", "Desk Lamp", "Paper Shredder", "Stapler", "Printer Paper",
        "Notebooks", "Pens", "Calculator", "Desk Organizer", "Whiteboard", "Planner",
        "Sticky Notes", "Binder", "Paper Clips", "Desk Calendar"
    ],
    "Pet Supplies": [
        "Pet Food", "Pet Bed", "Pet Toys", "Pet Carrier", "Pet Grooming Kit", "Pet Bowl",
        "Pet Collar", "Pet Treats", "Pet Medicine", "Pet Shampoo", "Pet Brush", "Pet Gate",
        "Pet Clothes", "Pet House", "Pet Training Pads", "Pet Leash"
    ],
    "Music": [
        "Guitar", "Piano", "Drums", "Violin", "Microphone", "Music Stand", "Keyboard",
        "Amplifier", "Music Books", "Drum Sticks", "Guitar Strings", "Metronome",
        "Headphones", "Sheet Music", "Tuner", "Music Software"
    ],
    "Art": [
        "Paint Set", "Canvas", "Brushes", "Easel", "Sketch Pad", "Colored Pencils",
        "Art Paper", "Markers", "Craft Kit", "Sculpture Tools", "Art Storage", "Drawing Set",
        "Art Books", "Paint Palette", "Art Supplies Box", "Art Software"
    ],
    "Health": [
        "Vitamins", "First Aid Kit", "Blood Pressure Monitor", "Thermometer", "Pain Relief",
        "Bandages", "Cold Medicine", "Health Supplements", "Face Masks", "Hand Sanitizer",
        "Heating Pad", "Compression Socks", "Fitness Tracker", "Pill Organizer", "Eye Drops",
        "Dental Care"
    ],
    "Tools": [
        "Power Drill", "Screwdriver Set", "Hammer", "Wrench Set", "Tool Box", "Measuring Tape",
        "Level", "Saw", "Pliers", "Work Gloves", "Safety Glasses", "Tool Belt", "Drill Bits",
        "Utility Knife", "Ladder", "Work Light"
    ]
}

FIRST_NAMES = [
    "John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa", "William", "Emma",
    "James", "Olivia", "Daniel", "Sophia", "Joseph", "Isabella", "Thomas", "Mia", "Christopher", "Ava",
    "Andrew", "Charlotte", "Matthew", "Amelia", "Alexander", "Harper", "Ryan", "Evelyn", "Joshua", "Abigail",
    "Kevin", "Elizabeth", "Brian", "Sofia", "George", "Victoria", "Edward", "Camila", "Ronald", "Aria"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
    "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King",
    "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter"
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio",
    "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "San Francisco",
    "Charlotte", "Indianapolis", "Seattle", "Denver", "Boston", "Portland", "Miami", "Atlanta",
    "Las Vegas", "Minneapolis", "New Orleans", "Cleveland", "Orlando", "Sacramento", "Pittsburgh"
]

STATES = [
    "NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA", "TX", "FL", "TX", "OH", "CA",
    "NC", "IN", "WA", "CO", "MA", "OR", "FL", "GA", "NV", "MN", "LA", "OH", "FL", "CA", "PA"
]

STATUS_OPTIONS = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]

PRODUCT_DESCRIPTIONS = {
    "Electronics": "High-quality electronic device with advanced features and reliable performance.",
    "Clothing": "Stylish and comfortable clothing made from premium materials.",
    "Books": "Engaging and informative book that will expand your knowledge and imagination.",
    "Home & Kitchen": "Essential home appliance designed for convenience and efficiency.",
    "Toys": "Fun and educational toy that provides hours of entertainment.",
    "Sports": "Professional-grade sports equipment for optimal performance.",
    "Beauty": "Premium beauty product for your personal care routine.",
    "Food": "Delicious and nutritious food product made with quality ingredients.",
    "Automotive": "Reliable automotive product for your vehicle maintenance needs.",
    "Garden": "High-quality gardening product for your outdoor space.",
    "Office": "Professional office supply for improved productivity.",
    "Pet Supplies": "Quality pet product for your furry friend's well-being.",
    "Music": "Premium musical instrument or accessory for musicians of all levels.",
    "Art": "Professional art supply for creative expression.",
    "Health": "Trusted health product for your wellness needs.",
    "Tools": "Durable tool for professional and DIY projects."
}

def generate_price(category):
    """Generate a realistic price based on the product category"""
    price_ranges = {
        "Electronics": (50, 2000),
        "Clothing": (15, 200),
        "Books": (10, 50),
        "Home & Kitchen": (20, 500),
        "Toys": (10, 100),
        "Sports": (20, 300),
        "Beauty": (5, 100),
        "Food": (5, 50),
        "Automotive": (20, 300),
        "Garden": (15, 200),
        "Office": (10, 150),
        "Pet Supplies": (5, 100),
        "Music": (30, 1000),
        "Art": (10, 200),
        "Health": (10, 100),
        "Tools": (20, 300)
    }
    min_price, max_price = price_ranges.get(category, (10, 100))
    return round(random.uniform(min_price, max_price), 2)

def generate_stock_quantity(category):
    """Generate a realistic stock quantity based on the product category"""
    stock_ranges = {
        "Electronics": (5, 100),
        "Clothing": (20, 500),
        "Books": (10, 200),
        "Home & Kitchen": (10, 150),
        "Toys": (15, 300),
        "Sports": (10, 200),
        "Beauty": (20, 400),
        "Food": (30, 600),
        "Automotive": (10, 150),
        "Garden": (15, 200),
        "Office": (20, 400),
        "Pet Supplies": (20, 300),
        "Music": (5, 100),
        "Art": (15, 300),
        "Health": (20, 400),
        "Tools": (10, 200)
    }
    min_stock, max_stock = stock_ranges.get(category, (10, 200))
    return random.randint(min_stock, max_stock)

def generate_user_data(user_id):
    """Generate realistic user data"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    email = f"{first_name.lower()}.{last_name.lower()}{user_id}@example.com"
    phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    city_idx = random.randint(0, len(CITIES) - 1)
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar', 'Pine'])} {random.choice(['St', 'Ave', 'Rd', 'Blvd', 'Dr'])}",
        "city": CITIES[city_idx],
        "state": STATES[city_idx],
        "zip_code": f"{random.randint(10000, 99999)}",
        "created_at": datetime.now() - timedelta(days=random.randint(1, 1000)),
    }

def generate_order_data(user_id, products, order_date=None):
    """Generate realistic order data"""
    if order_date is None:
        order_date = datetime.now() - timedelta(days=random.randint(1, 365))
    
    num_items = random.randint(1, 5)
    order_items = []
    total_amount = 0
    
    # Select random products
    available_products = list(range(1, len(products) + 1))
    selected_products = random.sample(available_products, num_items)
    
    for product_id in selected_products:
        quantity = random.randint(1, 5)
        price = products[product_id - 1]["price"]
        item_total = price * quantity
        total_amount += item_total
        order_items.append({
            "product_id": product_id,
            "quantity": quantity,
            "price": price
        })
    
    return {
        "order_date": order_date,
        "total_amount": round(total_amount, 2),
        "status": random.choice(STATUS_OPTIONS),
        "items": order_items
    }