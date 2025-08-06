from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from users.models import Seller

class ProductCategories(models.Model):
    name=models.CharField(max_length=100,unique=True)
    sub_category=models.ForeignKey('self',on_delete=models.CASCADE,related_name='parent_category',null=True,blank=True)
    slug=models.SlugField(max_length=100,unique=True)
    @property
    def is_parent(self):
        return self.parent_category.exists()
    @property
    def is_child(self):
        return self.sub_category is not None
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super().save(*args,**kwargs)

    def get_descendants(self):
        ancestors = []
        child = self.sub_category
        while child:
            ancestors.append(child)
            child = child.child
        return reversed(ancestors)

    def get_ancestors(self):
        descendants = []
        for parent in self.parent_category.all():
            descendants.append(parent)
            descendants.extend(parent.get_descendants())
        return descendants

    def get_breadcrumbs(self):
        breadcrumbs = list(self.get_ancestors())
        breadcrumbs.append(self)
        return breadcrumbs

    class Meta:
        verbose_name_plural = 'Categories'

class Product(models.Model):
    p_id=models.AutoField(primary_key=True,unique=True)
    p_title=models.CharField(max_length = 35)
    p_description=models.TextField()
    p_price=models.DecimalField()
    p_posted=models.DateTimeField(auto_now_add=True)
    p_category=models.ForeignKey(ProductCategories,on_delete=models.CASCADE,related_name='products')
    p_seller=models.ForeignKey( Seller ,on_delete=models.CASCADE,related_name='products')
    p_rating=models.DecimalField(max_digits=1,decimal_places=0)
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