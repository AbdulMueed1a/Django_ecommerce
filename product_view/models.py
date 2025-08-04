from django.db import models
from django.utils import timezone
from django.conf import settings
from users.models import Seller

class Product(models.Model):
    PRODUCT_CATEGORIES = [
        # Electronics & Technology
        ('smartphones', 'Smartphones'),
        ('laptops', 'Laptops'),
        ('tablets', 'Tablets'),
        ('desktop_computers', 'Desktop Computers'),
        ('gaming_consoles', 'Gaming Consoles'),
        ('headphones', 'Headphones & Earphones'),
        ('speakers', 'Speakers'),
        ('cameras', 'Cameras'),
        ('smart_watches', 'Smart Watches'),
        ('televisions', 'Televisions'),
        ('home_appliances', 'Home Appliances'),
        ('kitchen_appliances', 'Kitchen Appliances'),
        ('computer_accessories', 'Computer Accessories'),
        ('mobile_accessories', 'Mobile Accessories'),
        ('gaming_accessories', 'Gaming Accessories'),
        ('audio_equipment', 'Audio Equipment'),
        ('video_equipment', 'Video Equipment'),
        ('smart_home', 'Smart Home Devices'),
        ('wearable_tech', 'Wearable Technology'),
        ('drones', 'Drones & Quadcopters'),

        # Fashion & Apparel
        ('mens_clothing', 'Men\'s Clothing'),
        ('womens_clothing', 'Women\'s Clothing'),
        ('kids_clothing', 'Kids\' Clothing'),
        ('shoes', 'Shoes'),
        ('bags', 'Bags & Luggage'),
        ('accessories', 'Fashion Accessories'),
        ('jewelry', 'Jewelry'),
        ('watches', 'Watches'),
        ('sunglasses', 'Sunglasses'),
        ('hats', 'Hats & Caps'),
        ('belts', 'Belts'),
        ('scarves', 'Scarves'),
        ('underwear', 'Underwear & Lingerie'),
        ('activewear', 'Activewear'),
        ('formal_wear', 'Formal Wear'),
        ('casual_wear', 'Casual Wear'),
        ('ethnic_wear', 'Ethnic Wear'),

        # Health & Beauty
        ('skincare', 'Skincare'),
        ('makeup', 'Makeup & Cosmetics'),
        ('haircare', 'Hair Care'),
        ('fragrances', 'Fragrances'),
        ('personal_care', 'Personal Care'),
        ('health_supplements', 'Health Supplements'),
        ('fitness_equipment', 'Fitness Equipment'),
        ('medical_devices', 'Medical Devices'),
        ('wellness', 'Wellness Products'),
        ('oral_care', 'Oral Care'),
        ('mens_grooming', 'Men\'s Grooming'),
        ('womens_care', 'Women\'s Care'),

        # Home & Garden
        ('furniture', 'Furniture'),
        ('home_decor', 'Home Decor'),
        ('bedding', 'Bedding & Bath'),
        ('lighting', 'Lighting'),
        ('storage', 'Storage & Organization'),
        ('cleaning_supplies', 'Cleaning Supplies'),
        ('tools', 'Tools & Hardware'),
        ('garden_supplies', 'Garden & Outdoor'),
        ('kitchenware', 'Kitchenware'),
        ('dining', 'Dining & Tableware'),
        ('bathroom_accessories', 'Bathroom Accessories'),
        ('wall_art', 'Wall Art & Decor'),
        ('rugs_carpets', 'Rugs & Carpets'),
        ('curtains_blinds', 'Curtains & Blinds'),
        ('plants', 'Plants & Planters'),

        # Sports & Outdoors
        ('sports_equipment', 'Sports Equipment'),
        ('outdoor_gear', 'Outdoor Gear'),
        ('camping', 'Camping & Hiking'),
        ('cycling', 'Cycling'),
        ('water_sports', 'Water Sports'),
        ('winter_sports', 'Winter Sports'),
        ('team_sports', 'Team Sports'),
        ('individual_sports', 'Individual Sports'),
        ('fishing', 'Fishing'),
        ('hunting', 'Hunting'),
        ('outdoor_clothing', 'Outdoor Clothing'),
        ('sports_shoes', 'Sports Shoes'),
        ('gym_equipment', 'Gym Equipment'),

        # Books & Media
        ('books', 'Books'),
        ('ebooks', 'E-books'),
        ('audiobooks', 'Audiobooks'),
        ('magazines', 'Magazines'),
        ('movies_tv', 'Movies & TV Shows'),
        ('music', 'Music'),
        ('video_games', 'Video Games'),
        ('board_games', 'Board Games'),
        ('educational_materials', 'Educational Materials'),
        ('stationery', 'Stationery'),

        # Food & Beverages
        ('groceries', 'Groceries'),
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks'),
        ('organic_food', 'Organic Food'),
        ('specialty_food', 'Specialty Food'),
        ('frozen_food', 'Frozen Food'),
        ('dairy_products', 'Dairy Products'),
        ('meat_seafood', 'Meat & Seafood'),
        ('fruits_vegetables', 'Fruits & Vegetables'),
        ('bakery', 'Bakery Items'),
        ('condiments', 'Condiments & Sauces'),
        ('international_food', 'International Food'),

        # Baby & Kids
        ('baby_care', 'Baby Care'),
        ('baby_clothing', 'Baby Clothing'),
        ('toys', 'Toys'),
        ('kids_books', 'Kids\' Books'),
        ('baby_gear', 'Baby Gear'),
        ('feeding', 'Baby Feeding'),
        ('diapering', 'Diapering'),
        ('nursery', 'Nursery Furniture'),
        ('educational_toys', 'Educational Toys'),
        ('outdoor_toys', 'Outdoor Toys'),
        ('stuffed_animals', 'Stuffed Animals'),

        # Automotive
        ('car_accessories', 'Car Accessories'),
        ('car_parts', 'Car Parts'),
        ('motorcycle_accessories', 'Motorcycle Accessories'),
        ('tires', 'Tires'),
        ('car_care', 'Car Care Products'),
        ('tools_automotive', 'Automotive Tools'),
        ('electronics_automotive', 'Automotive Electronics'),

        # Pet Supplies
        ('pet_food', 'Pet Food'),
        ('pet_toys', 'Pet Toys'),
        ('pet_accessories', 'Pet Accessories'),
        ('pet_care', 'Pet Care'),
        ('pet_clothing', 'Pet Clothing'),
        ('aquarium_supplies', 'Aquarium Supplies'),
        ('bird_supplies', 'Bird Supplies'),
        ('reptile_supplies', 'Reptile Supplies'),

        # Office & Business
        ('office_supplies', 'Office Supplies'),
        ('office_furniture', 'Office Furniture'),
        ('printers_scanners', 'Printers & Scanners'),
        ('business_equipment', 'Business Equipment'),
        ('presentation_supplies', 'Presentation Supplies'),
        ('filing_storage', 'Filing & Storage'),

        # Arts & Crafts
        ('art_supplies', 'Art Supplies'),
        ('craft_materials', 'Craft Materials'),
        ('sewing_supplies', 'Sewing Supplies'),
        ('painting_supplies', 'Painting Supplies'),
        ('drawing_supplies', 'Drawing Supplies'),
        ('scrapbooking', 'Scrapbooking'),
        ('knitting_crochet', 'Knitting & Crochet'),

        # Musical Instruments
        ('guitars', 'Guitars'),
        ('keyboards_pianos', 'Keyboards & Pianos'),
        ('drums', 'Drums'),
        ('wind_instruments', 'Wind Instruments'),
        ('string_instruments', 'String Instruments'),
        ('music_accessories', 'Music Accessories'),
        ('recording_equipment', 'Recording Equipment'),

        # Industrial & Scientific
        ('industrial_supplies', 'Industrial Supplies'),
        ('scientific_equipment', 'Scientific Equipment'),
        ('safety_equipment', 'Safety Equipment'),
        ('laboratory_supplies', 'Laboratory Supplies'),
        ('measuring_tools', 'Measuring Tools'),

        # Gift Cards & Services
        ('gift_cards', 'Gift Cards'),
        ('digital_services', 'Digital Services'),
        ('subscriptions', 'Subscriptions'),
        ('experiences', 'Experiences'),
        ('warranties', 'Warranties & Protection Plans'),

        # Miscellaneous
        ('collectibles', 'Collectibles'),
        ('antiques', 'Antiques'),
        ('handmade', 'Handmade Items'),
        ('vintage', 'Vintage Items'),
        ('party_supplies', 'Party Supplies'),
        ('seasonal', 'Seasonal Items'),
        ('religious_items', 'Religious Items'),
        ('travel_accessories', 'Travel Accessories'),
        ('novelty_items', 'Novelty Items'),
        ('other', 'Other'),
    ]
    p_id=models.AutoField(primary_key=True,unique=True)
    p_title=models.CharField(max_length = 35)
    p_description=models.TextField()
    p_price=models.FloatField()
    p_posted=models.DateTimeField(auto_now_add=True)
    p_category=models.CharField(max_length=100,choices=PRODUCT_CATEGORIES)
    p_seller=models.ForeignKey( Seller ,on_delete=models.CASCADE,related_name='products')
    p_rating=models.FloatField(max_length=5)
    p_updated=models.DateField(auto_now=True)
    p_stock=models.IntegerField()
    p_sold=models.IntegerField()

class ProductImage(models.Model):
    image_id=models.AutoField(primary_key=True)
    image_product=models.ForeignKey( Product ,on_delete=models.CASCADE,related_name='images')
    image_pic=models.ImageField(upload_to='Images/')

class ProductReviews(models.Model):
    review_id=models.BigAutoField(primary_key=True)
    review_user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='reviews')
    review_product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_reviews')
    review_rating=models.IntegerField()
    review_desc=models.TextField()
    review_postedat=models.DateField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['review_user','review_product'],name='One review per product Allowed to any User')]

class ReviewImage(models.Model):
    review_image_id=models.BigAutoField(primary_key=True)
    image_review=models.ForeignKey(ProductReviews , on_delete = models.CASCADE,related_name='reviewImage')
    image_pic=models.ImageField(upload_to='ReviewImages/')

class ProductQuestion(models.Model):
    STATUS_CHOICES=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('spam', 'Marked as Spam'),
    ]
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='questions')
    question=models.TextField()
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.DO_NOTHING,related_name='questions_asked')
    datetime=models.DateTimeField(auto_now_add=True)
    approved_status=models.CharField(choices=STATUS_CHOICES,default='pending')
    status_updated_at=models.DateTimeField(null=True,blank=True)
    status_updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete = models.CASCADE,related_name='approver',null=True,blank=True)
    def save(self,*args,**kwargs):
        if not self.approved_status=='pending':
            self.status_updated_at=timezone.now()


class ProductAnswers(models.Model):
    question=models.OneToOneField(ProductQuestion,on_delete=models.CASCADE,related_name='answer')
    answer = models.TextField()
    seller = models.ForeignKey(Seller, on_delete=models.DO_NOTHING, related_name='questions_answered')
    datetime=models.DateTimeField(auto_now_add=True)
    @property
    def response_time(self):
        return self.datetime - self.question.status_updated_at